from flask import Blueprint, render_template, jsonify, request, redirect, url_for
import os
import csv

casiers_bp = Blueprint('casiers', __name__)

@casiers_bp.route('/')
@casiers_bp.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@casiers_bp.route('/compte')
def compte():
    return render_template('compte.html')

@casiers_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        # Logique pour traiter le formulaire de contact
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')
        # Ajouter votre logique ici (envoi email, sauvegarde, etc.)
        
        return redirect(url_for('casiers.contact'))
    
    return render_template('contact.html')

@casiers_bp.route('/le-projet')
def le_projet():
    return render_template('le_projet.html')

@casiers_bp.route('/api/casiers')
def get_casiers():
    casiers = []
    csv_path = os.path.join('data', 'casiers.csv')
    
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            casiers = list(reader)
    
    return jsonify(casiers)

@casiers_bp.route('/update-account', methods=['POST'])
def update_account():
    # Logique pour mettre à jour le compte
    # Récupérer les données du formulaire
    username = request.form.get('username')
    email = request.form.get('email')
    # Ajouter votre logique de mise à jour ici
    
    return redirect(url_for('casiers.compte'))