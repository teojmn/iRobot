from RPLCD.i2c import CharLCD
import time
import threading

class LCDDisplay:
    def __init__(self):
        self.lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2)
        self.lcd.clear()
        self._default_mode = True
        self._stop_alternating = False
        self._alternating_thread = None
        self.start_alternating()
    
    def clear(self):
        """Efface l'écran"""
        self.lcd.clear()
    
    def write(self, line1="", line2=""):
        """Écrit sur les deux lignes (max 16 caractères par ligne)"""
        self.stop_alternating()
        self.lcd.clear()
        if line1:
            self.lcd.cursor_pos = (0, 0)
            self.lcd.write_string(line1[:16].center(16))
        if line2:
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string(line2[:16].center(16))
    
    def write_temporary(self, line1="", line2="", duration=3):
        """Affiche le message voulu puis revient au message par défaut"""
        self.write(line1, line2)
        time.sleep(duration)
        self.start_alternating()
    
    def _alternate_default_messages(self):
        """Alterne entre les deux messages par défaut"""
        while not self._stop_alternating:
            if self._default_mode:
                self.lcd.clear()
                self.lcd.cursor_pos = (0, 0)
                self.lcd.write_string("HDMI Locker".center(16))
                self.lcd.cursor_pos = (1, 0)
                self.lcd.write_string("3000".center(16))
                
            else:
                self.lcd.clear()
                self.lcd.cursor_pos = (0, 0)
                self.lcd.write_string("Passez votre".center(16))
                self.lcd.cursor_pos = (1, 0)
                self.lcd.write_string("carte".center(16))
                
            self._default_mode = not self._default_mode
            time.sleep(3)
    
    def start_alternating(self):
        """Démarre l'alternance des messages par défaut"""
        self.stop_alternating()
        self._stop_alternating = False
        self._alternating_thread = threading.Thread(target=self._alternate_default_messages, daemon=True)
        self._alternating_thread.start()
    
    def stop_alternating(self):
        """Arrête l'alternance des messages par défaut"""
        if self._alternating_thread and self._alternating_thread.is_alive():
            self._stop_alternating = True
            self._alternating_thread.join(timeout=0.5)
    
    def cleanup(self):
        """Nettoie les ressources"""
        self.stop_alternating()
        self.clear()
