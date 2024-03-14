import re
from datetime import datetime

import pandas as pd
from dateutil import parser

import csv

import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import process

stamnummers_df = pd.read_csv('csv/stamnummers.csv')
stamnummers_df.columns = ['TeamName', 'TeamNumber']


def find_team_number_in_csv_fuzzy(team_name, csv_data):
    matched_rows = csv_data[csv_data['TeamName'].str.contains(team_name, case=False, na=False)]
    if not matched_rows.empty:
        return matched_rows.iloc[0]['TeamNumber']  # Retourneert het nummer van de eerste overeenkomstige rij
    return None


# Setup voor teamnamen
url = 'https://nl.wikipedia.org/wiki/Lijst_van_voetbalclubs_in_Belgi%C3%AB_naar_stamnummer'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

# Build een dict van alle teamnamen
counter = 0
team_dict = {}


def fuzzy_match_team_name(name, team_dict, threshold=85):
    match_fuzzy, score = process.extractOne(name, team_dict.keys())
    return team_dict[match_fuzzy] if score >= threshold else None


# loop en add alle namen
ol = soup.find('ol')
for li in ol.find_all('li'):
    counter += 1
    idx_name = li.text.find('(')
    team_name = li.text[:idx_name]
    team_dict[counter] = team_name

# Laatste element is irrelevant en geen teamnaam
team_dict.popitem()
# Een reverse dict voor gebruik later
reverse_team_dict = {name.strip(): num for num, name in team_dict.items()}

# Vars om bij te houden zodat ze altijd bestaan
seasons = []
matches = []
ranking_data = []
goals_data = []

# Dict die conversie van tijd mogelijk maakt
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

# Url van 1 pagina om de anderen op te kunnen bouwen
url = 'https://www.transfermarkt.be/jupiler-pro-league/spieltagtabelle/wettbewerb/BE1?saison_id=2021&spieltag=1'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
}

response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.content, 'html.parser')

wrong_names = set()

# Slaag alle seizoenen op adhv een pagine
for seasonObj in soup.find_all('div', class_='inline-select'):
    for season in seasonObj.find_all('option'):
        if int(season['value']) == 2020: #Bepaal welke seizoenen opgehaald moeten worden
            seasons.append(season['value'] if season else None)

# Loop over elk seizoen, eerste speeldag
for season in seasons:
    days = []
    url = f'https://www.transfermarkt.be/jupiler-pro-league/spieltagtabelle/wettbewerb/BE1/plus/?saison_id={season}&spieltag=1'
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    # Bouw nu per seizoen elke speeldag op zodat we elke seizoen en dag hebben
    for dayObj in soup.find_all('div', class_='inline-select'):
        for day in dayObj.find_all('option'):
            if int(day['value']) <= 50: #Bepaal hoeveel max dagen op te halen
                days.append(day['value'] if day else None)

    # Loop nu over elke dag
    for day in days:
        url = f'https://www.transfermarkt.be/jupiler-pro-league/spieltagtabelle/wettbewerb/BE1/plus/?saison_id={season}&spieltag={day}'
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        print(season, day)

        # Zoek de 2 nodige elementen om te bestuderen uit de pagina
        matches_table = soup.find('h1').find_next('table')
        rankings_table = soup.find('table', class_='items')

        last_date = None

        # Als de table niet bestaat, skip over de dag want er is niet gespeeld
        if matches_table.find_all('tr')[1:] is None:
            continue
        # Ga nu over elke match
        for row in matches_table.find_all('tr')[1:]:
            cols = row.find_all('td')
            if not cols:
                continue

            if cols[0].get_text(strip=True):
                last_date = cols[0].get_text(strip=True)
                last_date_recent = True
            elif cols[1].get_text(strip=True):
                last_date = last_date[:-5]

            # Slaag data op van de match
            if len(cols) >= 5:
                if cols[1].get_text(strip=True) != '':
                    time = cols[1].get_text(strip=True)
                home_team = cols[4].get_text(strip=True)
                away_team = cols[9].get_text(strip=True)
                result = cols[6].get_text(strip=True)
                match_id_tag = row.find('a', href=re.compile(r'/spielbericht/index/spielbericht/'))
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

                    # Zet date om in correct formaat
                    for dutch, english in month_mapping.items():
                        date_temp = date_temp.replace(dutch, english)
                    date = parser.parse(date_temp, dayfirst=True)
                    formatted_date = date.strftime("%Y/%m/%d")

                    time_obj = datetime.strptime(time, "%H:%M").time()

                    # Splits home team van de algemene string
                    home_team_string = home_team[idx_home + 1:].strip()
                    home_team_number = str(reverse_team_dict.get(home_team_string,
                                                                 fuzzy_match_team_name(home_team_string,
                                                                                       reverse_team_dict)))
                    if home_team_number == "None":
                        home_team_number = find_team_number_in_csv_fuzzy(home_team_string, stamnummers_df)

                    # Splits away team van de algemene string
                    away_team_string = away_team[:idx_away].strip()
                    away_team_number = str(reverse_team_dict.get(away_team_string,
                                                                 fuzzy_match_team_name(away_team_string,
                                                                                       reverse_team_dict)))
                    if away_team_number == "None":
                        away_team_number = find_team_number_in_csv_fuzzy(away_team_string, stamnummers_df)

                    # Add de match aan de array
                    matches.append(
                        {'seizoen': season, 'speeldag': day, 'datum': formatted_date, 'tijd': time_obj,
                         'id_match': extracted_id,
                         'thuisploeg_stamnummer': home_team_number, 'thuisploeg': home_team[idx_home + 1:],
                         'uitploeg_stamnummer': away_team_number, 'uitploeg': away_team[:idx_away],
                         'doelpunten_thuisploeg': result[:-2], 'doelpunten_uitploeg': result[2:],
                         })

        # Bouw de rankings op
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

            # Zet de naam om
            club_name_string = club_name.strip()
            if club_name_string in reverse_team_dict:
                club_number = str(reverse_team_dict[club_name_string])
            # Indien onze methode niet werkt, haal uit de stamnummers csv van lectoren
            else:
                club_number = find_team_number_in_csv_fuzzy(club_name_string, stamnummers_df)

            goals = goals.split(':')
            ranking_data.append({
                'seizoen': season,
                'speeldag': day,
                'stand': rank,
                'naam_ploeg': club_name,
                'id_ploeg': club_number,
                'aantal_wedstrijden': played,
                'aantal_gewonnen': wins,
                'aantal_gelijk': draws,
                'aantal_verloren': losses,
                'doelpunten_voor': goals[0],
                'doelpunten_tegen': goals[1],
                'verschil': goal_difference,
                'punten': points,
            })

        # Andere link voor de goals
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
        valid_goal = True
        match_id_tag = ''
        goal_team_home = True
        for table in div.find_all('table', style='border-top: 0 !important;'):
            # Loop over de goals rijen en bepaal welke info ze bevatten, slaag deze dan op
            for row in table.find_all('tr'):
                if 'class' in row.attrs and 'table-grosse-schrift' in row['class']:
                    home_team = row.find('td', class_='spieltagsansicht-vereinsname').get_text(strip=True)
                    away_team = row.find_all('td', class_='spieltagsansicht-vereinsname')[-1].get_text(strip=True)
                    idx_home = home_team.find(')')
                    idx_away = away_team.rfind('(')
                    home_team = home_team[idx_home + 1:]
                    away_team = away_team[:idx_away]
                    match_id_tag = row.find('a', href=re.compile(r'/spielbericht/index/spielbericht/'))
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
                        goal_team_home = False
                    except:
                        if row.find('td', class_='zentriert no-border-links'):
                            goal_time = row.find('td', class_='zentriert no-border-links').get_text(strip=True)
                            goal_team = home_team
                            goal_team_home = True
                    try:
                        result = row.find('td', class_='zentriert hauptlink').get_text(strip=True)
                    except:
                        # Rode/Gele kaart
                        result = result
                        valid_goal = False
                    idx_home = home_team.find(')')
                    idx_away = away_team.rfind('(')

                    time_obj = datetime.strptime(time, "%H:%M").time()

                    home_team_string = home_team.strip()
                    home_team_number = str(reverse_team_dict.get(home_team_string,
                                                                 fuzzy_match_team_name(home_team_string,
                                                                                       reverse_team_dict)))
                    # Haal uit CSV van lectoren voor de rest
                    if home_team_number == "None":
                        home_team_number = find_team_number_in_csv_fuzzy(home_team_string, stamnummers_df)

                    away_team_string = away_team.strip()
                    away_team_number = str(reverse_team_dict.get(away_team_string,
                                                                 fuzzy_match_team_name(away_team_string,
                                                                                       reverse_team_dict)))
                    if away_team_number == "None":
                        away_team_number = find_team_number_in_csv_fuzzy(away_team_string, stamnummers_df)
                    if goal_team_home:
                        goal_team_number = home_team_number
                    else:
                        goal_team_number = away_team_number

                    # Slaag data op
                    goals_data.append({
                        'seizoen': season,
                        'dag': day,
                        'datum': date,
                        'tijd': time_obj,
                        'id_match': extracted_id,
                        'thuisploeg_stamnummer': home_team_number,
                        'thuisploeg': home_team,
                        'uitploeg': away_team,
                        'uitploeg_stamnummer': away_team_number,
                        'goal_time': goal_time,
                        'goal_team_naam': goal_team,
                        'goal_team_stamnummer': goal_team_number,
                        'stand_thuis': result[:-2],
                        'stand_uit': result[2:],
                        'valid_goal': valid_goal,
                    })
                    valid_goal = True
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
# Slaag de info uit de arrays op in CSV bestanded
csv_file = "csv/wedstrijden_onverwerkd.csv"
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file,
                            fieldnames=['seizoen', 'speeldag', 'datum', 'tijd', 'id_match', 'thuisploeg_stamnummer',
                                        'thuisploeg', 'uitploeg_stamnummer', 'uitploeg', 'doelpunten_thuisploeg',
                                        'doelpunten_uitploeg'])
    writer.writeheader()
    for match in matches:
        writer.writerow(match)

csv_file = "csv/klassement_onverwerkd.csv"
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file,
                            fieldnames=['seizoen', 'speeldag', 'stand', 'naam_ploeg', 'id_ploeg', 'aantal_wedstrijden',
                                        'aantal_gewonnen', 'aantal_gelijk', 'aantal_verloren', 'doelpunten_voor',
                                        'doelpunten_tegen', 'verschil', 'punten'])
    writer.writeheader()
    for ranking in ranking_data:
        writer.writerow(ranking)

csv_file = "csv/doelpunten_onverwerkd.csv"
with open(csv_file, 'w', newline='', encoding='utf-8') as file:
    writer = csv.DictWriter(file, fieldnames=['seizoen', 'dag', 'datum', 'tijd', 'id_match', 'thuisploeg_stamnummer',
                                              'thuisploeg', 'uitploeg', 'uitploeg_stamnummer', 'goal_time',
                                              'goal_team_naam', 'goal_team_stamnummer', 'stand_thuis', 'stand_uit',
                                              'valid_goal'])
    writer.writeheader()
    for goals in goals_data:
        writer.writerow(goals)
