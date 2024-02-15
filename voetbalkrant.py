import requests
from bs4 import BeautifulSoup

url = 'https://www.voetbalkrant.com/belgie/jupiler-pro-league/geschiedenis/2013-2014/wedstrijden'

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')
seasons = []
for seasonObj in soup.find_all('div', class_="float-right"):
    for season in seasonObj.find_all('option'):
        seasons.append(season.get_text(strip=True))

for season in seasons:
    season = season.replace(" ", "")
    url = f'https://www.voetbalkrant.com/belgie/jupiler-pro-league/geschiedenis/%7Bseason%7D/wedstrijden'
    response = requests.get(url)
    season_soup = BeautifulSoup(response.text, 'html.parser')

    for match in season_soup.find_all('tr', class_='table-active'):
        datetime = match.find('td', class_='text-center').text.strip()

        teams_home = match.find_all('td', class_='text-right')
        hometeam = teams_home[0].get_text(strip=True)
        teams_away = match.find_all('td', class_='text-left')
        awayteam = teams_away[0].get_text(strip=True)

        score = match.find('td', class_='text-center').text.strip()

        print(f"{season} {datetime}: {hometeam} {score} {awayteam}")