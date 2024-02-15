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
    url = 'https://www.voetbalkrant.com/belgie/jupiler-pro-league/geschiedenis/' + str(season) + '/wedstrijden'
    response = requests.get(url)

    # Zoeken naar elke rij met wedstrijdgegevens
    for match in soup.find_all('tr', class_='table-active'):
        # Tijd en datum van de wedstrijd
        datetime = match.find('td', class_='text-center').text.strip()

        # Teams
        teams_home = match.find_all('td', class_='text-right')
        home_team = teams_home[0].get_text(strip=True)
        teams_away = match.find_all('td', class_='text-left')
        away_team = teams_away[0].get_text(strip=True)

        # Score
        score = match.find('a', style='background: #fff;padding:6px;white-space: nowrap;', ).get_text(strip=True)

        print(f"{season} {datetime}: {home_team} {score} {away_team}")