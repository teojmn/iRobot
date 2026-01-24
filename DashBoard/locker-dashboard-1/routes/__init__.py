from flask import Blueprint, Flask

# Create a blueprint for the routes
main = Blueprint('main', __name__)

# Import the routes to register them with the blueprint
from .casiers import *
from .emprunts import *

def register_routes(app: Flask):
    """Enregistre toutes les routes de l'application"""
    app.register_blueprint(casiers_bp)
    app.register_blueprint(emprunts_bp)