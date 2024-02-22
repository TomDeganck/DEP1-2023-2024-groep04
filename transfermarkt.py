import requests
from bs4 import BeautifulSoup

url = 'https://www.transfermarkt.be/jupiler-pro-league/spieltagtabelle/wettbewerb/BE1?saison_id=2021&spieltag=1'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

matches = soup.find_all('div', class_='match-row')  # You need to replace 'div' and 'match-row' with the correct tag and class

for match in matches:
    teams = match.find_all('span', class_='team-name')  # Again, replace with correct tag and class
    home_team = teams[0].get_text()
    away_team = teams[1].get_text()

    print(f"Thuisploeg: {home_team}, Uitploeg: {away_team}")

    # Extract other information like date, time, scores etc. in a similar way
