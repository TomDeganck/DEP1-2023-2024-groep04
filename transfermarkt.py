import requests
from bs4 import BeautifulSoup

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

    if cols[0].get_text(strip=True):
        last_date = cols[0].get_text(strip=True)
    else:
        last_date = last_date[:-5]

    if len(cols) >= 10:
        time = cols[1].get_text(strip=True)
        home_team = cols[4].get_text(strip=True)
        away_team = cols[9].get_text(strip=True)
        result = cols[6].get_text(strip=True)
        matches.append({'date': last_date, 'time': time, 'home_team': home_team, 'away_team': away_team, 'result': result})

for match in matches:
    print(match)
