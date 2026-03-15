#!/bin/bash
# Script utilitaire pour lancer le scraper AvoVentes

# Se positionner dans le répertoire du script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Activer l'environnement virtuel si présent
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "L'environnement virtuel n'existe pas. Veuillez lancer 'pip install -r requirements.txt' dans un venv."
    # Pas de exit 1 pour bash_session
fi

# Créer le répertoire de sortie
mkdir -p output

# Nom de fichier basé sur la date pour l'historisation (si exécution régulière)
DATE=$(date +"%Y-%m-%d")
OUTPUT_FILE="output/avoventes_$DATE.json"

echo "Démarrage du scraping à destination de $OUTPUT_FILE..."
python scraper.py "$OUTPUT_FILE"

echo "Scraping terminé. Les données sont dans le dossier output/."
