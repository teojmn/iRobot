import os
import json
import time
import re
from flask import Flask, request, render_template, redirect, url_for, flash, jsonify

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
STATE_FILE = os.path.join(DATA_DIR, "rfid_state.json")

ASSOCIATION_TIMEOUT_SECONDS = 20
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+\-]+@(epitech\.eu|epitech\.digital)$", re.IGNORECASE)

app = Flask(__name__)
app.secret_key = "change-me-in-prod"


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
    if request.method == "GET":
        return render_template("register.html", timeout=ASSOCIATION_TIMEOUT_SECONDS)

    # POST
    raw_email = (request.form.get("email") or "").strip().lower()
    local = (request.form.get("local") or "").strip().lower()
    domain = (request.form.get("domain") or "").strip().lower()

    if raw_email:
        email = raw_email
    elif local and domain:
        email = f"{local}@{domain}"
    else:
        email = ""

    if not is_valid_email(email):
        flash("Email invalide. Utilise @epitech.eu ou @epitech.digital", "error")
        return redirect(url_for("register"))

    # Ecrit une demande d'association que rfid_manager va consommer
    write_state({
        "mode": "ASSOCIATION",
        "mail": email,
        "timestamp": time.time()
    })

    # Page qui attend et poll /status
    return render_template("wait_for_card.html", email=email)


@app.get("/status")
def check_status():
    """
    Renvoie un statut simple pour la page wait_for_card.html:
    - waiting / success / error / timeout / idle
    """
    state = read_state()
    mode = state.get("mode", "NORMAL")

    if mode == "SUCCESS":
        return jsonify({
            "status": "success",
            "mail": state.get("mail"),
            "uid": state.get("uid")
        })

    if mode == "ERROR":
        return jsonify({
            "status": "error",
            "message": state.get("message", "Erreur inconnue")
        })

    if mode == "ASSOCIATION":
        ts = state.get("timestamp", 0)
        if time.time() - ts > ASSOCIATION_TIMEOUT_SECONDS:
            return jsonify({"status": "timeout"})
        return jsonify({"status": "waiting"})

    return jsonify({"status": "idle"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)