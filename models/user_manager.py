import pandas as pd
import os
from datetime import datetime

class UserManager:
    def __init__(self):
        self.csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'utilisateurs.csv')
        self.df = None
        self._load_users()

    def _load_users(self):
        try:
            if os.path.exists(self.csv_path):
                self.df = pd.read_csv(self.csv_path, dtype={'uid': str})
            else:
                self.df = pd.DataFrame(columns=['uid', 'mail', 'date_inscription'])
                self.df.to_csv(self.csv_path, index=False)
        except Exception as e:
            print(f"Erreur chargement utilisateurs: {e}")
            self.df = pd.DataFrame(columns=['uid', 'mail', 'date_inscription'])

    def get_mail_by_uid(self, uid):
        uid = str(uid)
        user = self.df[self.df['uid'] == uid]
        if not user.empty:
            return user.iloc[0]['mail']
        return None

    def register_user(self, uid, mail):
        """Associe un UID à un mail s'ils ne sont pas déjà utilisés"""
        uid = str(uid)
        if uid in self.df['uid'].values or mail in self.df['mail'].values:
            return False
        
        new_user = pd.DataFrame([{
            'uid': uid,
            'mail': mail,
            'date_inscription': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }])
        self.df = pd.concat([self.df, new_user], ignore_index=True)
        self.df.to_csv(self.csv_path, index=False)
        return True