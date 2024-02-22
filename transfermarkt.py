import requests
from bs4 import BeautifulSoup
import re

url = 'https://www.transfermarkt.be/jupiler-pro-league/spieltagtabelle/wettbewerb/BE1?saison_id=2021&spieltag=1'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

matches_table = soup.find('h1').find_next('table')
matches = []

last_date = None

for row in matches_table.find_all('tr')[1:]:
    cols = row.find_all('td')
    if not cols:
        continue

    date_text = cols[0].get_text(strip=True)
    if date_text:
        date_parts = date_text.split(' ')
        last_date = ' '.join(date_parts[:2])
        time = date_parts[2] if len(date_parts) > 2 else ''
        if re.match(r'\d{4}', time):
            year = time[:4]
            time = time[4:]
            last_date += ' ' + year

    if len(cols) >= 10:
        home_team = cols[4].get_text(strip=True)
        away_team = cols[9].get_text(strip=True)
        result = cols[6].get_text(strip=True)
        matches.append({'date': last_date, 'time': time, 'home_team': home_team, 'away_team': away_team, 'result': result})

for match in matches:
    print(match)
