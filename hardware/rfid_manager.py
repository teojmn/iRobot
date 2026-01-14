import time
import json
import os
from datetime import datetime
from mfrc522 import SimpleMFRC522
import sys

# Ajout du chemin parent pour importer les modèles
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.user_manager import UserManager
from models.emprunt_manager import EmpruntManager
from models.locker_manager import LockerManager
from hardware.arduino_comm import ArduinoComm

class RFIDManager:
    def __init__(self):
        self.reader = SimpleMFRC522()
        self.user_mgr = UserManager()
        self.emprunt_mgr = EmpruntManager()
        self.locker_mgr = LockerManager()
        self.arduino = ArduinoComm()
        
        self.state_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'rfid_state.json')
        self.association_timeout = 20  # secondes pour passer la carte

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
        print("--- Système iRobot RFID prêt ---")
        try:
            while True:
                # A. Vérifier si on est en mode association
                pending_mail = self.get_pending_association()
                
                if pending_mail:
                    print(f"\n>>> MODE ASSOCIATION ACTIF pour : {pending_mail}")
                    print("En attente d'une carte...")
                    
                    # Lecture bloquante courte pour l'association
                    try:
                        uid, text = self.reader.read()
                        if uid:
                            success = self.user_mgr.register_user(uid, pending_mail)
                            if success:
                                print(f"✓ Succès ! Carte {uid} associée à {pending_mail}")
                            else:
                                print("✗ Erreur : Carte ou Email déjà enregistré.")
                            self.reset_state()
                            time.sleep(2)
                    except Exception as e:
                        print(f"Erreur lecture RFID (association): {e}")
                        self.reset_state()
                else:
                    # B. Mode Normal (Lecture bloquante avec timeout court)
                    try:
                        # On utilise read() avec un timeout implicite
                        uid, text = self.reader.read()
                        if uid:
                            print(f"\n--- Carte détectée : {uid} ---")
                            self.handle_normal_mode(uid)
                            time.sleep(3)  # Anti-rebond pour éviter de lire 10 fois la carte
                    except Exception as e:
                        # Si pas de carte détectée, on continue la boucle
                        pass
                
                time.sleep(0.2)
                
        except KeyboardInterrupt:
            print("\n\nArrêt du système...")
        finally:
            print("Nettoyage GPIO...")

if __name__ == "__main__":
    manager = RFIDManager()
    manager.run()