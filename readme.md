# 1. Aller dans le dossier de test

```
cd ~/test_fonctionnel
```

# 2. Créer le venv
```
python3 -m venv venv
```

# 3. Activer le venv
```
source venv/bin/activate
```

# 4. Installer les dépendances
```
pip install picamera2 pyzbar pillow
```

# 5. Créer le fichier requirements.txt
pip freeze > requirements.txt

# 6. Lancer le test
cd ~/test_fonctionnel
source venv/bin/activate
python3 test_fonctionnel.py