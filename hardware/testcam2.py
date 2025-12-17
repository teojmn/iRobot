#most importantly for this code to run is to import OpenCV
import cv2

# set up camera object called Cap which we will use to find OpenCV
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Erreur: Impossible d'ouvrir la caméra")
    exit(1)

# QR code detection Method
detector = cv2.QRCodeDetector()

print("Caméra initialisée. Scannez un QR code (Ctrl+C pour quitter)...")

#This creates an Infinite loop to keep your camera searching for data at all times
try:
    while True:
        
        # Below is the method to get a image of the QR code
        ret, img = cap.read()
        
        if not ret:
            print("Erreur de lecture de frame")
            continue
        
        # Below is the method to read the QR code by detetecting the bounding box coords and decoding the hidden QR data 
        data, bbox, _ = detector.detectAndDecode(img)
        
        # This is how we get that Blue Box around our Data. This will draw one, and then Write the Data along with the top
        if bbox is not None and data:
            print(f"QR code détecté: {data}")
            
            # Logique métier ici
            if data == 'red':
                print("→ Action RED détectée")
            elif data == 'green':
                print("→ Action GREEN détectée")
        
        # Pas de cv2.imshow() pour compatibilité SSH
        
        # Quitter avec 'q' si en mode GUI
        # if cv2.waitKey(1) == ord("q"):
        #     break

except KeyboardInterrupt:
    print("\nArrêt de la détection")
finally:
    cap.release()
    # cv2.destroyAllWindows()  # Inutile sans imshow
    print("Caméra libérée")