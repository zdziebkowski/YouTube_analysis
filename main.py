import os
from googleapiclient.discovery import build


api_key = os.environ.get('YouTubeAPI')
youtube = build('youtube', 'v3', developerKey=api_key)
channel_id = 'UCHD-eeo8AnqR--UUn52FUTg'

request = youtube.channels().list(
    part='statistics',
    id=channel_id
)

response = request.execute()
print(response)


