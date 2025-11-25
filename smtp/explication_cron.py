# Éxécution quotidienne à 08:55 (méthode simple et robuste : cron)
#
# 1) Principe
#    - Utiliser cron pour lancer le script chaque jour à 08:55.
#    - Le script doit être appelé depuis son répertoire pour que ./data/emprunts.csv soit trouvé.
#
# 2) Entrée crontab recommandée (à ajouter via `crontab -e`)
#    55 8 * * * cd /[chemin vers le dossier du script] && /usr/bin/env python3 [nom du fichier].py >/dev/null 2>&1
#
#    - cd ... : garantit le bon répertoire de travail.
#    - /usr/bin/env python3 : utilise l'interpréteur système.
#    - >/dev/null 2>&1 : supprime toute sortie (pas de fichier de logs).
#
# 3) Commandes utiles
#    - Éditer la crontab : crontab -e
#    - Tester manuellement : 
#         cd [chemin vers le dossier du script]
#         /usr/bin/env python3 [nom du fichier].py
#    - Vérifier le démon cron (Ubuntu) :
#         sudo systemctl status cron.service
#       ou (ancienne méthode) :
#         sudo service cron status
#    - Voir les entrées cron dans les logs (debug si nécessaire) :
#         sudo grep CRON /var/log/syslog
#         journalctl -u cron --since "1 hour ago"
#
# 4) Remarques / bonnes pratiques
#    - Utiliser chemins absolus dans le script si tu préfères éviter le `cd`.
#    - Pour debug temporaire, supprimer la redirection `>/dev/null 2>&1` pour voir la sortie/erreurs.
#    - Les identifiants SMTP restent dans le script : pour plus de sécurité, tu peux migrer vers des variables d'environnement plus tard.