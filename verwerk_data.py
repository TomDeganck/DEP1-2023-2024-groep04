
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

