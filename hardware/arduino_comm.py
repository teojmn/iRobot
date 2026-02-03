import serial
import time
import sys
import os
import threading
from hardware.speaker import Speaker

SERIAL_PORT = '/dev/ttyACM0' 
BAUD_RATE = 9600 
MAX_CHANNEL = 14

def send_relay_command(channel, lcd=None, casier_id=None, speaker=None):
    """Initialise la communication série et envoie le numéro de canal."""
    try:
        if channel < 0 or channel > MAX_CHANNEL:
            print(f"Erreur: Le canal {channel} est hors limites (0 à {MAX_CHANNEL}).")
            return
        
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)   
        time.sleep(2.5)
        
        ser.reset_input_buffer()
        
        print(f"Connexion établie sur {SERIAL_PORT}")
        print(f"Envoi : Canal {channel} -> Relais {channel + 1}")
                
        if speaker and casier_id:
            audio_path = os.path.join(os.path.dirname(__file__), "..", "audio", f"audio_{casier_id}.mp3")
            if os.path.exists(audio_path):
                print(f"🔊 Lecture du son pour le casier {casier_id}")
                threading.Thread(target=speaker.play_sound, args=(audio_path, 3), daemon=True).start()
            else:
                print(f"⚠ Fichier audio introuvable: {audio_path}")

        ser.write(bytes([channel]))
        ser.flush()  # Force l'envoi immédiat
        
        
        time.sleep(0.3)
        while ser.in_waiting > 0:
            response = ser.readline().decode('utf-8', errors='ignore').strip()
            if response:
                print(f"Arduino -> {response}")
                
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
        self.speaker = speaker or Speaker(volume=1.0, system_volume=80)
    
    def envoyer_commande(self, id_casier, action):
        """Envoie une commande à l'Arduino pour contrôler un casier"""
        try:
            id_int = int(id_casier)
            
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