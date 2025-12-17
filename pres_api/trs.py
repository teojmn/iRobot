import serial
import time
import requests
import argparse

"""
Script trs.py

Usage :
    python3 trs.py --api-url http://localhost:3000 --arduino-port /dev/ttyACM0
"""

def main():
    parser = argparse.ArgumentParser(description="Interface API <-> Arduino pour casiers")
    parser.add_argument("--api-url", default="http://localhost:3000",
                        help="URL de base de l'API des casiers (par défaut: http://localhost:3000)")
    parser.add_argument("--arduino-port", default="/dev/ttyACM0",
                        help="Port série de l'Arduino (par défaut: /dev/ttyACM0)")
    parser.add_argument("--poll-interval", type=float, default=0.5,
                        help="Intervalle de polling de l'API en secondes (par défaut: 0.5)")
    args = parser.parse_args()

    API_URL = args.api_url.rstrip("/")  # pour éviter les // dans les URLs
    ARDUINO_PORT = args.arduino_port
    POLL_INTERVAL = args.poll_interval

    # Connexion série à l'Arduino
    try:
        ser = serial.Serial(ARDUINO_PORT, 9600, timeout=1)
        time.sleep(2)  # Pause pour laisser l'Arduino rebooter
        print(f"✅ Connexion série établie avec l'Arduino sur {ARDUINO_PORT}.")
    except Exception as e:
        print(f"❌ Erreur: Impossible de se connecter à l'Arduino ({ARDUINO_PORT}): {e}")
        return

    print(f"🔄 Écoute de l'API sur {API_URL}/next-casier ...")
    print("Appuyez sur Ctrl+C pour arrêter.\n")

    try:
        while True:
            try:
                # Interroge l'API pour savoir s'il y a un casier à ouvrir
                response = requests.get(f"{API_URL}/next-casier", timeout=2)
                
                if response.status_code == 200:
                    data = response.json()
                    casier_id = data.get("casierId")

                    if casier_id:
                        print(f"📦 Commande reçue: ouverture du casier {casier_id}")

                        # casierId est dans [1..15] -> index Arduino dans [0..14]
                        arduino_index = casier_id - 1

                        # Envoie la commande à l'Arduino (en ASCII + \n)
                        ser.write(f"{arduino_index}\n".encode())
                        print(f"✅ Commande envoyée à l'Arduino: index {arduino_index} (casier {casier_id})")

                        # On laisse l'Arduino gérer l'ouverture pendant ~5 s
                        # (le timing précis est dans le code Arduino)
                        time.sleep(0.5)  # petite pause avant de repoller l'API

                elif response.status_code == 204:
                    # Pas de casier en attente (No Content)
                    # On ne log pas pour éviter le spam
                    pass
                else:
                    print(f"⚠️ Réponse inattendue de l'API: {response.status_code}")

            except requests.exceptions.RequestException as e:
                print(f"⚠️ Erreur de connexion à l'API ({API_URL}): {e}")

            # Attend avant la prochaine vérification
            time.sleep(POLL_INTERVAL)

    except KeyboardInterrupt:
        ser.close()
        print("\n🛑 Programme arrêté proprement.")

if __name__ == "__main__":
    main()