import serial
import time

# Configuration du port série (vérifiez si c'est /dev/ttyUSB0 ou /dev/ttyACM0)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
time.sleep(2) # Attente de l'initialisation de l'Arduino

try:
    while True:
        for i in range(0, 16): # Envoie de 0 à 15
            print(f"Envoi de l'entier : {i}")
            ser.write(f"{i}\n".encode()) # Envoi sous forme de texte avec un retour à la ligne
            time.sleep(2)
except KeyboardInterrupt:
    ser.close()
    print("Connexion fermée.")