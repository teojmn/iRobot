from pathlib import Path
import csv
from flask import Flask, render_template, redirect, url_for

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

app = Flask(__name__)

def load_casiers():
    casiers = []
    csv_path = DATA_DIR / "casiers.csv"
    if not csv_path.exists():
        return casiers
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            etat = (row.get("etat") or "").strip()
            numero = row.get("id_casier") or row.get("numero") or ""
            statut = "disponible" if etat.upper() == "PLEIN" else "occupe"
            casiers.append({"numero": numero, "etat": etat or "N/A", "statut": statut})
    return casiers

def load_emprunts():
    emprunts = []
    csv_path = DATA_DIR / "emprunts.csv"
    if not csv_path.exists():
        return emprunts
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, 1):
            statut = (row.get("statut") or "N/A").strip()
            emprunts.append({
                "id": idx,
                "casier_id": row.get("id_casier", "N/A"),
                "utilisateur": row.get("mail", "N/A"),
                "date_debut": row.get("timestamp", "N/A"),
                "statut": statut
            })
    return emprunts

def build_stats(casiers):
    total = len(casiers)
    disponibles = sum(1 for c in casiers if c["statut"] == "disponible")
    occupes = total - disponibles
    return {"total": total, "disponibles": disponibles, "occupes": occupes}

@app.route("/")
def index():
    return redirect(url_for("dashboard"))

@app.route("/dashboard")
def dashboard():
    casiers = load_casiers()
    emprunts = load_emprunts()
    stats = build_stats(casiers)
    recent_emprunts = list(reversed(emprunts[-10:]))  # 10 derniers
    return render_template("dashboard.html", casiers=casiers, stats=stats, emprunts=recent_emprunts)

@app.route("/le-projet")
def le_projet():
    return render_template("le_projet.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5010)