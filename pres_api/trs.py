import serial
import time

# Adaptez le port selon votre config (/dev/ttyACM0 ou /dev/ttyUSB0)
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
    time.sleep(2) # Pause pour laisser l'Arduino rebooter à la connexion
    print("Connexion série établie.")
except:
    print("Erreur: Impossible de se connecter à l'Arduino.")
    exit()

try:
    while True:
        for i in range(16):
            ser.write(f"{i}\n".encode())
            time.sleep(2)
except KeyboardInterrupt:
    ser.close()
    print("\nProgramme arrêté.")