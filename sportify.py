""" import requests

url = 'https://api.sportify.bet/echo/v1/events?sport=voetbal&competition=belgium-first-division-a&_cached=true&key=market_type&lang=nl&bookmaker=bet777'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
}

response = requests.get(url, headers=headers)
data = response.json()

competitions = data.get('tree', [])[0].get('competitions', [])

for competition in competitions:
    print(f"Competitie: {competition.get('name')}")

    events = competition.get('events', [])

    for event in events:
        event_id = event.get('id')
        event_name = event.get('name')
        starts_at = event.get('starts_at')
        home_team = event.get('home_team')
        away_team = event.get('away_team')
        print(f"    Event ID: {event_id}")
        print(f"    Naam: {event_name}")
        print(f"    Starttijd: {starts_at}")
        print(f"    Thuisploeg: {home_team}")
        print(f"    Uitploeg: {away_team}")
        

      
        markets = event.get('markets', [])
        for market in markets:
            market_name = market.get('name')
            print(f"        Markt: {market_name}")
            outcomes = market.get('outcomes', [])
            for outcome in outcomes:
                outcome_name = outcome.get('name')
                odds = outcome.get('display_odds', {}).get('decimal')
                print(f"            Uitkomst: {outcome_name}, Kansen: {odds}")

            print("    -----")
 """
import requests
import csv

url = 'https://api.sportify.bet/echo/v1/events?sport=voetbal&competition=belgium-first-division-a&_cached=true&key=market_type&lang=nl&bookmaker=bet777'

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
}

response = requests.get(url, headers=headers)
data = response.json()

all_match_results = []

for competition in data.get('tree', [])[0].get('competitions', []):
    events = competition.get('events', [])
    for event in events:
        event_id = event.get('id')
        event_name = event.get('name')
        starts_at = event.get('starts_at')
        home_team = event.get('home_team')
        away_team = event.get('away_team')
        match_result_url = event.get('url')

        match_result = {
            'Datum van de match': starts_at.split('T')[0],
            'Tijdstip van de match': starts_at.split('T')[1],
            'Naam Thuisploeg': home_team,
            'Resultaat Thuisploeg': None,  
            'Resultaat Uitploeg': None,  
            'Naam Uitploeg': away_team,
            'ID van de match': match_result_url.split('/')[-1]
        }

        markets = event.get('markets', [])
        for market in markets:
            outcomes = market.get('outcomes', [])
            for outcome in outcomes:
                outcome_name = outcome.get('name')
                if outcome_name == '1':
                    match_result['Resultaat Thuisploeg'] = outcome.get('display_odds', {}).get('decimal')
                elif outcome_name == '2':
                    match_result['Resultaat Uitploeg'] = outcome.get('display_odds', {}).get('decimal')

        all_match_results.append(match_result)


fieldnames = ['Datum van de match', 'Tijdstip van de match', 'Naam Thuisploeg', 'Resultaat Thuisploeg', 'Resultaat Uitploeg', 'Naam Uitploeg', 'ID van de match']
filename = 'match_results.csv'

with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_match_results)

print(f"Match results written to {filename}")
