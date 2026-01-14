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

@app.route("/register", methods=["GET", "POST"])
def register():
    ensure_state_file()

    if request.method == "POST":
        email = (request.form.get("email") or "").strip()

        if not is_valid_email(email):
            flash("Email invalide. Utilise uniquement @epitech.eu ou @epitech.digital.", "error")
            return render_template("register.html", timeout=ASSOCIATION_TIMEOUT_SECONDS)

        # Option : empêcher de lancer une association si une autre est déjà en cours
        state = read_state()
        if state.get("mode") == "ASSOCIATION":
            # si association trop vieille -> on écrase
            ts = state.get("timestamp", 0)
            if time.time() - ts < ASSOCIATION_TIMEOUT_SECONDS:
                flash("Une association est déjà en cours. Réessaie dans quelques secondes.", "error")
                return render_template("register.html", timeout=ASSOCIATION_TIMEOUT_SECONDS)

        write_state({
            "mode": "ASSOCIATION",
            "mail": email,
            "timestamp": time.time(),
            "expires_at": time.time() + ASSOCIATION_TIMEOUT_SECONDS,
            "requested_at": datetime.now().isoformat(timespec="seconds"),
        })

        return render_template("wait_for_card.html", email=email, timeout=ASSOCIATION_TIMEOUT_SECONDS)

    return render_template("register.html", timeout=ASSOCIATION_TIMEOUT_SECONDS)

@app.get("/status")
def status():
    state = read_state()
    # expose un statut simple (utile pour debug)
    return jsonify(state)

if __name__ == "__main__":
    # Sur le réseau de l'école: écouter sur toutes les interfaces
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)