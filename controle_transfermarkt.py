import pandas as pd

# Load the CSV files
goal_events = pd.read_csv('csv/goal_events.csv')
match_results = pd.read_csv('csv/match_results.csv')

# Group and count the goals in goal_events.csv by match_id and goal_team
goal_counts = goal_events.groupby(['match_id', 'goal_team']).size().reset_index(name='goals')

# Pivot the goal_counts DataFrame to have separate columns for each team's goals
pivot_goals = goal_counts.pivot(index='match_id', columns='goal_team', values='goals').fillna(0)

# Creating a mapping for team name standardization
team_name_mapping = {
    'Antwerp FC': 'R Antwerp FC',
    'Cercle': 'Cercle Brugge',
    'Club Brugge': 'Club Brugge',
    'Eupen': 'KAS Eupen',
    'FCB': 'Club Brugge',
    'Genk': 'KRC Genk',
    'Gent': 'KAA Gent',
    'KAA Gent': 'KAA Gent',
    'KAS Eupen': 'KAS Eupen',
    'KV Kortrijk': 'KV Kortrijk',
    'KV Mechelen': 'KV Mechelen',
    'KVC Westerlo': 'KVC Westerlo',
    'KVCWes': 'KVC Westerlo',
    'KVK': 'KV Kortrijk',
    'KVM': 'KV Mechelen',
    'OH Leuven': 'Oud-Heverlee Leuven',
    'OHL': 'Oud-Heverlee Leuven',
    'R Charleroi SC': 'R Charleroi SC',
    'RAFC': 'R Antwerp FC',
    'RCSC': 'R Charleroi SC',
    'RSC Anderlecht': 'RSC Anderlecht',
    'RSCA': 'RSC Anderlecht',
    'RUSG': 'Union Saint-Gilloise',
    'RWDM': 'RWD Molenbeek',
    'SL': 'Standard Luik',
    'STVV': 'Sint-Truidense VV',
    'St-Truidense VV': 'Sint-Truidense VV',
    'Standard Luik': 'Standard Luik',
    'Union SG': 'Union Saint-Gilloise'
}

# Aggregate the goals under standardized team names in pivot_goals
for original_name, standardized_name in team_name_mapping.items():
    if original_name in pivot_goals.columns:
        if standardized_name in pivot_goals.columns:
            pivot_goals[standardized_name] += pivot_goals[original_name]
        else:
            pivot_goals[standardized_name] = pivot_goals[original_name]
        pivot_goals.drop(columns=original_name, inplace=True)


# Function to calculate the total goals scored by a team in a match
def calculate_total_goals(row, team_type):
    team_name = row[team_type]
    if team_name in row:
        return row[team_name]
    else:
        return 0


# Merge the match_results with the pivot_goals and calculate total goals
merged_data = pd.merge(match_results, pivot_goals, left_on='match_id', right_index=True)
merged_data['total_home_goals'] = merged_data.apply(lambda x: calculate_total_goals(x, 'home_team'), axis=1)
merged_data['total_away_goals'] = merged_data.apply(lambda x: calculate_total_goals(x, 'away_team'), axis=1)

# Check for discrepancies
discrepancies = []
for index, row in merged_data.iterrows():
    if row['result_home_team'] != row['total_home_goals'] or row['result_away_team'] != row['total_away_goals']:
        discrepancies.append({
            'match_id': row['match_id'],
            'home_team': row['home_team'],
            'away_team': row['away_team'],
            'reported_result': f"{row['result_home_team']}-{row['result_away_team']}",
            'actual_result': f"{int(row['total_home_goals'])}-{int(row['total_away_goals'])}"
        })

# Display discrepancies
for discrepancy in discrepancies:
    print(f"Match ID {discrepancy['match_id']}: {discrepancy['home_team']} vs {discrepancy['away_team']}, "
          f"reported result is {discrepancy['reported_result']}, but analysis shows {discrepancy['actual_result']}.")
