import datetime
import pandas as pd

goal_events_df = pd.read_csv('csv/goal_events.csv')

goal_events_df['goal_time'] = goal_events_df['goal_time'].map(lambda x: x[:-1])
goal_events_df['goal_time'] = goal_events_df['goal_time'].map(lambda x: x.split("+")).map(lambda x:str(sum(map(int, x))))

# Convert 'goal_time' column to numeric
goal_events_df['goal_time'] = pd.to_numeric(goal_events_df['goal_time'])
goal_events_df['time'] = pd.to_datetime(goal_events_df['time'])
goal_events_df['goal_time'] = goal_events_df['goal_time'].astype(int)
goal_events_df['real_time_goal'] = goal_events_df['time'] + pd.to_timedelta(goal_events_df['goal_time'], unit='m')
goal_events_df['real_time_goal'] = goal_events_df['real_time_goal'].astype(str).map(lambda x: x.split()[1])

goal_events_df['time'] = goal_events_df['time'].map(lambda x: x.strftime("%H:%M:%S"))

df = pd.DataFrame()
df = goal_events_df[goal_events_df.goal_time > 315]

goal_events_df.to_csv('csv/goal_events_verwerkt.csv', index=False)
df.to_csv('csv/goal_events_verwerkt_fout.csv',index=False)
