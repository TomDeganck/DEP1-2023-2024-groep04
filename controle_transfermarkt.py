import pandas as pd

# Load CSV files
match_results_df = pd.read_csv('csv/match_results.csv')
goal_events_df = pd.read_csv('csv/goal_events.csv')



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

goal_events_df = goal_events_df[goal_events_df['valid_goal'] == 1]

# Calculate goals for home and away teams
goals_home_team = goal_events_df[goal_events_df['goal_team'] == goal_events_df['home_team']].groupby('match_id').size()
goals_away_team = goal_events_df[goal_events_df['goal_team'] == goal_events_df['away_team']].groupby('match_id').size()

# Convert Series to DataFrame and reset index
goals_home_team_df = goals_home_team.reset_index(name='calculated_goals_home_team')
goals_away_team_df = goals_away_team.reset_index(name='calculated_goals_away_team')

# Replace NaN values in goal columns with 0
merged_df = pd.merge(match_results_df, goals_home_team_df, on='match_id', how='outer')
merged_df = pd.merge(merged_df, goals_away_team_df, on='match_id', how='outer')
merged_df['calculated_goals_home_team'] = merged_df['calculated_goals_home_team'].fillna(0)
merged_df['calculated_goals_away_team'] = merged_df['calculated_goals_away_team'].fillna(0)


# Calculate discrepancies
discrepancies = merged_df[
    (merged_df['calculated_goals_home_team'] != merged_df['result_home_team']) |
    (merged_df['calculated_goals_away_team'] != merged_df['result_away_team'])
]

# Select only relevant columns for display
discrepancies = discrepancies[['date', 'match_id', 'home_team', 'away_team', 'calculated_goals_home_team', 'result_home_team', 'calculated_goals_away_team', 'result_away_team']]
discrepancies.head()