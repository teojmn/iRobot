import pygame
import time
import os
import subprocess

class Speaker:
    """Gère la lecture de sons via le haut-parleur USB"""
    
    def __init__(self, volume=0.5, system_volume=100):
        """
        Initialise pygame mixer pour la lecture audio
        
        Args:
            volume: Volume de lecture pygame (0.0 à 1.0, par défaut 0.5)
            system_volume: Volume système (0 à 100, par défaut 100%)
        """
        self.initialized = False
        try:
            pygame.mixer.init()
            self.initialized = True
            self.set_volume(volume)
            self.set_system_volume(system_volume)
            print("✓ Haut-parleur initialisé")
        except Exception as e:
            print(f"⚠ Haut-parleur non disponible (le système continuera sans audio): {e}")
            self.initialized = False
    
    def set_system_volume(self, volume):
        """
        Ajuste le volume système du Raspberry Pi
        
        Args:
            volume: Valeur entre 0 et 100
        """
        if not self.initialized:
            return
        
        try:
            volume = max(0, min(100, volume))
            subprocess.run(['amixer', 'sset', 'PCM', f'{volume}%'], 
                         check=True, capture_output=True)
            print(f"🔊 Volume système réglé à {volume}%")
        except Exception as e:
            print(f"⚠ Volume système non ajusté: {e}")
    
    def set_volume(self, volume):
        """
        Ajuste le volume de lecture pygame
        
        Args:
            volume: Valeur entre 0.0 (muet) et 1.0 (volume max)
        """
        if not self.initialized:
            return
        
        try:
            volume = max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(volume)
            print(f"🔊 Volume pygame réglé à {int(volume * 100)}%")
        except Exception as e:
            print(f"⚠ Erreur lors du réglage du volume: {e}")
    
    def play_sound(self, file_path, duration=None):
        """
        Joue un fichier audio
        
        Args:
            file_path: Chemin vers le fichier audio (MP3, WAV, OGG)
            duration: Durée de lecture en secondes (None = jusqu'à la fin)
        """
        if not self.initialized:
            return  # Pas d'erreur, on ignore silencieusement
        
        try:
            if not os.path.exists(file_path):
                print(f"⚠ Fichier audio introuvable: {file_path}")
                return
            
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            print(f"🔊 Lecture de: {os.path.basename(file_path)}")
            
            if duration:
                time.sleep(duration)
                pygame.mixer.music.stop()
            else:
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"⚠ Lecture audio ignorée: {e}")
    
    def stop(self):
        """Arrête la lecture en cours"""
        if not self.initialized:
            return
        
        try:
            pygame.mixer.music.stop()
        except Exception as e:
            print(f"⚠ Erreur lors de l'arrêt: {e}")
    
    def cleanup(self):
        """Libère les ressources"""
        if not self.initialized:
            return
        
        try:
            pygame.mixer.quit()
        except Exception as e:
            print(f"⚠ Erreur lors du nettoyage: {e}")
