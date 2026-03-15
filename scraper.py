import json
import sys
from playwright.sync_api import sync_playwright
from parser import parse_detail_page

def run_scraper(output_file="avoventes_data.json", max_items=None):
    all_data = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={'width': 1920, 'height': 1080}
        )
        page = context.new_page()

        print("Initialisation de la session sur la page d'accueil...")
        page.goto('https://avoventes.fr', wait_until="networkidle")

        print("Récupération de la liste des ventes aux enchères...")
        page.goto('https://avoventes.fr/ventes-aux-encheres?sort=date&order=asc&display=liste', wait_until="networkidle")

        print("Défilement pour charger tous les éléments...")
        last_count = 0
        retries = 0
        while retries < 5:
            links = page.locator('[data-link]').all()
            count = len(links)
            if count == last_count:
                retries += 1
            else:
                retries = 0
            last_count = count
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(1000)

        links = page.locator('[data-link]').all()
        hrefs = []
        for link in links:
            h = link.get_attribute('data-link')
            if h and '/enchere/' in h:
                hrefs.append(h)

        hrefs = list(set(hrefs)) # Déduplication
        print(f"Trouvé {len(hrefs)} annonces.")

        if max_items:
            hrefs = hrefs[:max_items]
            print(f"Limité à {max_items} annonces pour le test.")

        for i, url in enumerate(hrefs):
            print(f"[{i+1}/{len(hrefs)}] Scraping de : {url}")
            try:
                page.goto(url, wait_until="networkidle")
                page.wait_for_timeout(1000)
                html = page.content()
                data = parse_detail_page(html, url)
                all_data.append(data)
            except Exception as e:
                print(f"Erreur lors du scraping de {url}: {e}")

            # Sauvegarde incrémentale
            if (i + 1) % 10 == 0:
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(all_data, f, ensure_ascii=False, indent=2)

        browser.close()

    # Sauvegarde finale
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    print(f"Scraping terminé. {len(all_data)} biens sauvegardés dans {output_file}")

if __name__ == '__main__':
    output_path = sys.argv[1] if len(sys.argv) > 1 else "avoventes_data.json"
    run_scraper(output_path, max_items=2)
