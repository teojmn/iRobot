import time

import cv2
import numpy as np
from picamera2 import Picamera2

def main():
    # Initialisation Picamera2
    picam2 = Picamera2()

    # Configuration vidéo (résolution modérée pour accélérer le décodage)
    video_config = picam2.create_video_configuration(
        main={"size": (1280, 720)},  # tu peux baisser à (640, 480) si c'est lent
        buffer_count=4
    )
    picam2.configure(video_config)

    # Démarrage de la caméra
    picam2.start()
    time.sleep(0.5)  # petit délai pour stabiliser exposition / focus

    # Initialisation du détecteur de QR OpenCV
    qr_detector = cv2.QRCodeDetector()

    print("Caméra lancée. Appuie sur Ctrl+C pour quitter.")

    try:
        while True:
            # Récupération d'une frame sous forme de numpy array
            frame = picam2.capture_array()

            # OpenCV travaille en BGR -> conversion
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Détection + décodage du QR code
            data, points, _ = qr_detector.detectAndDecode(frame_bgr)

            if points is not None and len(points) > 0:
                # Si `data` n'est pas vide, on a décodé quelque chose
                if data:
                    print("QR code détecté:", data)

            time.sleep(0.1)  # petit délai pour éviter la surcharge CPU

    except KeyboardInterrupt:
        print("\nArrêt du programme...")
    finally:
        # Nettoyage
        picam2.stop()
        picam2.close()

if __name__ == "__main__":
    main()