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
        # Vérifier si l'utilisateur a déjà un emprunt EN COURS
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

emprunt = EmpruntManager()

print("=== Test 1: Créer un emprunt ===")
result = emprunt.creer_emprunt("user1@example.com", 1, "2025-12-05 10:00:00")
print(f"Emprunt créé: {result}")

print("\n=== Test 2: Tentative de créer un second emprunt (devrait échouer) ===")
result = emprunt.creer_emprunt("user1@example.com", 2, "2025-12-05 11:00:00")
print(f"Second emprunt créé: {result}")

print("\n=== Test 3: Clôturer l'emprunt ===")
result = emprunt.cloturer_emprunt("user1@example.com", "2025-12-05 12:00:00")
print(f"Emprunt clôturé: {result}")

print("\n=== Test 4: Maintenant on peut créer un nouvel emprunt ===")
result = emprunt.creer_emprunt("user1@example.com", 2, "2025-12-05 13:00:00")
print(f"Nouvel emprunt créé: {result}")

print("\n=== Test 5: Clôturer un emprunt inexistant ===")
result = emprunt.cloturer_emprunt("user3@example.com", "2025-12-05 14:00:00")
print(f"Résultat clôture inexistante: {result}")

print("\n=== État final du DataFrame ===")
print(emprunt.df)