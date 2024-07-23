import os
from googleapiclient.discovery import build
from typing import List, Dict
import pandas as pd

api_key = os.environ.get('YouTubeAPI')
youtube = build('youtube', 'v3', developerKey=api_key)
channel_id = 'UCHD-eeo8AnqR--UUn52FUTg'


def get_channel_stats(youtube: any, channel_id: str) -> Dict:
    """
        Retrieve the title and statistics of a specified YouTube channel.

        Args:
            youtube (any): The YouTube API service object.
            channel_id (str): The ID of the YouTube channel to retrieve statistics for.

        Dict: A dictionary containing channel statistics.
        """
    request = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id
    )

    response = request.execute()
    channel_info = response['items'][0]
    return {
        'title': channel_info['snippet']['title'],
        'subscriberCount': channel_info['statistics']['subscriberCount'],
        'viewCount': channel_info['statistics']['viewCount'],
        'videoCount': channel_info['statistics']['videoCount']
    }


def get_uploads_playlist_id(youtube: any, channel_id: str) -> str:
    """
    Retrieve the uploads playlist ID for a specified YouTube channel.

    Args:
        youtube (any): The YouTube API service object.
        channel_id (str): The ID of the YouTube channel.

    Returns:
        str: The uploads playlist ID.
    """
    request = youtube.channels().list(
        part='contentDetails',
        id=channel_id
    )
    response = request.execute()
    uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    return uploads_playlist_id


def get_videos_in_playlist(youtube: any, playlist_id: str) -> List[Dict]:
    """
    Retrieve all videos in a specified YouTube playlist.

    Args:
        youtube (any): The YouTube API service object.
        playlist_id (str): The ID of the playlist.

    Returns:
        List[Dict]: A list of video details dictionaries.
    """
    videos = []
    request = youtube.playlistItems().list(
        part='snippet',
        playlistId=playlist_id,
        maxResults=50
    )

    while request is not None:
        response = request.execute()
        videos += response['items']
        request = youtube.playlistItems().list_next(request, response)

    return videos


def get_video_details(youtube: any, video_ids: List[str]) -> List[Dict]:
    """
    Retrieve details for a list of YouTube video IDs.

    Args:
        youtube (any): The YouTube API service object.
        video_ids (List[str]): A list of YouTube video IDs.

    Returns:
        List[Dict]: A list of video details dictionaries.
    """
    details = []
    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
            part='snippet,contentDetails,statistics',
            id=','.join(video_ids[i:i+50])
        )
        response = request.execute()
        details += response['items']

    return details


def get_all_videos_and_details(youtube: any, channel_id: str) -> List[Dict]:
    """
    Retrieve all videos and their details from a specified YouTube channel.

    Args:
        youtube (any): The YouTube API service object.
        channel_id (str): The ID of the YouTube channel.

    Returns:
        List[Dict]: A list of video details dictionaries.
    """
    upload_playlist = get_uploads_playlist_id(youtube, channel_id)
    all_videos = get_videos_in_playlist(youtube, upload_playlist)
    video_ids = [video['snippet']['resourceId']['videoId'] for video in all_videos]
    video_details = get_video_details(youtube, video_ids)
    return video_details

channel_stats = get_channel_stats(youtube, channel_id)
video_details = get_all_videos_and_details(youtube, channel_id)

channel_info = pd.DataFrame([channel_stats], columns=['title', 'subscriberCount', 'viewCount', 'videoCount'])

video_data = []
for video in video_details:
    video_info = {
        'title': video['snippet']['title'],
        'date': video['snippet']['publishedAt'],
        'likes': video['statistics'].get('likeCount', 'N/A'),
        'dislikes': video['statistics'].get('dislikeCount', 'N/A'),  # Dislikes may not be available
        'comments': video['statistics'].get('commentCount', 'N/A'),
        'views': video['statistics'].get('viewCount', 'N/A'),
        'duration': video['contentDetails']['duration'],
        'description': video['snippet']['description']
    }
    video_data.append(video_info)

video_df = pd.DataFrame(video_data)

channel_info.to_csv('chanel_stats.csv', index=False)
video_df.to_csv('video_stats.csv', index=False)

print("Channel Stats DataFrame")
print(channel_info)
print("Video Details DataFrame")
print(video_df)