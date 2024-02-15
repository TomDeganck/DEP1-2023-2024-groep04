import requests

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
        print("    -----")
