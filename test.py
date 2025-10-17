# python
import time
import argparse
import cv2
from pyzbar.pyzbar import decode
import sys
import os
import csv
from datetime import datetime

class DummyOutputDevice:
    def __init__(self, pin, active_high=True, initial_value=True):
        self.pin = pin
        self.active_high = active_high
        self.value = initial_value
        print(f"[DummyLock] init pin={pin} active_high={active_high} initial={initial_value}")

    def off(self):
        self.value = False
        print("[DummyLock] off (ouvrir)")

    def on(self):
        self.value = True
        print("[DummyLock] on (refermer)")

def get_lock(pin, simulate=False):
    # explicit simulation or non-Linux platforms -> dummy
    if simulate:
        return DummyOutputDevice(pin, active_high=False, initial_value=True)

    # quick platform check: only try real GPIO on Linux with /proc/cpuinfo (Raspberry Pi)
    if not sys.platform.startswith("linux") or not os.path.exists("/proc/cpuinfo"):
        print("GPIO non disponible sur cette plateforme — utilisation du DummyOutputDevice.")
        return DummyOutputDevice(pin, active_high=False, initial_value=True)

    # try importing/creating the real OutputDevice; fallback to dummy on error
    try:
        from gpiozero import OutputDevice  # type: ignore
        return OutputDevice(pin, active_high=False, initial_value=True)
    except Exception as e:
        print("Impossible d'initialiser gpiozero, fallback vers DummyOutputDevice:", e)
        return DummyOutputDevice(pin, active_high=False, initial_value=True)

# CSV helpers
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMPRUNTS_CSV = os.path.join(BASE_DIR, "emprunts.csv")
CASIERS_CSV = os.path.join(BASE_DIR, "casiers.csv")

def read_casiers():
    casiers = []
    if not os.path.exists(CASIERS_CSV):
        print("Fichier casiers.csv introuvable:", CASIERS_CSV)
        return casiers
    with open(CASIERS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # normalize statut to bool
            statut = str(row.get("statut", "")).strip().lower() in ("true", "1", "yes")
            try:
                idc = int(str(row.get("id_casier", "")).strip())
            except Exception:
                continue
            casiers.append({"id_casier": idc, "statut": statut})
    return casiers

def write_casiers(casiers):
    with open(CASIERS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_casier", "statut"])
        for c in casiers:
            writer.writerow([c["id_casier"], "True" if c["statut"] else "False"])
    print("Mise à jour de casiers.csv")

def read_emprunts():
    emprunts = []
    if not os.path.exists(EMPRUNTS_CSV):
        return emprunts
    with open(EMPRUNTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                id_e = int(str(row.get("id_emprunt", "")).strip()) if row.get("id_emprunt") else None
                id_c = int(str(row.get("id_casier", "")).strip()) if row.get("id_casier") else None
            except Exception:
                continue
            emprunts.append({
                "id_emprunt": id_e,
                "mail": (row.get("mail") or "").strip(),
                "id_casier": id_c,
                "date": (row.get("date") or "").strip(),
                "heure": (row.get("heure") or "").strip(),
                "statut": (row.get("statut") or "").strip().upper() if row.get("statut") else ""
            })
    return emprunts

def write_emprunts(emprunts):
    with open(EMPRUNTS_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id_emprunt", "mail", "id_casier", "date", "heure", "statut"])
        for e in emprunts:
            writer.writerow([
                e.get("id_emprunt") or "",
                e.get("mail") or "",
                e.get("id_casier") or "",
                e.get("date") or "",
                e.get("heure") or "",
                e.get("statut") or ""
            ])
    print("Mise à jour emprunts.csv")

def append_emprunt(mail, id_casier, statut="EN_COURS"):
    # ensure file exists and header present
    emprunts = read_emprunts()
    next_id = 1
    ids = [e["id_emprunt"] for e in emprunts if e.get("id_emprunt")]
    if ids:
        next_id = max(ids) + 1

    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")

    new = {
        "id_emprunt": next_id,
        "mail": mail,
        "id_casier": id_casier,
        "date": date_str,
        "heure": time_str,
        "statut": statut
    }
    emprunts.append(new)
    write_emprunts(emprunts)
    print(f"Ajout emprunt id={next_id} mail={mail} id_casier={id_casier} statut={statut} {date_str} {time_str}")
    return next_id

def set_emprunt_status(id_emprunt, new_status):
    emprunts = read_emprunts()
    updated = False
    for e in emprunts:
        if e.get("id_emprunt") == id_emprunt:
            e["statut"] = new_status
            updated = True
            break
    if updated:
        write_emprunts(emprunts)
        print(f"Emprunt id={id_emprunt} mis à jour statut={new_status}")
    else:
        print(f"Emprunt id={id_emprunt} non trouvé pour mise à jour.")

def decode_frame(frame):
    decoded = decode(frame)
    return [q.data.decode('utf-8') for q in decoded]

def handle_scan(mail, lock):
    """Gère un scan : si l'étudiant a un emprunt EN_COURS -> ferme l'emprunt (TERMINE) et marque le casier plein.
       Sinon -> crée un nouvel emprunt (EN_COURS) en ouvrant le premier casier plein disponible (statut True -> devient False)."""
    print(f"Scan reçu (mail) : {mail} — vérification des emprunts en cours...")
    emprunts = read_emprunts()
    # find latest EN_COURS for this mail (by id_emprunt)
    en_cours = [e for e in emprunts if e.get("mail") == mail and e.get("statut") == "EN_COURS"]
    if en_cours:
        # pick the latest (max id)
        emp = max(en_cours, key=lambda x: x.get("id_emprunt") or 0)
        idc = emp.get("id_casier")
        print(f"Emprunt en cours trouvé id_emprunt={emp.get('id_emprunt')} casier={idc} -> fermeture de l'emprunt (TERMINÉ) et marquage du casier comme PLEIN.")
        # open the casier
        lock.off()
        time.sleep(2)
        lock.on()
        # update emprunt statut -> TERMINE
        set_emprunt_status(emp.get("id_emprunt"), "TERMINE")
        # update casiers: mark casier as True (full)
        casiers = read_casiers()
        for c in casiers:
            if c["id_casier"] == idc:
                c["statut"] = True
                break
        write_casiers(casiers)
        print("Retour traité.")
        return

    # no current emprunt -> create new emprunt (borrow)
    print("Aucun emprunt en cours — recherche d'un casier plein (statut True) à ouvrir pour emprunt...")
    casiers = read_casiers()
    if not casiers:
        print("Aucun casier configuré.")
        return

    target = None
    for c in casiers:
        if c["statut"]:
            target = c
            break

    if not target:
        print("Aucun casier disponible pour emprunt (aucun statut True).")
        return

    idc = target["id_casier"]
    print(f"Ouverture du casier id={idc} pour nouvel emprunt de {mail}.")
    lock.off()
    time.sleep(2)
    lock.on()
    # mark casier now empty (False)
    for c in casiers:
        if c["id_casier"] == idc:
            c["statut"] = False
            break
    write_casiers(casiers)
    append_emprunt(mail, idc, statut="EN_COURS")
    print("Emprunt créé.")

def try_open_for_mail(mail, lock):
    # kept for compatibility but delegate to handle_scan
    handle_scan(mail, lock)

def main():
    parser = argparse.ArgumentParser(description="Test QR lock (simulate on macOS)")
    parser.add_argument("--simulate", action="store_true", help="Use dummy GPIO (no hardware)")
    parser.add_argument("--image", type=str, help="Decode single image file and exit")
    parser.add_argument("--video", type=str, help="Use video file instead of webcam")
    parser.add_argument("--pin", type=int, default=17, help="GPIO pin for lock (simulated by default on mac)")
    parser.add_argument("--code", type=str, default=None, help="Optional exact QR payload to accept (if set, other payloads ignored)")
    args = parser.parse_args()

    lock = get_lock(args.pin, simulate=args.simulate)

    # Single image mode
    if args.image:
        img = cv2.imread(args.image)
        if img is None:
            print("Erreur: impossible de lire l'image:", args.image)
            return
        found = decode_frame(img)
        print("Decoded:", found)
        for data in found:
            # treat QR payload that looks like an email as mail
            if args.code and data != args.code:
                print("QR ignoré (ne correspond pas à --code).")
                continue
            if "@" in data:
                handle_scan(data, lock)
            else:
                print("Payload non reconnu (attendu mail). Contenu:", data)
        return

    # Video/webcam mode
    src = args.video if args.video else 0
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        print("Erreur: impossible d'ouvrir la source vidéo:", src)
        print("Si vous êtes en simulation sans webcam, lancez avec --simulate --image <fichier> ou utilisez --simulate et entrez QR via stdin.")
        # fallback: allow stdin simulation
        if args.simulate:
            print("Mode stdin: tapez le mail contenu dans le QR puis ENTER pour simuler.")
            try:
                while True:
                    s = input().strip()
                    if not s:
                        continue
                    print("Simulé QR:", s)
                    if args.code and s != args.code:
                        print("Ignoré (ne correspond pas --code).")
                        continue
                    if "@" in s:
                        handle_scan(s, lock)
                    else:
                        print("Payload non reconnu (attendu mail).")
            except KeyboardInterrupt:
                print("Terminé.")
        return

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            decoded = decode_frame(frame)
            for data in decoded:
                print("QR:", data)
                if args.code and data != args.code:
                    print("Ignoré (ne correspond pas --code).")
                    continue
                if "@" in data:
                    handle_scan(data, lock)
                else:
                    print("Payload non reconnu (attendu mail).")
            # Ajout pour afficher la vidéo
            cv2.imshow("Camera", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.1)
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()