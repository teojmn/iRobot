from RPLCD.i2c import CharLCD
import time

lcd = CharLCD(i2c_expander='PCF8574', address=0x27, port=1, cols=16, rows=2)

def scroll_text(text, line=1, delay=0.2):
    padding = ' ' * 16
    text = padding + text + padding
    
    for i in range(len(text) - 15):
        # Effacer proprement la ligne complète
        lcd.cursor_pos = (line - 1, 0)
        lcd.write_string(' ' * 16)

        # Récrire le segment voulu
        lcd.cursor_pos = (line - 1, 0)
        lcd.write_string(text[i:i+16])
        time.sleep(delay)

scroll_text("Bienvenue sur mon Raspberry Pi 4 avec ecran LCD I2C!", line=1, delay=0.15)