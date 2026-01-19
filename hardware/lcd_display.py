from RPLCD.i2c import CharLCD
import time

class LCDDisplay:
    def __init__(self):
        self.lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2)
        self.lcd.clear()
    
    def clear(self):
        """Efface l'écran"""
        self.lcd.clear()
    
    def write(self, line1="", line2=""):
        """Écrit sur les deux lignes (max 16 caractères par ligne)"""
        self.lcd.clear()
        if line1:
            self.lcd.cursor_pos = (0, 0)
            self.lcd.write_string(line1[:16].center(16))
        if line2:
            self.lcd.cursor_pos = (1, 0)
            self.lcd.write_string(line2[:16].center(16))
    
    def write_temporary(self, line1="", line2="", duration=3):
        """Affiche un message temporaire puis revient à l'écran d'accueil"""
        self.write(line1, line2)
        time.sleep(duration)
        self.write("Scannez votre", "carte")