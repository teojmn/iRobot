import pandas as pd
import os

class EmpruntManager:
    def __init__(self):
        self.csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'emprunts.csv')
        self.df = None
        self._load_emprunts()
    
    def _load_emprunts(self):
        """Charge les emprunts depuis le fichier CSV"""
        try:
            self.df = pd.read_csv(self.csv_path)
        except FileNotFoundError:
            print(f"Erreur: Le fichier {self.csv_path} n'existe pas")
            self.df = pd.DataFrame(columns=['mail', 'id_casier', 'timestamp', 'statut'])
    
    def _save_emprunts(self):
        """Sauvegarde les emprunts dans le fichier CSV"""
        if self.df is not None:
            self.df.to_csv(self.csv_path, index=False)
    
    def creer_emprunt(self, mail, id_casier, timestamp):
        """Ajoute un nouvel emprunt avec le statut EN COURS si l'utilisateur n'a pas déjà un emprunt"""
        if self.get_emprunt(mail):
            return False
        
        new_row = pd.DataFrame([{
            'mail': mail,
            'id_casier': id_casier,
            'timestamp': timestamp,
            'statut': 'EN COURS'
        }])
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self._save_emprunts()
        return True
    
    def cloturer_emprunt(self, mail, timestamp):
        """Met à jour la dernière ligne avec l'adresse mail en mettant le statut à TERMINE"""
        mask = (self.df['mail'] == mail) & (self.df['statut'] == 'EN COURS')
        emprunts_en_cours = self.df[mask]
        
        if not emprunts_en_cours.empty:
            dernier_index = emprunts_en_cours.index[-1]
            self.df.loc[dernier_index, 'timestamp'] = timestamp
            self.df.loc[dernier_index, 'statut'] = 'TERMINE'
            self._save_emprunts()
            return True
        return None
    
    def get_emprunt(self, mail):
        """Vérifie si l'utilisateur a un emprunt EN COURS"""
        mask = (self.df['mail'] == mail) & (self.df['statut'] == 'EN COURS')
        return mask.any()
    
    def get_casier_en_cours(self, mail):
        """Retourne l'id_casier de l'emprunt EN COURS pour ce mail, sinon None"""
        mask = (self.df['mail'] == mail) & (self.df['statut'] == 'EN COURS')
        emprunts_en_cours = self.df[mask]
        if not emprunts_en_cours.empty:
            return int(emprunts_en_cours.iloc[-1]['id_casier'])
        return None