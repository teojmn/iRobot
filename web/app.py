import os
import json
import time
import re
from datetime import datetime
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATE_FILE = os.path.join(DATA_DIR, "rfid_state.json")

ASSOCIATION_TIMEOUT_SECONDS = 20

EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@(epitech\.eu|epitech\.digital)$", re.IGNORECASE)

app = Flask(__name__)
app.secret_key = "change-me-in-prod"  # nécessaire pour flash messages

def ensure_state_file():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, "w") as f:
            json.dump({"mode": "NORMAL"}, f)

def read_state():
    ensure_state_file()
    try:
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    except Exception:
        return {"mode": "NORMAL"}

def write_state(payload: dict):
    ensure_state_file()
    with open(STATE_FILE, "w") as f:
        json.dump(payload, f)

def is_valid_email(email: str) -> bool:
    if not email:
        return False
    email = email.strip()
    return EMAIL_REGEX.match(email) is not None

@app.get("/")
def root():
    return redirect(url_for("register"))

@app.route('/status')
def check_status():
    """Vérifie le statut de l'association en cours"""
    state_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'rfid_state.json')
    
    if not os.path.exists(state_file):
        return jsonify({"status": "waiting"})
    
    try:
        with open(state_file, 'r') as f:
            data = json.load(f)
        
        mode = data.get('mode', 'NORMAL')
        
        if mode == 'SUCCESS':
            return jsonify({
                "status": "success",
                "mail": data.get('mail'),
                "uid": data.get('uid')
            })
        elif mode == 'ERROR':
            return jsonify({
                "status": "error",
                "message": data.get('message', 'Erreur inconnue')
            })
        elif mode == 'ASSOCIATION':
            # Vérifier le timeout
            timestamp = data.get('timestamp', 0)
            if time.time() - timestamp > 20:
                return jsonify({"status": "timeout"})
            return jsonify({"status": "waiting"})
        else:
            return jsonify({"status": "idle"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)})

@app.get("/status")
def status():
    state = read_state()
    # expose un statut simple (utile pour debug)
    return jsonify(state)

if __name__ == "__main__":
    # Sur le réseau de l'école: écouter sur toutes les interfaces
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)