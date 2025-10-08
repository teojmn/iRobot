import os
import csv
import time
import smtplib
import argparse
from datetime import datetime, date, timedelta
from email.mime.text import MIMEText

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EMPRUNTS_CSV = os.path.join(BASE_DIR, "emprunts.csv")

# try to reuse SMTP config from smtp_test.py if present
try:
    import smtp_test as smtp_conf  # type: ignore
    SMTP_SERVER = getattr(smtp_conf, "SMTP_SERVER", None)
    SMTP_PORT = getattr(smtp_conf, "SMTP_PORT", None)
    SMTP_USER = getattr(smtp_conf, "SMTP_USER", None)
    SMTP_PASS = getattr(smtp_conf, "SMTP_PASS", None)
    FROM_EMAIL = getattr(smtp_conf, "FROM_EMAIL", None)
except Exception:
    SMTP_SERVER = os.environ.get("SMTP_SERVER")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
    SMTP_USER = os.environ.get("SMTP_USER")
    SMTP_PASS = os.environ.get("SMTP_PASS")
    FROM_EMAIL = os.environ.get("FROM_EMAIL")

SUBJECT = "Rappel : merci de rendre le câble HDMI"
BODY_TEMPLATE = (
    "Bonjour,\n\n"
    "Notre suivi indique que vous avez emprunté un câble HDMI et ne l'avez pas rendu.\n"
    "Merci de le rendre dès que possible.\n\n"
    "Cordialement,\n"
    "Service Borne HDMI"
)

def read_emprunts():
    emprunts = []
    if not os.path.exists(EMPRUNTS_CSV):
        return emprunts
    with open(EMPRUNTS_CSV, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            emprunts.append({
                "id_emprunt": int(row.get("id_emprunt") or 0),
                "mail": (row.get("mail") or "").strip(),
                "id_casier": row.get("id_casier"),
                "date": (row.get("date") or "").strip(),
                "heure": (row.get("heure") or "").strip(),
                "statut": (row.get("statut") or "").strip().upper()
            })
    return emprunts

def send_email(to_email, subject, body):
    if not (SMTP_SERVER and SMTP_PORT and FROM_EMAIL):
        print("SMTP non configuré (SMTP_SERVER/SMTP_PORT/FROM_EMAIL manquants). Email non envoyé.")
        return False
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30) as server:
            server.starttls()
            if SMTP_USER and SMTP_PASS:
                server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(FROM_EMAIL, [to_email], msg.as_string())
        print(f"Email envoyé à {to_email}")
        return True
    except Exception as e:
        print(f"Erreur envoi email à {to_email} :", e)
        return False

def find_overdue_emprunts_for_yesterday():
    emprunts = read_emprunts()
    yesterday = date.today() - timedelta(days=1)
    overdue = []
    for e in emprunts:
        if e["statut"] != "EN_COURS":
            continue
        # parse date in CSV (format YYYY-MM-DD)
        try:
            d = datetime.strptime(e["date"], "%Y-%m-%d").date()
        except Exception:
            continue
        if d == yesterday:
            overdue.append(e)
    return overdue

def test_mode_overdue():
    # for testing: consider all EN_COURS as overdue after 30s (send to all EN_COURS)
    emprunts = read_emprunts()
    overdue = [e for e in emprunts if e["statut"] == "EN_COURS"]
    if not overdue:
        print("Aucun emprunt EN_COURS trouvé (test mode).")
        return
    print(f"Mode TEST: envoi de rappel dans 30 secondes pour {len(overdue)} emprunt(s).")
    time.sleep(30)
    for e in overdue:
        if e["mail"]:
            print(f"Envoi test rappel à {e['mail']} (id_emprunt={e['id_emprunt']})")
            send_email(e["mail"], SUBJECT, BODY_TEMPLATE)
        else:
            print(f"Emprunt id={e['id_emprunt']} sans mail, skip.")

def run_once():
    overdue = find_overdue_emprunts_for_yesterday()
    if not overdue:
        print("Aucun emprunt à relancer (aucun EN_COURS pour la date d'hier).")
        return
    print(f"Envoi de {len(overdue)} rappel(s) pour les emprunts d'hier.")
    for e in overdue:
        if e["mail"]:
            send_email(e["mail"], SUBJECT, BODY_TEMPLATE)
        else:
            print(f"Emprunt id={e['id_emprunt']} sans mail, skip.")

def seconds_until_next_0830():
    now = datetime.now()
    target = now.replace(hour=8, minute=30, second=0, microsecond=0)
    if target <= now:
        target = target + timedelta(days=1)
    return (target - now).total_seconds()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Test mode: wait 30s then send reminders to all EN_COURS")
    parser.add_argument("--once", action="store_true", help="Run one immediate check (yesterday logic)")
    args = parser.parse_args()

    print("Reminder service démarré. SMTP server:", SMTP_SERVER or "(non configuré)")
    if args.test:
        test_mode_overdue()
        return

    if args.once:
        run_once()
        return

    # production loop: wake up at 08:30 every day
    try:
        while True:
            secs = seconds_until_next_0830()
            print(f"En veille jusqu'à 08:30 (sec restant: {int(secs)}).")
            time.sleep(secs)
            print("Heure 08:30 atteinte — vérification des emprunts d'hier.")
            run_once()
            # small sleep to avoid double-run in edge cases
            time.sleep(5)
    except KeyboardInterrupt:
        print("Reminder service arrêté par l'utilisateur.")

if __name__ == "__main__":
    main()