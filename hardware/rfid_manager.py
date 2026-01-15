import time
import json
import os
from datetime import datetime
from mfrc522 import MFRC522
import RPi.GPIO as GPIO
import sys

# Ajout du chemin parent pour importer les modèles
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user_manager import UserManager
from models.emprunt_manager import EmpruntManager
from models.locker_manager import LockerManager
from hardware.arduino_comm import ArduinoComm

class RFIDManager:
    def __init__(self):
        self.reader = MFRC522()
        self.user_mgr = UserManager()
        self.emprunt_mgr = EmpruntManager()
        self.locker_mgr = LockerManager()
        self.arduino = ArduinoComm()
        
        self.state_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'rfid_state.json')
        self.association_timeout = 20  # secondes pour passer la carte
        
        self.last_uid = None
        self.last_read_time = 0

    def read_uid_no_block(self):
        """Tente de lire un UID sans bloquer le programme"""
        (status, TagType) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
        
        if status == self.reader.MI_OK:
            (status, uid_bytes) = self.reader.MFRC522_Anticoll()
            if status == self.reader.MI_OK:
                # Convertit la liste [byte1, byte2, byte3, byte4, byte5] en un seul nombre
                uid = 0
                for i in range(len(uid_bytes)):
                    uid = uid * 256 + uid_bytes[i]
                return uid
        return None

    def get_pending_association(self):
        """Vérifie si Flask a demandé une association dans le fichier JSON"""
        if not os.path.exists(self.state_file):
            return None
        
        try:
            with open(self.state_file, 'r') as f:
                data = json.load(f)
            
            # Vérifier si la demande n'est pas trop vieille (timeout)
            if data.get('mode') == 'ASSOCIATION':
                start_time = data.get('timestamp', 0)
                if time.time() - start_time < self.association_timeout:
                    return data.get('mail')
                else:
                    # Timeout expiré, on repasse en normal
                    self.reset_state()
        except Exception as e:
            print(f"Erreur lecture state: {e}")
        return None

    def reset_state(self):
        """Repasse le système en mode normal"""
        try:
            with open(self.state_file, 'w') as f:
                json.dump({"mode": "NORMAL"}, f)
        except Exception as e:
            print(f"Erreur écriture state: {e}")

    def handle_normal_mode(self, uid):
        """Logique d'emprunt/rendu classique"""
        mail = self.user_mgr.get_mail_by_uid(uid)
        
        if not mail:
            print(f"ID {uid} inconnu. Veuillez scanner le QR Code sur le casier.")
            return

        print(f"Utilisateur reconnu : {mail}")
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1) Si l'utilisateur a déjà un emprunt -> RENDU
        if self.emprunt_mgr.get_emprunt(mail):
            print("Action : Rendu de matériel")
            
            id_casier = self.emprunt_mgr.get_casier_en_cours(mail)
            if not id_casier:
                print("Erreur: emprunt EN COURS mais id_casier introuvable")
                return
            
            print(f"Ouverture du casier {id_casier}...")
            self.arduino.envoyer_commande(id_casier, "OUVRIR")
            self.emprunt_mgr.cloturer_emprunt(mail, now)
            self.locker_mgr.casier_vide(id_casier)
            print(f"✓ Casier {id_casier} rendu et libéré")
            return
        
        # 2) Sinon -> EMPRUNT
        print("Action : Nouvel emprunt")
        
        id_casier = self.locker_mgr.get_premier_libre()
        if id_casier is None:
            print("Désolé, aucun casier n'est disponible.")
            return
        
        id_casier = int(id_casier)
        print(f"Attribution du casier {id_casier}...")
        self.arduino.envoyer_commande(id_casier, "OUVRIR")
        
        ok = self.emprunt_mgr.creer_emprunt(mail, id_casier, now)
        if not ok:
            print("Impossible de créer l'emprunt (déjà un emprunt en cours?)")
            return
        
        self.locker_mgr.casier_plein(id_casier)
        print(f"✓ Casier {id_casier} attribué à {mail}")

    def run(self):
        print("--- Système iRobot RFID prêt (Mode Réactif) ---")
        try:
            while True:
                # 1. Vérifier le JSON à chaque tour de boucle (très rapide)
                pending_mail = self.get_pending_association()
                
                # 2. Tenter de détecter une carte (sans bloquer)
                uid = self.read_uid_no_block()
                
                if uid:
                    # Anti-rebond : ignorer si c'est la même carte dans les 3 dernières secondes
                    current_time = time.time()
                    if uid == self.last_uid and (current_time - self.last_read_time) < 3:
                        time.sleep(0.1)
                        continue
                    
                    self.last_uid = uid
                    self.last_read_time = current_time
                    
                    if pending_mail:
                        # MODE ASSOCIATION
                        print(f"\n>>> ASSOCIATION : Carte {uid} pour {pending_mail}")
                        success = self.user_mgr.register_user(uid, pending_mail)
                        if success:
                            print(f"✓ Succès ! Carte {uid} associée à {pending_mail}")
                        else:
                            print("✗ Erreur : Carte ou Email déjà enregistré.")
                        self.reset_state()
                        time.sleep(2)
                    else:
                        # MODE NORMAL
                        print(f"\n--- Carte détectée : {uid} ---")
                        self.handle_normal_mode(uid)
                        time.sleep(3)  # Anti-rebond supplémentaire
                
                # Petite pause pour ne pas saturer le CPU (10 vérifications/seconde)
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\nArrêt du système...")
        finally:
            print("Nettoyage GPIO...")
            GPIO.cleanup()

if __name__ == "__main__":
    manager = RFIDManager()
    manager.run()