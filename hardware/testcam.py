import cv2
from pyzbar.pyzbar import decode
import numpy as np

def read_qr_code():
    """Lit un QR code depuis la caméra et affiche l'adresse email."""
    
    # Initialiser la caméra (0 pour la caméra par défaut)
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erreur: Impossible d'ouvrir la caméra")
        return
    
    print("Appuyez sur 'q' pour quitter")
    print("Positionnez le QR code devant la caméra...")
    
    while True:
        # Capturer une frame
        ret, frame = cap.read()
        
        if not ret:
            print("Erreur: Impossible de lire la frame")
            break
        
        # Décoder les QR codes dans la frame
        decoded_objects = decode(frame)
        
        for obj in decoded_objects:
            # Extraire les données du QR code
            data = obj.data.decode('utf-8')
            print(f"\nQR Code détecté!")
            print(f"Adresse email: {data}")
            
            # Dessiner un rectangle autour du QR code
            points = obj.polygon
            if len(points) == 4:
                pts = [(point.x, point.y) for point in points]
                pts = np.array(pts, dtype=np.int32)
                cv2.polylines(frame, [pts], True, (0, 255, 0), 3)
        
        # Afficher la frame
        cv2.imshow('Test Camera - QR Code Reader', frame)
        
        # Quitter avec 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # Libérer les ressources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    read_qr_code()