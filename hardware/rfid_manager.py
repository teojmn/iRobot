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
from hardware.lcd_display import LCDDisplay

class RFIDManager:
    def __init__(self):
        self.reader = MFRC522()
        self.user_mgr = UserManager()
        self.emprunt_mgr = EmpruntManager()
        self.locker_mgr = LockerManager()
        self.lcd = LCDDisplay()
        
        # Initialiser ArduinoComm (qui gère le haut-parleur en interne)
        self.arduino = ArduinoComm(self.lcd)
        
        self.state_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'rfid_state.json')
        self.association_timeout = 20
        
        self.last_uid = None
        self.last_read_time = 0
        self.cooldown_duration = 5
        self.is_processing = False

    def read_uid_no_block(self):
        """Tente de lire un UID sans bloquer, avec le format SimpleMFRC522"""
        (status, TagType) = self.reader.MFRC522_Request(self.reader.PICC_REQIDL)
        
        if status == self.reader.MI_OK:
            (status, uid_bytes) = self.reader.MFRC522_Anticoll()
            if status == self.reader.MI_OK:
                # FORMULE EXACTE DE SIMPLEMFRC522 :
                # On prend les 4 premiers octets et on les transforme en entier
                n = 0
                for i in range(0, 4):
                    n = n << 8
                    n = n | uid_bytes[i]
                return n
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
        try:
            self.lcd.write("Veuillez", "patienter...")
        except OSError as e:
            self.lcd.cursor_mode = 'hide'
            print(f"Erreur LCD: {e}")
        
        mail = self.user_mgr.get_mail_by_uid(uid)
        
        if not mail:
            print(f"ID {uid} inconnu. Veuillez scanner le QR Code sur le casier.")
            try:
                self.lcd.write("Utilisateur", "inconnu")
                time.sleep(3)
                self.lcd.write("Scannez le", "QR code")
            except OSError:
                self.lcd.cursor_mode = 'hide'
                pass
            return

        print(f"Utilisateur reconnu : {mail}")
        
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 1) Si l'utilisateur a déjà un emprunt -> RENDU
        if self.emprunt_mgr.get_emprunt(mail):
            print("Action : Rendu de matériel")
            
            id_casier = self.emprunt_mgr.get_casier_en_cours(mail)
            if not id_casier:
                print("Erreur: emprunt EN COURS mais id_casier introuvable")
                self.lcd.start_alternating()
                return
            
            print(f"Ouverture du casier {id_casier}...")
            self.arduino.envoyer_commande(id_casier, "OUVRIR")  # LCD géré dans arduino_comm
            self.emprunt_mgr.cloturer_emprunt(mail, now)
            
            # ✅ CORRECTION : Après un RENDU, le câble est déposé → casier devient PLEIN
            self.locker_mgr.casier_plein(id_casier)
            print(f"✓ Casier {id_casier} rendu et libéré")
            return
        
        # 2) Sinon -> EMPRUNT
        print("Action : Nouvel emprunt")
        
        id_casier = self.locker_mgr.get_premier_libre()
        if id_casier is None:
            print("Désolé, aucun casier n'est disponible.")
            self.lcd.write_temporary("Aucun casier", "disponible", 3)
            return
        
        id_casier = int(id_casier)
        print(f"Attribution du casier {id_casier}...")
        self.arduino.envoyer_commande(id_casier, "OUVRIR")
        
        ok = self.emprunt_mgr.creer_emprunt(mail, id_casier, now)
        if not ok:
            print("Impossible de créer l'emprunt (déjà un emprunt en cours?)")
            self.lcd.start_alternating()
            return
        
        # ✅ CORRECTION : Après un EMPRUNT, le câble est pris → casier devient VIDE
        self.locker_mgr.casier_vide(id_casier)
        print(f"✓ Casier {id_casier} attribué à {mail}")

    def run(self):
        print("--- Système iRobot RFID prêt (Mode Réactif) ---")
        try:
            while True:
                # 1. Vérifier le JSON à chaque tour de boucle (très rapide)
                pending_mail = self.get_pending_association()
                
                # Afficher le bon message selon le mode
                if pending_mail and not hasattr(self, '_association_msg_shown'):
                    self.lcd.write("Enregistrez", "votre carte")
                    self._association_msg_shown = True
                elif not pending_mail and hasattr(self, '_association_msg_shown'):
                    self.lcd.start_alternating()
                    delattr(self, '_association_msg_shown')
                
                # 2. Vérifier si on est en période de cooldown
                current_time = time.time()
                if self.is_processing and (current_time - self.last_read_time) < self.cooldown_duration:
                    time.sleep(0.1)
                    continue
                
                # Fin du cooldown, réactiver le lecteur
                if self.is_processing:
                    self.is_processing = False
                    print("Lecteur RFID réactivé")
                
                # 3. Tenter de détecter une carte (sans bloquer)
                uid = self.read_uid_no_block()
                
                if uid:
                    # Bloquer immédiatement le lecteur
                    self.is_processing = True
                    self.last_uid = uid
                    self.last_read_time = current_time
                    print(f"Carte détectée - Lecteur RFID bloqué pour {self.cooldown_duration}s")
                    
                    if pending_mail:
                        # MODE ASSOCIATION
                        print(f"\n>>> ASSOCIATION : Carte {uid} pour {pending_mail}")
                        success = self.user_mgr.register_user(uid, pending_mail)
                        
                        if success:
                            print(f"✓ Succès ! Carte {uid} associée à {pending_mail}")
                            self.lcd.write_temporary("Succes !", "", 3)
                            # Écrire le succès dans le JSON pour que Flask le lise
                            try:
                                with open(self.state_file, 'w') as f:
                                    json.dump({
                                        "mode": "SUCCESS",
                                        "mail": pending_mail,
                                        "uid": uid,
                                        "timestamp": time.time()
                                    }, f)
                            except Exception as e:
                                print(f"Erreur écriture succès: {e}")
                        else:
                            print("✗ Erreur : Carte ou Email déjà enregistré.")
                            self.lcd.write_temporary("Carte deja", "enregistree", 3)
                            # Écrire l'échec dans le JSON
                            try:
                                with open(self.state_file, 'w') as f:
                                    json.dump({
                                        "mode": "ERROR",
                                        "mail": pending_mail,
                                        "message": "Carte ou email déjà enregistré",
                                        "timestamp": time.time()
                                    }, f)
                            except Exception as e:
                                print(f"Erreur écriture erreur: {e}")
                        
                        delattr(self, '_association_msg_shown')
                    else:
                        # MODE NORMAL
                        print(f"\n--- Carte détectée : {uid} ---")
                        self.handle_normal_mode(uid)
                
                # Petite pause pour ne pas saturer le CPU (10 vérifications/seconde)
                time.sleep(0.1)
                
        except KeyboardInterrupt:
            print("\n\nArrêt du système...")
        finally:
            print("Nettoyage GPIO...")
            self.lcd.cleanup()
            GPIO.cleanup()

if __name__ == "__main__":
    manager = RFIDManager()
    manager.run()