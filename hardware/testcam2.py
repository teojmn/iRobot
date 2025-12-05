import cv2
import numpy as np
from pyzbar.pyzbar import decode
from picamera2 import Picamera2
import time

def read_qr_code_rpicam():
    """
    Lit un QR code depuis la Raspberry Pi Camera Module 3
    en utilisant Picamera2 et pyzbar.
    """
    print("Initialisation de Picamera2...")
    try:
        # Initialisation de Picamera2
        # On demande la configuration pour une résolution de 640x480 (preview)
        picam2 = Picamera2()
        config = picam2.create_preview_configuration(main={"size": (640, 480)})
        picam2.configure(config)
        picam2.start()
        
        # Laisser le temps à la caméra de s'initialiser
        time.sleep(1)
        
    except Exception as e:
        print(f"Erreur lors de l'initialisation de Picamera2: {e}")
        print("Vérifiez que la caméra est connectée et activée (via raspi-config).")
        return
    
    print("Détection de QR code en cours (Ctrl+C pour quitter)...")
    
    try:
        while True:
            # 1. Capture de l'image (frame)
            # La fonction capture_array renvoie un tableau NumPy (Bayer format)
            frame_bayer = picam2.capture_array()

            # 2. Conversion en image couleur (BGR) pour OpenCV/pyzbar
            # La conversion de Bayer à BGR est nécessaire pour l'interprétation correcte des couleurs
            frame_bgr = cv2.cvtColor(frame_bayer, cv2.COLOR_BAYER_BGGR2BGR)
            
            # 3. Traitement de l'image pour la détection (souvent mieux en niveaux de gris)
            # Une conversion en niveaux de gris est plus rapide et suffisante pour pyzbar
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            
            # 4. Décoder les codes barres/QR codes
            # obj.data contient le payload du QR code en bytes
            for obj in decode(gray):
                data = obj.data.decode('utf-8')
                print(f"QR Code détecté: {data}")
                
            # Facultatif: Afficher la fenêtre de la caméra (utile pour le debug)
            # cv2.imshow("QR Code Detector", frame_bgr)
            # if cv2.waitKey(1) & 0xFF == ord('q'):
            #     break

            # Limiter la fréquence de rafraîchissement si la CPU est trop sollicitée
            # time.sleep(0.05) 
            
    except KeyboardInterrupt:
        print("\nArrêt de la détection.")
    finally:
        # Arrêter la caméra et détruire les fenêtres (si elles étaient affichées)
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    read_qr_code_rpicam()