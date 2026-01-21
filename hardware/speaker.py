import pygame
import time
import os

class Speaker:
    """Gère la lecture de sons via le haut-parleur USB"""
    
    def __init__(self, volume=0.5):
        """
        Initialise pygame mixer pour la lecture audio
        
        Args:
            volume: Volume de lecture (0.0 à 1.0, par défaut 0.5)
        """
        try:
            pygame.mixer.init()
            self.initialized = True
            self.set_volume(volume)
            print("✓ Haut-parleur initialisé")
        except Exception as e:
            print(f"⚠ Erreur d'initialisation du haut-parleur: {e}")
            self.initialized = False
    
    def set_volume(self, volume):
        """
        Ajuste le volume de lecture
        
        Args:
            volume: Valeur entre 0.0 (muet) et 1.0 (volume max)
        """
        if self.initialized:
            # Limiter le volume entre 0.0 et 1.0
            volume = max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(volume)
            print(f"🔊 Volume réglé à {int(volume * 100)}%")
    
    def play_sound(self, file_path, duration=None):
        """
        Joue un fichier audio
        
        Args:
            file_path: Chemin vers le fichier audio (MP3, WAV, OGG)
            duration: Durée de lecture en secondes (None = jusqu'à la fin)
        """
        if not self.initialized:
            print("⚠ Haut-parleur non initialisé")
            return
        
        try:
            if not os.path.exists(file_path):
                print(f"⚠ Fichier audio introuvable: {file_path}")
                return
            
            # Charger et jouer le son
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            print(f"🔊 Lecture de: {os.path.basename(file_path)}")
            
            # Attendre la durée spécifiée ou jusqu'à la fin
            if duration:
                time.sleep(duration)
                pygame.mixer.music.stop()
            else:
                # Attendre que la lecture soit terminée
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
                    
        except Exception as e:
            print(f"⚠ Erreur lors de la lecture: {e}")
    
    def stop(self):
        """Arrête la lecture en cours"""
        if self.initialized:
            pygame.mixer.music.stop()
    
    def cleanup(self):
        """Libère les ressources"""
        if self.initialized:
            pygame.mixer.quit()


if __name__ == "__main__":
    # Test du haut-parleur
    print("=== Test du haut-parleur ===")
    speaker = Speaker(volume=0.3)  # Volume à 30%
    
    # Chemin vers le fichier test
    audio_path = os.path.join(os.path.dirname(__file__), "..", "audio", "test.mp3")
    
    if os.path.exists(audio_path):
        print(f"Test avec: {audio_path}")
        speaker.play_sound(audio_path, duration=2)
        print("✓ Test terminé")
    else:
        print(f"⚠ Fichier de test non trouvé: {audio_path}")
    
    speaker.cleanup()
