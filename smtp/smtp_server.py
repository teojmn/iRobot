#Server SMTP pour envoi d'email via Brevo avec contenu HTML/CSS et phrase aléatoire depuis CSV

#Importations
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from pathlib import Path
from random import choice
from html import escape
import csv
from datetime import datetime, date, timedelta
import sys
import re
import os
from pathlib import Path

# Charge le .env si présent (dev uniquement)
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            if line.strip() and not line.startswith("#"):
                key, value = line.strip().split("=", 1)
                os.environ[key] = value

# Logging configuration (EN HAUT POUR QUE ÇA FONCTIONNE)
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("smtp_test")

#CONFIG SMTP BREVO     
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "9c33ff001@smtp-brevo.com"
SMTP_PASS = os.getenv("SMTP_PASS", "")

#CONFIG EMAIL     
FROM_EMAIL = "hdmi-locker@outlook.fr"

#Texte brut de secours
plain_text = (
    "Rappel : Rendre le câble HDMI\n\n"
    "Il faudrait que tu ramènes le câble HDMI.\n\n"
    "Il est demandé aux étudiants de rendre le câble HDMI emprunté en fin de journée afin de permettre à d'autres étudiants de l'utiliser.\n\n"
    "Ceci est un mail automatique envoyé par le HDMI Locker 3000"
)

#Chargement du fichier html (visuel du mail)
html_path = Path("template.html")
if html_path.exists():
    html_content = html_path.read_text(encoding="utf-8")
else:
    html_content = f"<pre>{plain_text}</pre>"

#Chargement des phrases aléatoires depuis le CSV
phrases_path = Path("../data/phrases_rappel.csv")
logger.debug("Recherche du fichier de phrases à %s", phrases_path)

try:
    if phrases_path.exists():
        with phrases_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            phrases = [row[0].strip() for row in reader if row]

        logger.debug("Found %d phrases", len(phrases))

        if phrases:
            # Échappe le HTML et convertit les retours à la ligne en <br>
            selected = escape(choice(phrases))
            selected = selected.replace('\n', '<br>')
            logger.debug("Phrase sélectionnée (après escape) : %s", selected)

            def _repl(m):
                return m.group(1) + selected + m.group(2)

            html_content = re.sub(
                r'(<span[^>]*id=["\']rappel-phrase["\'][^>]*>).*?(</span>)',
                _repl,
                html_content,
                flags=re.IGNORECASE | re.DOTALL
            )
    else:
        logger.warning("Fichier de phrases introuvable : %s", phrases_path)

except Exception as exc:
    logger.exception("Erreur en injectant la phrase aléatoire: %s", exc)

# Lecture du fichier d'emprunts pour déterminer les destinataires
emprunts_path = Path("../data/emprunts.csv")
recipients = set()
logger.debug("Recherche du fichier d'emprunts à %s", emprunts_path)

if emprunts_path.exists():
    try:
        with emprunts_path.open("r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            cutoff = datetime.now() - timedelta(days=1)  # il y a 24h
            for row in reader:
                mail = (row.get("mail") or "").strip()
                statut = (row.get("statut") or "").strip().upper()
                timestamp_str = (row.get("timestamp") or "").strip()
                if not mail:
                    logger.debug("Ligne ignorée sans adresse mail: %s", row)
                    continue
                if statut != "EN COURS":
                    logger.debug("Statut non 'EN COURS' pour %s: %s", mail, statut)
                    continue
                try:
                    row_datetime = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")
                except Exception:
                    logger.warning("Impossible de parser le timestamp '%s' pour %s, ligne ignorée", timestamp_str, mail)
                    continue
                if row_datetime <= cutoff:
                    recipients.add(mail)
                    logger.debug("Ajout du destinataire %s (emprunt du %s)", mail, row_datetime)
    except Exception as exc:
        logger.exception("Erreur en lisant %s: %s", emprunts_path, exc)
else:
    logger.warning("Fichier d'emprunts introuvable: %s", emprunts_path)

#Convertit en liste triée pour envoi, si vide -> quitter
recipients = sorted(recipients)
if not recipients:
    logger.info("Aucun destinataire à notifier aujourd'hui. Fin du script.")
    sys.exit(0)

#Prépare l'en-tête To avec la liste des destinataires
to_header = ", ".join(recipients)

message = MIMEMultipart("alternative")
message["Subject"] = "Rappel : merci de rendre le câble HDMI"
message["From"] = FROM_EMAIL
message["To"] = to_header

message.attach(MIMEText(plain_text, "plain", "utf-8"))
message.attach(MIMEText(html_content, "html", "utf-8"))

try:
    logger.debug("Initialisation du client SMTP vers %s:%s (délai d'attente=10s)", SMTP_SERVER, SMTP_PORT)
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=10) as server:
        logger.debug("Connecté au serveur SMTP, envoi de EHLO")
        server.ehlo()
        logger.debug("Démarrage de TLS...")
        server.starttls()
        server.ehlo()
        logger.debug("Tentative d'authentification en tant que %s", SMTP_USER)
        server.login(SMTP_USER, SMTP_PASS)
        logger.info("Authentification réussie")
        logger.debug("Envoi du message de %s à %s", FROM_EMAIL, recipients)
        result = server.sendmail(FROM_EMAIL, recipients, message.as_string())
        if result:
            logger.warning("sendmail a signalé des destinataires en échec : %s", result)
        else:
            logger.info("Email envoyé avec succès via Brevo !")
except smtplib.SMTPAuthenticationError as e:
    logger.exception("Échec de l'authentification : %s", e)
except smtplib.SMTPException as e:
    logger.exception("Erreur SMTP : %s", e)
except Exception as e:
    logger.exception("Erreur inattendue : %s", e)