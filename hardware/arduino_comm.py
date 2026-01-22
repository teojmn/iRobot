import serial
import time
import sys
import os
import threading
from hardware.speaker import Speaker

# --- Configuration du port série ---
SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 9600 

# Le numéro de canal maximal que l'Arduino accepte (0 à 14 pour les Relais 1 à 15)
MAX_CHANNEL = 14

def send_relay_command(channel, lcd=None, casier_id=None, speaker=None):
    """Initialise la communication série et envoie le numéro de canal."""
    try:
        # 1. Vérification de la validité du canal
        if channel < 0 or channel > MAX_CHANNEL:
            print(f"Erreur: Le canal {channel} est hors limites (0 à {MAX_CHANNEL}).")
            return
        
        # 2. Initialisation de la connexion
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
        
        # 3. Attendre que l'Arduino finisse de redémarrer (auto-reset à l'ouverture USB)
        time.sleep(2.5)
        
        # 4. Vider le buffer résiduel (évite les lectures parasites)
        ser.reset_input_buffer()
        
        print(f"Connexion établie sur {SERIAL_PORT}")
        print(f"Envoi : Canal {channel} -> Relais {channel + 1}")
                
        # Jouer le son maintenant que la serrure est ouverte
        if speaker and casier_id:
            # Construire le chemin du fichier audio spécifique au casier
            audio_path = os.path.join(os.path.dirname(__file__), "..", "audio", f"audio_{casier_id}.mp3")
            if os.path.exists(audio_path):
                print(f"🔊 Lecture du son pour le casier {casier_id}")
                threading.Thread(target=speaker.play_sound, args=(audio_path, 3), daemon=True).start()
            else:
                print(f"⚠ Fichier audio introuvable: {audio_path}")

        # 5. Envoi de la commande binaire (1 octet)
        ser.write(bytes([channel]))
        ser.flush()  # Force l'envoi immédiat
        
        
        # 6. Lecture de la confirmation de l'Arduino (optionnel)
        time.sleep(0.3)
        while ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if response:
                print(f"Arduino -> {response}")
                
                # Afficher sur LCD et jouer le son AU MOMENT où le relais s'active
                if lcd and casier_id:
                    lcd.write_temporary(f"Casier {casier_id}", "ouvert", 4)

    except serial.SerialException as e:
        print(f"Erreur de communication série: {e}")
        print("Vérifiez le port et la connexion USB.")
    except FileNotFoundError:
        print(f"Erreur: Le port {SERIAL_PORT} est introuvable.")
    except Exception as e:
        print(f"Erreur inattendue: {e}")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Port série fermé.\n")

class ArduinoComm:
    def __init__(self, lcd=None, speaker=None):
        self.serial_port = SERIAL_PORT
        self.baud_rate = BAUD_RATE
        self.lcd = lcd
        self.speaker = speaker or Speaker(volume=0.9)
    
    def envoyer_commande(self, id_casier, action):
        """Envoie une commande à l'Arduino pour contrôler un casier"""
        try:
            # Force la conversion en entier (important si id_casier est une string)
            id_int = int(id_casier)
            
            # Convertir l'ID du casier (1-15) en numéro de canal (0-14)
            channel = id_int - 1
            
            if action.upper() == "OUVRIR":
                print(f"\n🔓 Ouverture du casier {id_int} (Canal Arduino: {channel})")
                send_relay_command(channel, self.lcd, id_int, self.speaker)
            else:
                print(f"Action inconnue: {action}")
                
        except ValueError:
            print(f"Erreur: id_casier '{id_casier}' n'est pas un nombre valide.")
        except Exception as e:
            print(f"Erreur lors de l'envoi: {e}")

if __name__ == "__main__":
    # Mode test en ligne de commande
    if len(sys.argv) != 2:
        print("Usage: python3 arduino_comm.py <numero_du_canal>")
        print("Exemple pour Relais 1: python3 arduino_comm.py 0")
        print("Exemple pour Relais 8: python3 arduino_comm.py 7")
        sys.exit(1)
    
    try:
        target_channel = int(sys.argv[1])
        send_relay_command(target_channel)
    except ValueError:
        print("Erreur: L'argument doit être un nombre entier (0-14).")
        sys.exit(1)