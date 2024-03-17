import pandas as pd

def process_goal_time(x):
    if pd.isna(x) or x == '':
        return 0
    try:
        # Remove any trailing single quotes and split
        parts = map(int, x.replace("'", "").split("+"))
        return sum(parts)
    except ValueError:
        print(f"Invalid format found: {x}")
        return 0

goal_events_df = pd.read_csv('csv/doelpunten_onverwerkd.csv')

# Process 'goal_time'
goal_events_df['goal_time'] = goal_events_df['goal_time'].apply(process_goal_time)

# Check the result
print(goal_events_df['goal_time'].value_counts())

# Convert 'goal_time' column to numeric
goal_events_df['goal_time'] = pd.to_numeric(goal_events_df['goal_time'])
goal_events_df['tijd'] = pd.to_datetime(goal_events_df['tijd'])
goal_events_df['goal_time'] = goal_events_df['goal_time'].astype(int)
goal_events_df['real_time_goal'] = goal_events_df['tijd'] + pd.to_timedelta(goal_events_df['goal_time'], unit='m')

# Insert 'real_time_goal' right after 'goal_time' column
goal_events_df.insert(goal_events_df.columns.get_loc('goal_time') + 1, 'real_time_goal', goal_events_df.pop('real_time_goal'))

# Further processing
goal_events_df['real_time_goal'] = goal_events_df['real_time_goal'].astype(str).map(lambda x: x.split()[1])
goal_events_df['tijd'] = goal_events_df['tijd'].map(lambda x: x.strftime("%H:%M:%S"))

# Filter and save the data
df = goal_events_df[goal_events_df.goal_time > 160]

goal_events_df.to_csv('csv/doelpunten_onverwerkd.csv', index=False)
df.to_csv('csv/doelpunten_onverwerkd_fout.csv', index=False)
