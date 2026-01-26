from flask import Blueprint, jsonify
import os
import csv

emprunts_bp = Blueprint('emprunts', __name__)

@emprunts_bp.route('/data/emprunts')
def get_emprunts():
    emprunts = []
    csv_path = os.path.join('data', 'emprunts.csv')
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for idx, row in enumerate(reader, 1):
                emprunts.append({
                    'id': idx,
                    'casier_id': row.get('id_casier', 'N/A'),
                    'utilisateur': row.get('mail', 'N/A'),
                    'date_debut': row.get('timestamp', 'N/A'),
                    'date_fin': 'En cours' if row.get('statut', '').upper() == 'EN COURS' else row.get('timestamp', 'N/A'),
                    'statut': row.get('statut', 'N/A')
                })
    
    return jsonify(emprunts)