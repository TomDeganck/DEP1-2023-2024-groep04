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

for indx in goal_events_df.index:
    goal_time = goal_events_df.at[indx, 'goal_time'][:-1]
    if "+" in goal_time:
        times = goal_time.split("+")
        goal_events_df.at[indx, 'goal_time'] = str(sum(map(int, times)))
    else:
        goal_events_df.at[indx, 'goal_time'] = goal_time

# Convert 'goal_time' column to numeric
goal_events_df['goal_time'] = pd.to_numeric(goal_events_df['goal_time'])

# Create TimedeltaIndex
lijst_times = goal_events_df['time'] + pd.to_timedelta(goal_events_df['goal_time'], unit='m',)

goal_events_df['real_time_goal'] = lijst_times.astype(str).map(lambda x: x[7:])

goal_events_df.to_csv('csv/goal_events.csv', index=False)


goal_events_df = goal_events_df[goal_events_df['valid_goal'] == 1]

goal_events_df['home_team'] = goal_events_df['home_team'].map(team_name_mapping).fillna(goal_events_df['home_team'])
goal_events_df['away_team'] = goal_events_df['away_team'].map(team_name_mapping).fillna(goal_events_df['away_team'])

goals_home_team = goal_events_df[goal_events_df['goal_team'] == goal_events_df['home_team']].groupby('match_id').size()
goals_home_team_df = goals_home_team.reset_index(name='goals_home_team')
print(goals_home_team)

goals_away_team = goal_events_df[goal_events_df['goal_team'] == goal_events_df['away_team']].groupby('match_id').size()
goals_away_team_df = goals_away_team.reset_index(name='goals_away_team')

merged_df_home = pd.merge(match_results_df, goals_home_team_df, on='match_id', how='left')
merged_df_away = pd.merge(match_results_df, goals_away_team_df, on='match_id', how='left')

merged_df = pd.merge(merged_df_home, merged_df_away[['match_id', 'goals_away_team']], on='match_id', how='left')

discrepancies = merged_df[
    (merged_df['goals_home_team'] != merged_df['result_home_team']) |
    (merged_df['goals_away_team'] != merged_df['result_away_team'])
]

print("Discrepancies found:")
print(discrepancies)
