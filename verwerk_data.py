import datetime
import pandas as pd

goal_events_df = pd.read_csv('csv/doelpunten_onverwerkd.csv')

goal_events_df['goal_time'] = goal_events_df['goal_time'].map(lambda x: x[:-1])
goal_events_df['goal_time'] = goal_events_df['goal_time'].map(lambda x: x.split("+")).map(lambda x:str(sum(map(int, x))))

# Convert 'goal_time' column to numeric
goal_events_df['goal_time'] = pd.to_numeric(goal_events_df['goal_time'])
goal_events_df['tijd'] = pd.to_datetime(goal_events_df['tijd'])
goal_events_df['goal_time'] = goal_events_df['goal_time'].astype(int)
goal_events_df['real_time_goal'] = goal_events_df['tijd'] + pd.to_timedelta(goal_events_df['goal_time'], unit='m')
# Plaats 'real_time_goal' direct na 'goal_time' kolom
goal_events_df.insert(goal_events_df.columns.get_loc('goal_time') + 1, 'real_time_goal', goal_events_df.pop('real_time_goal'))

# Verdere verwerkingen
goal_events_df['real_time_goal'] = goal_events_df['real_time_goal'].astype(str).map(lambda x: x.split()[1])
goal_events_df['tijd'] = goal_events_df['tijd'].map(lambda x: x.strftime("%H:%M:%S"))

# Filter en sla de data op
df = goal_events_df[goal_events_df.goal_time > 120]

goal_events_df.to_csv('csv/doelpunten_onverwerkd.csv', index=False)
df.to_csv('csv/doelpunten_onverwerkd_fout.csv',index=False)
