import smtplib
from email.mime.text import MIMEText

# === CONFIG SMTP BREVO ===
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "987b65001@smtp-brevo.com"
SMTP_PASS = "QCrcdKvU1fLJbG94"

# === CONFIG EMAIL ===
FROM_EMAIL = "test.teo@outlook.fr"       # doit être une adresse validée dans Brevo
TO_EMAIL = "loan.lucmau@epitech.digital"            # destinataire test (tu peux mettre n’importe quel email réel)

msg = MIMEText(
    "Bonjour 👋\n\nCeci est un email de test envoyé depuis la borne HDMI via Brevo.\n\n"
    "En prod, ce message sera utilisé pour rappeler à l’utilisateur de rendre le câble."
)
msg["Subject"] = "🔔 Rappel : merci de rendre le câble HDMI"
msg["From"] = FROM_EMAIL
msg["To"] = TO_EMAIL

try:
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # sécuriser la connexion
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(FROM_EMAIL, [TO_EMAIL], msg.as_string())
        print("✅ Email envoyé avec succès via Brevo !")
except Exception as e:
    print("❌ Erreur:", e)