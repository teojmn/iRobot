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
        """Récupère l'id_casier du premier casier disponible"""
        casiers_libres = self.df[self.df['etat'].str.upper() == 'VIDE']
        if not casiers_libres.empty:
            return casiers_libres.iloc[0]['id_casier']
        return None
    
    
    def get_premier_plein(self):
        """Récupère l'id_casier du premier casier disponible"""
        casiers_pleins = self.df[self.df['etat'].str.upper() == 'PLEIN']
        if not casiers_pleins.empty:
            return casiers_pleins.iloc[0]['id_casier']
        return None
    
    def casier_vide(self, id_casier):
        """Met l'état du casier sur VIDE"""
        mask = self.df['id_casier'] == id_casier
        if mask.any():
            self.df.loc[mask, 'etat'] = 'VIDE'
            self._save_casiers()
            return True
        return False
    
    def casier_plein(self, id_casier):
        """Met l'état du casier sur PLEIN"""
        mask = self.df['id_casier'] == id_casier
        if mask.any():
            self.df.loc[mask, 'etat'] = 'PLEIN'
            self._save_casiers()
            return True
        return False
    
"""locker = LockerManager()

test_id = locker.get_premier_libre()
print(f"Premier casier libre: {test_id}")

test_plein = locker.casier_plein(test_id)
print(f"Casier {test_id} mis à PLEIN: {test_plein}")

test_id = locker.get_premier_plein()
print(f"Premier casier plein: {test_id}")

test_vide = locker.casier_vide(1)
print(f"Casier 1 mis à VIDE: {test_vide}")"""