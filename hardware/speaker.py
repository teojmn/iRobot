import os
os.environ["SDL_AUDIODRIVER"] = "alsa"

import pygame
import time
import subprocess

class Speaker:
    """Gère la lecture de sons via le haut-parleur USB"""
    
    def __init__(self, volume=0.5, system_volume=100):
        """Initialise pygame mixer pour la lecture audio"""

        self.initialized = False
        try:
            print("🔧 Nettoyage des verrous audio...")
            subprocess.run("sudo fuser -k /dev/snd/* 2>/dev/null", 
                         shell=True, capture_output=True, timeout=3)
            time.sleep(0.5)
            
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
            self.initialized = True
            self.set_volume(volume)
            self.set_system_volume(system_volume)
            print("✓ Haut-parleur initialisé")
            
        except Exception as e:
            print(f"⚠ Haut-parleur indisponible (mode silencieux activé)")
            print(f"   Détails: {e}")
            self.initialized = False
    
    def set_system_volume(self, volume):
        """Ajuste le volume système du Raspberry Pi"""

        if not self.initialized:
            return
            
        try:
            volume = max(0, min(100, volume))
            subprocess.run(['amixer', 'sset', 'PCM', f'{volume}%'], 
                         check=False, capture_output=True, timeout=2)
            print(f"🔊 Volume système réglé à {volume}%")
        except Exception:
            pass  # Ignore silencieusement les erreurs
    
    def set_volume(self, volume):
        """Ajuste le volume de lecture pygame"""
        
        if not self.initialized:
            return
            
        try:
            volume = max(0.0, min(1.0, volume))
            pygame.mixer.music.set_volume(volume)
            print(f"🔊 Volume pygame réglé à {int(volume * 100)}%")
        except Exception:
            pass
    
    def play_sound(self, file_path, duration=None):
        """Joue un fichier audio"""

        if not self.initialized:
            return
        
        try:
            if not os.path.exists(file_path):
                return
            
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            print(f"🔊 Lecture de: {os.path.basename(file_path)}")
            
            if duration:
                time.sleep(duration)
                pygame.mixer.music.stop()
                    
        except Exception as e:
            print(f"🔊 Erreur lecture audio (non critique): {e}")
    
    def stop(self):
        """Arrête la lecture en cours"""
        if self.initialized:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
    
    def cleanup(self):
        """Libère les ressources"""
        if self.initialized:
            try:
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                pygame.mixer.quit()
                self.initialized = False
                print("✓ Ressources audio libérées")
            except Exception as e:
                print(f"⚠ Erreur lors du nettoyage: {e}")

if __name__ == "__main__":
    print("=== Test du haut-parleur ===")
    speaker = Speaker(volume=1.0, system_volume=100)
    
    audio_path = os.path.join(os.path.dirname(__file__), "..", "audio", "test2.mp3")
    
    if os.path.exists(audio_path):
        print(f"Test avec: {audio_path}")
        speaker.play_sound(audio_path, duration=2)
        print("✓ Test terminé")
    else:
        print(f"⚠ Fichier de test non trouvé: {audio_path}")
    
    speaker.cleanup()