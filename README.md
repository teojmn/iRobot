# iRobot - Smart HDMI Locker System

A Raspberry Pi-based locker management system for HDMI cables using RFID authentication, Arduino relay control, and automated email reminders.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Software Requirements](#software-requirements)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [Configuration](#configuration)
- [Data Management](#data-management)

## 🎯 Overview

The iRobot HDMI Locker System is an automated locker management solution designed for shared environments like schools or offices. Users can borrow and return HDMI cables by simply scanning their RFID card. The system tracks loans, controls physical lockers via Arduino relays, provides audio and visual feedback through speakers and LCD displays, and sends automated reminder emails to users who haven't returned their cables.

## ✨ Features

- **RFID Authentication**: Users authenticate using RFID cards (MFRC522 reader)
- **Automated Locker Control**: 15 lockers controlled via Arduino and relay modules
- **Loan Management**: Automatic tracking of cable loans and returns
- **LCD Display**: Real-time feedback on a 20x4 LCD screen
- **Audio Feedback**: Personalized audio messages for each locker
- **Email Reminders**: Automated SMTP server for sending reminder emails via Brevo
- **User Management**: CSV-based user database linking RFID cards to email addresses
- **State Tracking**: Real-time monitoring of locker availability (PLEIN/VIDE)

## 💻 Software Requirements

### Python Dependencies

```
pandas
pyserial
numpy
flask
spidev
mfrc522
lgpio
gpiozero
RPLCD
smbus2
pygame
```

Install with:
```bash
pip install -r requirements.txt
```

### System Requirements

- Python 3.7+
- GPIO access (Raspberry Pi OS)
- Arduino IDE (for programming the Arduino with relay control firmware)

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/teojmn/iRobot.git
   cd iRobot
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare data directory**
   ```bash
   mkdir -p data
   # Create required CSV files:
   # - data/users.csv (mail, uid, nom, prenom)
   # - data/casiers.csv (id_casier, etat)
   # - data/emprunts.csv (mail, id_casier, timestamp, statut)
   # - data/phrases_rappel.csv (phrases for reminder emails)
   ```

4. **Configure hardware connections**
   - Connect MFRC522 to Raspberry Pi SPI pins
   - Connect LCD to I2C bus
   - Connect Arduino to USB port
   - Connect speaker to audio output

5. **Upload Arduino firmware**
   - Program the Arduino to listen on serial and control relays

6. **Make scripts executable**
   ```bash
   chmod +x start.sh stop.sh
   ```

## 📁 Project Structure

```
iRobot/
├── main_rfid.py              # Main entry point (template)
├── config.py                 # Configuration file
├── requirements.txt          # Python dependencies
├── start.sh / stop.sh        # Service control scripts
│
├── hardware/                 # Hardware interface modules
│   ├── rfid_manager.py       # RFID reader logic & main system loop
│   ├── arduino_comm.py       # Serial communication with Arduino
│   ├── lcd_display.py        # LCD display control
│   ├── speaker.py            # Audio playback
│   └── test_rfid_simple.py   # RFID testing utility
│
├── models/                   # Data management
│   ├── user_manager.py       # User database (RFID ↔ email)
│   ├── emprunt_manager.py    # Loan tracking (EN COURS/TERMINE)
│   └── locker_manager.py     # Locker state (PLEIN/VIDE)
│
├── smtp/                     # Email notification system
│   ├── smtp_server.py        # Brevo SMTP sender with HTML templates
│   └── explication_cron.py   # Cron job setup documentation
│
├── audio/                    # Audio files for each locker
│   ├── audio_1.mp3
│   ├── audio_2.mp3
│   └── ...                   # (audio_1.mp3 to audio_15.mp3)
│
└── pres_api/                 # Presentation/API examples
    ├── api_casiers.js        # JavaScript API example
    └── trs.py                # API tests/demos
```

## 🚀 Usage

### Starting the System

```bash
./start.sh
```

### Basic Workflow

1. **Borrowing a Cable**
   - User scans RFID card
   - System checks if user is registered
   - System finds an available locker (PLEIN = cable inside)
   - Locker opens, user takes cable
   - Loan is created with status "EN COURS"
   - LCD displays confirmation
   - Audio message plays

2. **Returning a Cable**
   - User scans RFID card
   - System detects active loan
   - Opens the assigned locker
   - User returns cable
   - Loan status changes to "TERMINE"
   - Locker state returns to "PLEIN"

### Stopping the System

```bash
./stop.sh
```

## ⚙️ Configuration

### Serial Port Configuration

Edit `hardware/arduino_comm.py`:
```python
SERIAL_PORT = '/dev/ttyACM0'  # Adjust to your Arduino port
BAUD_RATE = 9600
```

### Locker Adjustments

The system supports 15 lockers (Arduino channels 0-14). Adjust `MAX_CHANNEL` in `hardware/arduino_comm.py` if needed.

## 💾 Data Management

### CSV Files Structure

**users.csv**
```csv
mail,uid,nom,prenom
user@example.com,123456789,Doe,John
```

**casiers.csv**
```csv
id_casier,etat
1,PLEIN
2,VIDE
```

**emprunts.csv**
```csv
mail,id_casier,timestamp,statut
user@example.com,1,2026-02-03 14:30:00,EN COURS
```

**phrases_rappel.csv**
```csv
"N'oublie pas de rendre ton câble HDMI !"
```

### State Logic

- **PLEIN**: Locker contains a cable (available for loan)
- **VIDE**: Locker is empty (cable currently loaned)
- **EN COURS**: Active loan
- **TERMINE**: Completed loan

## 📧 Email Reminders

The SMTP system can send automated reminders to users who haven't returned cables. Set up a cron job:

```bash
# Example: Send reminders every day at 18:00
0 18 * * * cd /path/to/iRobot/smtp && python3 smtp_server.py
```

See `smtp/explication_cron.py` for detailed cron setup instructions.

## 🔍 Testing

Test RFID functionality:
```bash
python3 hardware/test_rfid_simple.py
```

## 📝 Notes

- The system uses a cooldown mechanism to prevent duplicate reads (5 seconds by default)
- RFID UIDs are converted using SimpleMFRC522 format for compatibility
- Audio files must be named `audio_1.mp3` through `audio_15.mp3` matching locker IDs
- The LCD display supports 20 characters × 4 lines

## 🤝 Contributing

This is an educational project for locker management automation. Feel free to adapt it for your needs!

**Last Updated**: February 2026