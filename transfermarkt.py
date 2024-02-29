import re
from datetime import datetime

from dateutil import parser

import csv

import requests
from bs4 import BeautifulSoup

url = 'https://nl.wikipedia.org/wiki/Lijst_van_voetbalclubs_in_Belgi%C3%AB_naar_stamnummer'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

counter = 0
team_dict = {}

ol = soup.find('ol')
for li in ol.find_all('li'):
    counter += 1
    idx_name = li.text.find('(')
    team_name = li.text[:idx_name]
    team_dict[counter] = team_name

team_dict.popitem()
reverse_team_dict = {name.strip(): num for num, name in team_dict.items()}
print(team_dict)

seasons = []
matches = []
ranking_data = []
goals_data = []

month_mapping = {
    'jan.': 'Jan',
    'feb.': 'Feb',
    'mrt.': 'Mar',
    'apr.': 'Apr',
    'mei': 'May',
    'jun.': 'Jun',
    'jul.': 'Jul',
    'aug.': 'Aug',
    'sep.': 'Sep',
    'okt.': 'Oct',
    'nov.': 'Nov',
    'dec.': 'Dec'
}

url = 'https://www.transfermarkt.be/jupiler-pro-league/spieltagtabelle/wettbewerb/BE1?saison_id=2021&spieltag=1'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

wrong_names = set()

for seasonObj in soup.find_all('div', class_='inline-select'):
    for season in seasonObj.find_all('option'):
        if int(season['value']) >= 1960:
            seasons.append(season['value'] if season else None)

for season in seasons:
    days = []
    url = f'https://www.transfermarkt.be/jupiler-pro-league/spieltagtabelle/wettbewerb/BE1/plus/?saison_id={season}&spieltag=1'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    for dayObj in soup.find_all('div', class_='inline-select'):
        for day in dayObj.find_all('option'):
            if int(day['value']) <= 5:
                days.append(day['value'] if day else None)

    for day in days:
        url = f'https://www.transfermarkt.be/jupiler-pro-league/spieltagtabelle/wettbewerb/BE1/plus/?saison_id={season}&spieltag={day}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        matches_table = soup.find('h1').find_next('table')
        rankings_table = soup.find('table', class_='items')

        last_date = None

        if matches_table.find_all('tr')[1:] is None:
            continue
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
                match_id_tag = soup.find('a', href=re.compile(r'/spielbericht/index/spielbericht/'))
                if match_id_tag and match_id_tag['href']:
                    match_id = re.search(r'/spielbericht/index/spielbericht/(\d+)', match_id_tag['href'])
                    if match_id:
                        extracted_id = match_id.group(1)
                # for true last_date cut off first 2 char in CSV
                if result == time:
                    result = ''
                if last_date != '' and time != '':
                    idx_home = home_team.find(')')
                    idx_away = away_team.rfind('(')
                    date_temp = last_date[2:]

                    for dutch, english in month_mapping.items():
                        date_temp = date_temp.replace(dutch, english)
                    date = parser.parse(date_temp, dayfirst=True)
                    formatted_date = date.strftime("%Y/%m/%d")

                    time_obj = datetime.strptime(time, "%H:%M").time()

                    home_team_string = home_team[idx_home + 1:].strip()
                    if home_team_string in reverse_team_dict:
                        home_team_number = str(reverse_team_dict[home_team_string])
                    else:
                        home_team_number = home_team_string
                        wrong_names.add(home_team_number)

                    away_team_string = away_team[:idx_away].strip()
                    if away_team_string in reverse_team_dict:
                        away_team_number = str(reverse_team_dict[away_team_string])
                    else:
                        away_team_number = away_team_string
                        wrong_names.add(away_team_number)

                    matches.append(
                        {'date': formatted_date, 'time': time_obj, 'home_team': home_team[idx_home + 1:], 'home_team_number': home_team_number,
                         'result_home_team': result[:-2], 'result_away_team': result[2:],
                         'away_team': away_team[:idx_away], 'away_team_number': away_team_number,
                         'season': season,
                         'day': day,
                         'match_id': extracted_id})

        for row in rankings_table.find_all('tr')[1:]:
            cols = row.find_all('td')

            rank = cols[0].get_text(strip=True).split()[0]
            club_name = cols[2].get_text(strip=True)
            played = cols[3].get_text(strip=True)
            wins = cols[4].get_text(strip=True)
            draws = cols[5].get_text(strip=True)
            losses = cols[6].get_text(strip=True)
            goals = cols[7].get_text(strip=True)
            goal_difference = cols[8].get_text(strip=True)
            points = cols[9].get_text(strip=True)

            club_name_string = club_name.strip()
            if club_name_string in reverse_team_dict:
                club_number = str(reverse_team_dict[club_name_string])
            else:
                club_number = club_name_string
                wrong_names.add(club_name_string)

            ranking_data.append({
                'Rank': rank,
                'Club': club_name,
                'Club Number': club_number,
                'Played': played,
                'Wins': wins,
                'Draws': draws,
                'Losses': losses,
                'Goals': goals,
                'Goal Difference': goal_difference,
                'Points': points,
                'Season': season,
                'Day': day
            })

        url = f'https://www.transfermarkt.be/jupiler-pro-league/spieltag/wettbewerb/BE1/plus/?saison_id={season}&spieltag={day}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        div = soup.find('div', class_='large-8 columns')

        date = ''
        time = ''
        home_team = ''
        away_team = ''
        result = ''
        goal_team = ''
        goal_time = ''
        match_id_tag = ''
        for table in div.find_all('table', style='border-top: 0 !important;'):
            for row in table.find_all('tr'):
                if 'class' in row.attrs and 'table-grosse-schrift' in row['class']:
                    home_team = row.find('td', class_='spieltagsansicht-vereinsname').get_text(strip=True)
                    away_team = row.find_all('td', class_='spieltagsansicht-vereinsname')[-1].get_text(strip=True)
                    idx_home = home_team.find(')')
                    idx_away = away_team.rfind('(')
                    home_team = home_team[idx_home + 1:]
                    away_team = away_team[:idx_away]
                    match_id_tag = soup.find('a', href=re.compile(r'/spielbericht/index/spielbericht/'))
                    if match_id_tag and match_id_tag['href']:
                        match_id = re.search(r'/spielbericht/index/spielbericht/(\d+)', match_id_tag['href'])
                        if match_id:
                            extracted_id = match_id.group(1)
                elif 'class' in row.attrs and ('no-border' and 'spieltagsansicht-aktionen') in row['class']:
                    try:
                        tempTeamTest = row.find('td', class_='links no-border-links spieltagsansicht').get_text(
                            strip=True)
                        goal_time = row.find('td', class_='zentriert no-border-rechts').get_text(strip=True)
                        goal_team = away_team
                    except:
                        if row.find('td', class_='zentriert no-border-links'):
                            goal_time = row.find('td', class_='zentriert no-border-links').get_text(strip=True)
                            goal_team = home_team
                    try:
                        result = row.find('td', class_='zentriert hauptlink').get_text(strip=True)
                    except:
                        # Rode/Gele kaart
                        result = result
                    idx_home = home_team.find(')')
                    idx_away = away_team.rfind('(')

                    time_obj = datetime.strptime(time, "%H:%M").time()

                    home_team_string = home_team.strip()
                    if home_team_string in reverse_team_dict:
                        home_team_number = str(reverse_team_dict[home_team_string])
                    else:
                        home_team_number = home_team_string
                        wrong_names.add(home_team_number)

                    away_team_string = away_team.strip()
                    if away_team_string in reverse_team_dict:
                        away_team_number = str(reverse_team_dict[away_team_string])
                    else:
                        away_team_number = away_team_string
                        wrong_names.add(away_team_number)

                    goals_data.append({
                        'date': date,
                        'time': time_obj,
                        'home_team': home_team,
                        'home_team_number': home_team_number,
                        'away_team': away_team,
                        'away_team_number': away_team_number,
                        'goal_team': goal_team,
                        'goal_time': goal_time,
                        'result_home_team': result[:-2],
                        'result_away_team': result[2:],
                        'season': season,
                        'day': day,
                        'match_id': extracted_id
                    })
                elif 'class' not in row.attrs:
                    td_text = row.get_text(strip=True, separator=' ').replace('uur', '').strip()
                    if str(td_text).rfind(':') >= 1:
                        stringObj = td_text.split('-')
                        date_temp = stringObj[0]
                        dateObj = td_text.split(',')
                        unformated_date = dateObj[1][4:]
                        for dutch, english in month_mapping.items():
                            unformated_date = unformated_date.replace(dutch, english)
                        parsed_date = parser.parse(unformated_date, dayfirst=True)
                        date = parsed_date.strftime("%Y/%m/%d")
                        time = stringObj[1]
                        time = time[1:]
print("These names don't match any on record:")
print(wrong_names)
csv_file = "csv/match_results.csv"
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['date', 'time', 'home_team', 'home_team_number', 'result_home_team', 'result_away_team',
                                              'away_team', 'away_team_number', 'season', 'day', 'match_id'])
    writer.writeheader()
    for match in matches:
        writer.writerow(match)

csv_file = "csv/standings.csv"
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['Rank', 'Club', 'Club Number', 'Played', 'Wins', 'Draws',
                                              'Losses', 'Goals', 'Goal Difference', 'Points', 'Season', 'Day'])
    writer.writeheader()
    for ranking in ranking_data:
        writer.writerow(ranking)

csv_file = "csv/goal_events.csv"
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['date', 'time', 'home_team', 'home_team_number', 'away_team', 'away_team_number', 'goal_team',
                                              'goal_time', 'result_home_team', 'result_away_team', 'season', 'day',
                                              'match_id'])
    writer.writeheader()
    for goals in goals_data:
        writer.writerow(goals)
