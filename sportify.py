import requests
import csv
import datetime

# URL en headers
url = 'https://api.sportify.bet/echo/v1/events?sport=voetbal&competition=belgium-first-division-a&_cached=true&key=market_type&lang=nl&bookmaker=bet777'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
}

def scrape_data(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Er is een fout opgetreden bij het ophalen van de gegevens.")
        return None

def process_data(data):
    if data is None:
        return []

    matches = []

    events = data.get('events', [])

    for event in events:
        event_name = event.get('name')
        starts_at = event.get('starts_at')
        home_team = event.get('home_team')
        away_team = event.get('away_team')
        total_goals = None
        both_teams_score = None
        match_winner = None

        markets = event.get('markets', [])
        for market in markets:
            market_name = market.get('name')
            if market_name == 'Match Winner':
                outcomes = market.get('outcomes', [])
                for outcome in outcomes:
                    outcome_name = outcome.get('name')
                    if outcome_name == home_team or outcome_name == away_team:
                        match_winner = outcome_name
            elif market_name == 'Totaal aantal goals':
                outcomes = market.get('outcomes', [])
                for outcome in outcomes:
                    outcome_name = outcome.get('name')
                    if outcome_name == 'Meer dan 2.5':
                        total_goals = outcome.get('display_odds', {}).get('decimal')
            elif market_name == 'Beide teams zullen scoren':
                outcomes = market.get('outcomes', [])
                for outcome in outcomes:
                    outcome_name = outcome.get('name')
                    if outcome_name == 'Ja':
                        both_teams_score = True

        matches.append({
            'Event Name': event_name,
            'Starts At': starts_at,
            'Home Team': home_team,
            'Away Team': away_team,
            'Total Goals': total_goals,
            'Both Teams Score': both_teams_score,
            'Match Winner': match_winner
        })

    return matches


def save_to_csv(matches):
    csv_file = "csv/match_results_live.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Event Name', 'Starts At', 'Home Team', 'Away Team', 'Total Goals', 'Both Teams Score', 'Match Winner'])
        writer.writeheader()
        for match in matches:
            writer.writerow(match)

    print(f"Data written to {csv_file}")


# Eenmalig scrape van historische gegevens
data = scrape_data(url, headers)
matches = process_data(data)
save_to_csv(matches)

""" 
import requests
import csv
import datetime

def scrape_data(url, headers):
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print("Er is een fout opgetreden bij het ophalen van de gegevens.")
        return None

def process_data(data):
    if data is None:
        return []

    matches = []

    competitions = data.get('tree', [])[0].get('competitions', [])

    for competition in competitions:
        events = competition.get('events', [])

        for event in events:
            event_name = event.get('name')
            starts_at = event.get('starts_at')
            home_team = event.get('home_team')
            away_team = event.get('away_team')
            total_goals = event.get('total_goals')
            both_teams_score = event.get('both_teams_score')
            match_winner = event.get('match_winner')

            markets = event.get('markets', [])
            for market in markets:
                market_name = market.get('name')
                if market_name in ['Match Winner', 'Totaal aantal goals', 'Beide teams zullen scoren']:
                    outcomes = market.get('outcomes', [])
                    for outcome in outcomes:
                        outcome_name = outcome.get('name')
                        odds = outcome.get('display_odds', {}).get('decimal')

                        matches.append({
                            'Totaal aantal goals': total_goals,
                            'Beide teams zullen scoren': both_teams_score,
                            'Match Winner': match_winner,
                        })
                        

    return matches


def save_to_csv(matches):
    csv_file = "csv/match_results_live.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=['Totaal aantal goals', 'Beide teams zullen scoren', 'Match Winner'])
        writer.writeheader()
        for match in matches:
            writer.writerow(match)

    print(f"Data written to {csv_file}")

# URL en headers
url = 'https://api.sportify.bet/echo/v1/events?sport=voetbal&competition=belgium-first-division-a&_cached=true&key=market_type&lang=nl&bookmaker=bet777'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
}

# Eenmalig scrape van historische gegevens
data = scrape_data(url, headers)
matches = process_data(data)
save_to_csv(matches) """

 



