import pandas as pd
import isodate

channel_info = pd.read_csv('chanel_stats.csv')
video_info = pd.read_csv('video_stats.csv')

# videos data manipulation
video_info = video_info.drop(columns=['dislikes'])
video_info['description'] = video_info['description'].fillna('')
video_info['sponsor'] = video_info['description'].apply(lambda x: 'XTB' if 'XTB' in x else None)
video_info = video_info.drop(columns=['description'])
video_info['date'] = pd.to_datetime(video_info['date']).dt.date
video_info['duration'] = video_info['duration'].apply(lambda x: isodate.parse_duration(x).total_seconds())

# measures for videos
total_views = video_info['views'].sum()
average_views_per_video = video_info['views'].mean()
average_comments_per_video = video_info['comments'].mean()
engagement_rate = (video_info['likes'] + video_info['comments']).sum() / total_views
total_video_time = video_info['duration'].sum()
average_video_time = video_info['duration'].mean()
likes_to_comments_ratio = video_info['likes'].sum() / video_info['comments'].sum()

print(video_info.head())
print(video_info.tail())

print(f"Total views: {total_views}")
print(f"Average views per video: {average_views_per_video}")
print(f"Average comments per video: {average_comments_per_video}")
print(f"Engagement rate: {engagement_rate}")
print(f"Total video time (seconds): {total_video_time}")
print(f"Average video time (seconds): {average_video_time}")
print(f"Likes to comments ratio: {likes_to_comments_ratio}")