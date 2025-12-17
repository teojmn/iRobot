# consigne.py
import csv
from datetime import datetime
from picamera2 import Picamera2
from pyzbar.pyzbar import decode
from PIL import Image
import time

# Configuration caméra
camera = Picamera2()
camera.configure(camera.create_preview_configuration(main={"size": (640, 480)}))
camera.start()

def lire_emprunts():
    """Lit les emprunts"""
    with open('emprunts.csv', 'r') as f:
        return list(csv.DictReader(f))

def emprunt_en_cours(email):
    """Vérifie si l'étudiant a un emprunt en cours"""
    email = email.replace('mailto:', '')
    emprunts = lire_emprunts()
    
    for e in emprunts:
        if e['mail'].replace('mailto:', '') == email and e['statut'] == 'EN_COURS':
            return e
    return None

def casier_disponible():
    """Trouve un casier vide (False = vide)"""
    with open('casiers.csv', 'r') as f:
        casiers = list(csv.DictReader(f))
    
    for c in casiers:
        if c['statut'] == 'False':
            return c['id_casier']
    return None

def creer_emprunt(email, id_casier):
    """Crée un nouvel emprunt"""
    emprunts = lire_emprunts()
    nouvel_id = max([int(e['id_emprunt']) for e in emprunts]) + 1 if emprunts else 1
    
    with open('emprunts.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        now = datetime.now()
        writer.writerow([
            nouvel_id,
            email,
            id_casier,
            now.strftime('%Y-%m-%d'),
            now.strftime('%H:%M:%S'),
            'EN_COURS'
        ])
    
    print(f"✅ Emprunt créé - Casier #{id_casier}")

def cloturer_emprunt(emprunt):
    """Clôture un emprunt"""
    emprunts = lire_emprunts()
    
    for e in emprunts:
        if e['id_emprunt'] == emprunt['id_emprunt']:
            e['statut'] = 'TERMINE'
    
    with open('emprunts.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id_emprunt', 'mail', 'id_casier', 'date', 'heure', 'statut'])
        writer.writeheader()
        writer.writerows(emprunts)
    
    print(f"✅ Retour effectué - Casier #{emprunt['id_casier']}")

def maj_casier(id_casier, occupe):
    """Met à jour le statut d'un casier"""
    with open('casiers.csv', 'r') as f:
        casiers = list(csv.DictReader(f))
    
    for c in casiers:
        if c['id_casier'] == str(id_casier):
            c['statut'] = str(occupe)
    
    with open('casiers.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id_casier', 'statut'])
        writer.writeheader()
        writer.writerows(casiers)

def ouvrir_casier(id_casier):
    """Ouvre le casier (à implémenter avec GPIO)"""
    print(f"🔓 OUVERTURE CASIER #{id_casier}")
    # TODO: Ajouter code GPIO ici

def scanner_qr():
    """Scanne un QR code avec la caméra"""
    print("📷 Scannez votre carte étudiante...")
    
    while True:
        # Capture image
        image = camera.capture_array()
        
        # Décode QR codes
        codes = decode(Image.fromarray(image))
        
        if codes:
            email = codes[0].data.decode('utf-8')
            print(f"✓ QR scanné: {email}")
            return email
        
        time.sleep(0.1)

def traiter_scan(email):
    """Traite le scan d'une carte"""
    print(f"\n{'='*50}")
    print(f"Étudiant: {email}")
    
    emprunt = emprunt_en_cours(email)
    
    if emprunt:
        # RETOUR
        print("→ Mode: RETOUR")
        id_casier = emprunt['id_casier']
        ouvrir_casier(id_casier)
        cloturer_emprunt(emprunt)
        maj_casier(id_casier, False)
    else:
        # EMPRUNT
        print("→ Mode: EMPRUNT")
        id_casier = casier_disponible()
        
        if id_casier:
            ouvrir_casier(id_casier)
            creer_emprunt(email, id_casier)
            maj_casier(id_casier, True)
        else:
            print("❌ Aucun casier disponible")
    
    print(f"{'='*50}\n")

# Programme principal
if __name__ == "__main__":
    print("🤖 Système de consigne démarré\n")
    
    try:
        while True:
            email = scanner_qr()
            traiter_scan(email)
            time.sleep(2)  # Pause entre scans
    
    except KeyboardInterrupt:
        print("\n🛑 Arrêt du système")
        camera.stop()