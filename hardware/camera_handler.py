import time

import cv2
import numpy as np
from picamera2 import Picamera2

def main():
    # Initialisation Picamera2
    picam2 = Picamera2()

    # Configuration vidéo (résolution modérée pour accélérer le décodage)
    video_config = picam2.create_video_configuration(
        main={"size": (1280, 720)},  # tu peux baisser à (640, 480) si c’est lent
        buffer_count=4
    )
    picam2.configure(video_config)

    # Démarrage de la caméra
    picam2.start()
    time.sleep(0.5)  # petit délai pour stabiliser exposition / focus

    # Initialisation du détecteur de QR OpenCV
    qr_detector = cv2.QRCodeDetector()

    print("Caméra lancée. Appuie sur 'q' dans la fenêtre pour quitter.")

    try:
        while True:
            # Récupération d'une frame sous forme de numpy array
            # Par défaut Picamera2 renvoie un tableau en RGB
            frame = picam2.capture_array()

            # OpenCV travaille en BGR -> conversion facultative pour cohérence,
            # (QRCodeDetector marche généralement aussi sur RGB)
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

            # Détection + décodage du QR code
            data, points, _ = qr_detector.detectAndDecode(frame_bgr)

            if points is not None and len(points) > 0:
                # Dessiner le polygone autour du QR code
                pts = points[0].astype(int)
                for i in range(len(pts)):
                    pt1 = tuple(pts[i])
                    pt2 = tuple(pts[(i + 1) % len(pts)])
                    cv2.line(frame_bgr, pt1, pt2, (255, 0, 255), 2)

                # Si `data` n'est pas vide, on a décodé quelque chose
                if data:
                    print("data found:", data)

                    # Afficher le texte décodé au-dessus du QR
                    x, y = pts[0]
                    cv2.putText(
                        frame_bgr,
                        data,
                        (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (0, 255, 0),
                        2
                    )

            # Afficher le flux vidéo (facultatif)
            cv2.imshow("QR code detector (Picamera2)", frame_bgr)

            # Sortie sur 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Nettoyage
        cv2.destroyAllWindows()
        picam2.stop()
        picam2.close()

if __name__ == "__main__":
    main()