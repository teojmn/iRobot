from flask import Blueprint, render_template, jsonify
import os
import csv

casiers_bp = Blueprint('casiers', __name__)

@casiers_bp.route('/')
@casiers_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@casiers_bp.route('/le-projet')
def le_projet():
    return render_template('le_projet.html')

@casiers_bp.route('/data/casiers')
def get_casiers():
    casiers = []
    csv_path = os.path.join('data', 'casiers.csv')
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                casiers.append({
                    'id': row['id_casier'],
                    'numero': row['id_casier'],
                    'etat': row['etat'],
                    'statut': 'disponible' if row['etat'].upper() == 'PLEIN' else 'occupe'
                })
    
    return jsonify(casiers)