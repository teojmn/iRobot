import serial
import time
import sys

# --- Configuration du port série ---
SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 9600 

# Le numéro de canal maximal que l'Arduino accepte (0 à 14 pour les Relais 1 à 15)
MAX_CHANNEL = 14

def send_relay_command(channel):
    """Initialise la communication série et envoie le numéro de canal."""
    try:
        # 1. Vérification de la validité du canal
        if channel < 0 or channel > MAX_CHANNEL:
            print(f"Erreur: Le canal {channel} est hors limites (0 à {MAX_CHANNEL}).")
            return
        
        # 2. Initialisation de la connexion
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE)
        time.sleep(2) # Attendre l'établissement de la connexion

        print(f"Connexion établie sur {SERIAL_PORT}")
        print(f"Envoi de la commande : Canal {channel} (Relais {channel + 1})...")

        # 3. Envoi de la commande binaire
        # On envoie l'octet correspondant au numéro de canal
        ser.write(bytes([channel]))
        
        # 4. Lecture de la confirmation de l'Arduino (optionnel)
        time.sleep(0.1) 
        while ser.in_waiting > 0:
            print(f"Arduino dit: {ser.readline().decode('utf-8').strip()}")

    except serial.SerialException as e:
        print(f"Erreur de communication série: {e}")
        print("Vérifiez le port et la connexion USB.")
    except FileNotFoundError:
        print(f"Erreur: Le port {SERIAL_PORT} est introuvable.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Port série fermé.")

class ArduinoComm:
    def __init__(self):
        self.serial_port = SERIAL_PORT
        self.baud_rate = BAUD_RATE
    
    def envoyer_commande(self, id_casier, action):
        """Envoie une commande à l'Arduino pour contrôler un casier"""
        try:
            # FORCE la conversion en entier pour être sûr du calcul
            id_int = int(id_casier)
            # Convertir l'ID du casier (1-15) en numéro de canal (0-14)
            channel = id_int - 1
            
            if action.upper() == "OUVRIR":
                print(f"DEBUG ARDUINO: Envoi Canal {channel} pour Casier {id_int}")
                send_relay_command(channel)
            else:
                print(f"Action inconnue: {action}")
        except ValueError:
            print(f"Erreur: id_casier '{id_casier}' n'est pas un nombre valide.")

if __name__ == "__main__":
    # Vérifie si le numéro de canal a été passé en argument
    if len(sys.argv) != 2:
        print("Utilisation: python3 relay_transmitter.py <numero_du_canal>")
        print("Exemple (Relais 8): python3 relay_transmitter.py 7")
        sys.exit(1)
    
    try:
        # Tente de convertir l'argument en entier (le canal)
        target_channel = int(sys.argv[1])
        send_relay_command(target_channel)
    except ValueError:
        print("Erreur: L'argument doit être un nombre entier.")
        sys.exit(1)