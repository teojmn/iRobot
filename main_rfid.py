import time
from hardware.arduino_comm import ArduinoComm # Pour ouvrir les casiers
from models.user_manager import UserManager
from models.emprunt_manager import EmpruntManager
from models.locker_manager import LockerManager
# Importez ici votre lib RFID (ex: SimpleMFRC522)

class IRobotSystem:
    def __init__(self):
        self.user_mgr = UserManager()
        self.emprunt_mgr = EmpruntManager()
        self.locker_mgr = LockerManager()
        # self.reader = SimpleMFRC522()
        self.state_file = "data/rfid_state.json" # Pour communiquer avec Flask

    def loop(self):
        print("Système RFID prêt...")
        while True:
            # 1. Vérifier si Flask a demandé une association (via un fichier JSON par ex)
            # 2. Sinon, mode lecture normale :
            
            # uid, text = self.reader.read_no_block()
            uid = None # Simulation
            
            if uid:
                mail = self.user_mgr.get_mail_by_uid(uid)
                if mail:
                    self.handle_access(mail)
                else:
                    print("Carte inconnue. Scannez le QR Code pour vous enregistrer.")
            
            time.sleep(0.5)

    def handle_access(self, mail):
        # Logique existante : si a un emprunt -> rendre, sinon -> emprunter
        if self.emprunt_mgr.get_emprunt(mail):
            # Clôturer l'emprunt et ouvrir le casier
            pass
        else:
            # Trouver un casier vide et créer l'emprunt
            pass