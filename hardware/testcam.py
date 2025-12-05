import cv2
from pyzbar.pyzbar import decode

def read_qr_code():
    """Lit un QR code depuis la caméra."""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("Erreur: Impossible d'ouvrir la caméra")
        return
    
    print("Positionnez le QR code devant la caméra (q pour quitter)...")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Décoder les QR codes
        for obj in decode(frame):
            print(f"Email détecté: {obj.data.decode('utf-8')}")
        
        # Afficher la frame
        cv2.imshow('Camera', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    read_qr_code()