from bs4 import BeautifulSoup
import re
import datetime

def parse_detail_page(html, url):
    """
    Extrait les données d'une page de détail immobilier avoventes.fr.
    """
    soup = BeautifulSoup(html, 'html.parser')
    data = {'url': url, 'date_scraping': datetime.datetime.now().isoformat()}

    # 1. Titre
    title_elem = soup.find('h1')
    data['title'] = title_elem.text.strip() if title_elem else ""
    if not data['title']:
        # Fallback pour le titre
        h1 = soup.select_one('.text-32') or soup.select_one('.text-24')
        if h1:
            data['title'] = h1.text.strip()

    # 2. Types de bien / Tags (Maison, Vente aux enchères...)
    badges = soup.select('.badge')
    data['tags'] = [b.text.strip() for b in badges]

    # 3. Adresse
    data['address'] = None
    addr_divs = soup.select('div.inline-block')
    for div in addr_divs:
        if 'France' in div.text:
            data['address'] = div.text.strip()
            break

    # 4. Détails financiers (Mise à prix, frais...)
    details = {
        'mise_a_prix': None,
        'frais_prealables': None,
        'surenchere': None,
        'adjudication': None,
        'date_vente': None,
        'visites': None
    }
    info_container = soup.select_one('.bg-light.border.rounded-xl')
    if info_container:
        text_nodes = [t for t in info_container.stripped_strings]
        for i, t in enumerate(text_nodes):
            if 'Mise à prix' in t:
                details['mise_a_prix'] = text_nodes[i+1] if i+1 < len(text_nodes) else None
            elif 'Frais' in t:
                details['frais_prealables'] = text_nodes[i+1] if i+1 < len(text_nodes) else None
            elif 'Surenchère' in t:
                details['surenchere'] = text_nodes[i+1] if i+1 < len(text_nodes) else None
            elif 'Adjudication' in t:
                details['adjudication'] = text_nodes[i+1] if i+1 < len(text_nodes) else None

    # Dates
    vente_h2 = soup.find(lambda tag: tag.name == 'h2' and 'Vente' in tag.text)
    if vente_h2:
        date_vente = vente_h2.find_next_sibling('div')
        if date_vente:
            details['date_vente'] = date_vente.text.strip()

    visites_elem = soup.find(lambda tag: tag.name == 'div' and 'VISITES :' in tag.text)
    if visites_elem:
        details['visites'] = visites_elem.text.replace('VISITES :', '').strip()

    data['details'] = details

    # 5. Description détaillée (À propos du bien)
    about_h2 = soup.find(lambda tag: tag.name == 'h2' and 'À propos du bien' in tag.text)
    if about_h2:
        about_div = about_h2.find_next_sibling('div')
        data['description'] = about_div.text.strip() if about_div else None
    else:
        # Fallback pour la description si structure différente
        text_justify = soup.select_one('.text-justify')
        if text_justify:
            data['description'] = text_justify.text.strip()

    # 6. Données des valeurs foncières
    foncier_table = soup.find('table')
    valeurs_foncieres = []
    if foncier_table:
        headers = [th.text.strip() for th in foncier_table.find_all('th')]
        for row in foncier_table.find_all('tr')[1:]:
            cells = [td.text.strip() for td in row.find_all('td')]
            if len(cells) == len(headers):
                valeurs_foncieres.append(dict(zip(headers, cells)))
    data['valeurs_foncieres'] = valeurs_foncieres

    # 7. Documents (Récupération des liens)
    doc_links = soup.select('a[href*="/public/uploads/"]')
    docs = []
    for d in doc_links:
        # On peut avoir des liens identiques plusieurs fois dans le DOM, on évite les doublons simples
        doc_url = d['href']
        if not doc_url.startswith('http'):
            doc_url = 'https://avoventes.fr' + doc_url

        docs.append({
            'name': d.text.strip(),
            'url': doc_url
        })
    # Remove duplicates from docs based on url
    unique_docs = {v['url']:v for v in docs}.values()
    data['documents'] = list(unique_docs)

    # 8. Cabinet (Avocat poursuivant)
    cabinet = {
        'nom': None,
        'telephone': None,
        'email': None,
        'site': None,
        'adresse': None
    }
    tel_elem = soup.find(string=re.compile(r'Tél\s*:'))
    if tel_elem:
        cabinet['telephone'] = tel_elem.parent.text.replace('Tél. :', '').replace('Tél. :', '').strip()
        container = tel_elem.find_parent('div', class_=re.compile(r'bg-white'))
        if container:
            name = container.find(['h2', 'h3'])
            if name: cabinet['nom'] = name.text.strip()
            addr = container.find('div', class_='text-16')
            if addr: cabinet['adresse'] = addr.text.strip()

            email_elem = container.find(string=re.compile(r'Email\s*:'))
            if email_elem:
                cabinet['email'] = email_elem.parent.text.replace('Email. :', '').strip()

            site_elem = container.find(string=re.compile(r'Site\s*:'))
            if site_elem:
                cabinet['site'] = site_elem.parent.text.replace('Site. :', '').strip()

    data['cabinet'] = cabinet

    return data

if __name__ == '__main__':
    # Test unitaire rapide si lancé seul
    pass
