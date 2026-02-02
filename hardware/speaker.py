import os
# FORCE le driver ALSA avant toute chose
os.environ["SDL_AUDIODRIVER"] = "alsa"

import pygame
import time
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
            # DÉBLOCAGE FORCÉ : Libère les devices audio potentiellement verrouillés
            print("🔧 Nettoyage des verrous audio...")
            subprocess.run("sudo fuser -k /dev/snd/* 2>/dev/null", 
                         shell=True, capture_output=True, timeout=3)
            time.sleep(0.5)  # Petite pause pour laisser le device se libérer
            
            # Initialisation de pygame
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            
            self.initialized = True
            self.set_volume(volume)
            self.set_system_volume(system_volume)
            print("✓ Haut-parleur initialisé")
            
        except Exception as e:
            # MODE FAIL-SAFE : On ne crash pas, on désactive juste le son
            print(f"⚠ Haut-parleur indisponible (mode silencieux activé)")
            print(f"   Détails: {e}")
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
                         check=False, capture_output=True, timeout=2)
            print(f"🔊 Volume système réglé à {volume}%")
        except Exception:
            pass  # Ignore silencieusement les erreurs
    
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
        except Exception:
            pass
    
    def play_sound(self, file_path, duration=None):
        """
        Joue un fichier audio
        
        Args:
            file_path: Chemin vers le fichier audio (MP3, WAV, OGG)
            duration: Durée de lecture en secondes (None = lecture complète non bloquante)
        """
        # Si pas initialisé, on sort immédiatement sans erreur
        if not self.initialized:
            return
        
        try:
            if not os.path.exists(file_path):
                return
            
            # Charger et jouer le son
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            print(f"🔊 Lecture de: {os.path.basename(file_path)}")
            
            # Si une durée est spécifiée, on attend puis on coupe
            if duration:
                time.sleep(duration)
                pygame.mixer.music.stop()
            # Sinon on laisse jouer en arrière-plan (non bloquant)
                    
        except Exception as e:
            print(f"🔊 Erreur lecture audio (non critique): {e}")
            # On ne raise pas pour ne pas casser l'appelant
    
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
    # Test du haut-parleur
    print("=== Test du haut-parleur ===")
    speaker = Speaker(volume=1.0, system_volume=100)
    
    # Chemin vers le fichier test
    audio_path = os.path.join(os.path.dirname(__file__), "..", "audio", "test2.mp3")
    
    if os.path.exists(audio_path):
        print(f"Test avec: {audio_path}")
        speaker.play_sound(audio_path, duration=2)
        print("✓ Test terminé")
    else:
        print(f"⚠ Fichier de test non trouvé: {audio_path}")
    
    speaker.cleanup()