import cv2
import numpy as np
from pyzbar.pyzbar import decode
from picamera2 import Picamera2
import time

def read_qr_code_rpicam():
    # ... (le code précédent est inchangé) ...
    # L'important est d'utiliser Picamera2, qui est le bon outil si rpicam-hello fonctionne.
    # ...
    # Initialisation de Picamera2
    picam2 = Picamera2()
    config = picam2.create_preview_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    
    time.sleep(1)
    
    # ... (boucle de détection) ...
    try:
        while True:
            frame_bayer = picam2.capture_array()
            frame_bgr = cv2.cvtColor(frame_bayer, cv2.COLOR_BAYER_BGGR2BGR)
            gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
            
            for obj in decode(gray):
                data = obj.data.decode('utf-8')
                print(f"QR Code détecté: {data}")
                
    except KeyboardInterrupt:
        print("\nArrêt de la détection.")
    finally:
        picam2.stop()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    read_qr_code_rpicam()