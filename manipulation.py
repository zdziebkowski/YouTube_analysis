import pandas as pd
import isodate

channel_info = pd.read_csv('chanel_stats.csv')
video_info = pd.read_csv('video_stats.csv')

video_info = video_info.drop(columns=['dislikes'])
video_info['description'] = video_info['description'].fillna('')
video_info['sponsor'] = video_info['description'].apply(lambda x: 'XTB' if 'XTB' in x else None)
video_info = video_info.drop(columns=['description'])
video_info['date'] = pd.to_datetime(video_info['date']).dt.date
video_info['duration'] = video_info['duration'].apply(lambda x: isodate.parse_duration(x).total_seconds())

total_views = video_info['views'].sum()

print(video_info.head())
print(video_info.tail())
