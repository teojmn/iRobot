import pandas as pd
import os

class LockerManager:
    def __init__(self):
        self.csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'casiers.csv')
        self.df = None
        self._load_casiers()
    
    def _load_casiers(self):
        """Charge les casiers depuis le fichier CSV"""
        try:
            self.df = pd.read_csv(self.csv_path)
        except FileNotFoundError:
            print(f"Erreur: Le fichier {self.csv_path} n'existe pas")
            self.df = pd.DataFrame()
    
    def _save_casiers(self):
        """Sauvegarde les casiers dans le fichier CSV"""
        if self.df is not None and not self.df.empty:
            self.df.to_csv(self.csv_path, index=False)
    
    def get_premier_libre(self):
        """
        Récupère le premier casier DISPONIBLE pour un emprunt.
        → DISPONIBLE = PLEIN (un câble est présent)
        """
        casiers_disponibles = self.df[self.df['etat'].str.upper() == 'PLEIN']
        if not casiers_disponibles.empty:
            return casiers_disponibles.iloc[0]['id_casier']
        return None
    
    def get_premier_plein(self):
        """Alias, laissé si ton code l'utilise ailleurs"""
        return self.get_premier_libre()
    
    def casier_vide(self, id_casier):
        """
        Un utilisateur REND un câble ⇒ casier devient VIDE
        """
        mask = self.df['id_casier'] == id_casier
        if mask.any():
            self.df.loc[mask, 'etat'] = 'VIDE'
            self._save_casiers()
            return True
        return False
    
    def casier_plein(self, id_casier):
        """
        Un utilisateur PREND un câble ⇒ casier devient PLEIN ou VIDE ?
        Nouvelle logique : un casier plein signifie "câble présent"
        Donc quand un étudiant PREND un câble → il n'y en a plus → VIDE.
        """
        mask = self.df['id_casier'] == id_casier
        if mask.any():
            self.df.loc[mask, 'etat'] = 'PLEIN'
            self._save_casiers()
            return True
        return False