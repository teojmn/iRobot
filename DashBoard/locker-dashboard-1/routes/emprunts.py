from flask import Blueprint, render_template, jsonify, request
import os
import csv
from models.emprunt import Emprunt

emprunts_bp = Blueprint('emprunts', __name__)

@emprunts_bp.route('/api/emprunts')
def get_emprunts():
    emprunts = []
    csv_path = os.path.join('data', 'emprunts.csv')
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            emprunts = list(reader)
    
    return jsonify(emprunts)

@emprunts_bp.route('/emprunts', methods=['GET'])
def list_emprunts():
    # Logic to list all emprunts
    emprunts = Emprunt.query.all()  # Assuming you have a query method
    return jsonify([emprunt.to_dict() for emprunt in emprunts])

@emprunts_bp.route('/emprunts', methods=['POST'])
def create_emprunt():
    # Logic to create a new emprunt
    data = request.get_json()
    new_emprunt = Emprunt(**data)  # Assuming the Emprunt model accepts data as keyword arguments
    new_emprunt.save()  # Assuming you have a save method
    return jsonify(new_emprunt.to_dict()), 201

@emprunts_bp.route('/emprunts/<int:emprunt_id>', methods=['GET'])
def get_emprunt(emprunt_id):
    # Logic to get a specific emprunt by ID
    emprunt = Emprunt.query.get_or_404(emprunt_id)  # Assuming you have a query method
    return jsonify(emprunt.to_dict())