Voici un court mode d'emploi et quelques exemples d'utilisation du CameraHandler depuis d'autres scripts.

- Ce que renvoie CameraHandler
  - read() -> (frame, qr_list)
  - wait_for_qr(timeout) -> liste de QR ou None
  - qr_list : liste de dicts { "data": str, "type": "EMAIL"|"NUMERIC", "rect": {...}, "polygon": [...] }

- Dépendances
  - opencv-python (ou opencv-python-headless si environnement sans affichage)

Exemple 1 — usage bloquant (attente d'un QR) :

````python
```python
from hardware.camera_handler import CameraHandler

cam = CameraHandler(camera_index=0)
cam.start()

# attend un QR pendant 10 secondes
result = cam.wait_for_qr(timeout=10.0)
if result:
    for qr in result:
        print("type:", qr["type"], "data:", qr["data"])
else:
    print("Aucun QR détecté")

cam.stop()
```
````

Exemple 2 — usage avec callback (réception en continu) :

````python
```python
from hardware.camera_handler import CameraHandler

def on_qr(qr_list, frame):
    for qr in qr_list:
        print("QR détecté:", qr["type"], qr["data"])
        # ex: envoyer la data à un service, stocker, etc.

cam = CameraHandler(use_thread=True)
cam.register_callback(on_qr)
cam.start()

try:
    # faire autre chose; le callback est appelé en tâche de fond
    while True:
        pass
except KeyboardInterrupt:
    cam.stop()
```
````





Voici une explication concise des deux modes d'utilisation principaux (blocking vs callback), ce qu'ils font et quand les préférer.

1) Mode bloquant — wait_for_qr(timeout)
- Ce que ça fait
  - Bloque l'appelant jusqu'à ce qu'au moins un QR valide soit détecté ou que le timeout expire.
  - Retourne une liste de dicts [{data, type, rect, polygon}] ou None si timeout.
- Quand l'utiliser
  - Flux séquentiel simple : le script doit attendre une seule valeur avant de continuer (ex. étape « lire un QR » dans un processus CLI ou script de configuration).
  - Interfaces console ou scripts courts où on veut une logique linéaire (pas de gestion de thread/événements).
- Avantages / limites
  - Simple à utiliser, pas besoin d'écrire de gestion d'événements.
  - Bloque le thread courant — pas adapté si l'application doit rester réactive (GUI, serveur).

2) Mode événementiel — register_callback(fn) + start(use_thread=True)
- Ce que ça fait
  - Lance (optionnellement) un thread de capture en arrière-plan.
  - Appelle fn(qr_list, frame) à chaque frame contenant au moins un QR valide.
  - La capture continue tant que CameraHandler tourne ; plusieurs détections successives arrivent via la callback.
- Quand l'utiliser
  - Applications long-running : services, GUI, robot, serveur ou tout code qui doit rester réactif pendant la détection.
  - Quand on veut traiter chaque détection immédiatement, afficher un retour visuel, ou envoyer les données ailleurs sans stopper la boucle principale.
- Avantages / limites
  - Non bloquant pour l'application principale ; bonne réactivité.
  - Les callbacks doivent être rapides et thread-safe (ne pas faire de blocages longs dans la callback). Si traitement long, déléguer à une queue/worker.
  - Penser à unregister_callback() et cam.stop() proprement au shutdown.

Remarques pratiques
- Format des résultats : chaque item contient 'data' (str), 'type' ('EMAIL' | 'NUMERIC'), 'rect' et 'polygon'.
- Pour les environnements sans affichage, utilisez opencv-python-headless.
- Si vous n'avez pas besoin de thread, créez CameraHandler(use_thread=False) et appelez périodiquement capture_once() dans votre boucle principale (utile pour boucles d'événements synchrones).
- Ajustez decode_interval pour réduire la charge CPU (ex. decode_interval=0.1 pour 10 Hz).

Exemples d'usage résumés
- Single-scan CLI : wait_for_qr(timeout=10)
- Robot / service / GUI : register_callback + start(use_thread=True)

Si vous voulez, je peux fournir un petit exemple concret adapté à votre cas (CLI, GUI ou service).