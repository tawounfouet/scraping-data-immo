# Scraper AvoVentes.fr

Ce projet est un script Python automatisé pour extraire toutes les données relatives aux biens immobiliers mis aux enchères sur [avoventes.fr](https://avoventes.fr/).

Il est conçu pour pouvoir être exécuté de manière régulière (par exemple via un `cron`) et pour extraire de façon détaillée (au format JSON) :
- Les informations du bien (Titre, adresse, tags)
- Les informations financières (Mise à prix, adjudication, surenchère...)
- Les dates (Vente, visites)
- La description détaillée
- L'historique des valeurs foncières de la DGFiP à proximité
- Les liens vers tous les documents associés
- Les informations concernant le cabinet d'avocats en charge

## Pré-requis

- Python 3.9+
- Les dépendances contenues dans `requirements.txt`
- Playwright installé (pour le scraping du rendu JavaScript)

## Installation

1. Cloner ou déplacer le dossier du projet à l'emplacement souhaité.
2. Créer un environnement virtuel :
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Installer les dépendances :
   ```bash
   pip install -r requirements.txt
   ```
4. Installer les navigateurs Playwright :
   ```bash
   playwright install chromium
   ```

## Exécution

Pour lancer le scraping, utilisez le script utilitaire fourni :
```bash
./run.sh
```

Le script va créer un dossier `output/` s'il n'existe pas et sauvegarder le résultat sous la forme `output/avoventes_YYYY-MM-DD.json`.

Si vous souhaitez le lancer manuellement ou tester sur un nombre limité d'annonces :
```bash
source venv/bin/activate
python scraper.py output.json
```

## Automatisation (Cron)

Pour exécuter ce script tous les lundis à 2h00 du matin, vous pouvez ajouter cette ligne à votre `crontab` (`crontab -e`) :
```text
0 2 * * 1 /chemin/vers/avoventes_scraper/run.sh >> /chemin/vers/avoventes_scraper/cron.log 2>&1
```
*(Remplacez `/chemin/vers/avoventes_scraper` par le chemin réel du projet).*
