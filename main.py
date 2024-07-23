import os
from googleapiclient.discovery import build

api_key = os.environ.get('YouTubeAPI')
youtube = build('youtube', 'v3', developerKey=api_key)
channel_id = 'UCHD-eeo8AnqR--UUn52FUTg'


def get_channel_stats(youtube: any, channel_id: str) -> tuple:
    """
        Retrieve the title and statistics of a specified YouTube channel.

        Args:
            youtube (any): The YouTube API service object.
            channel_id (str): The ID of the YouTube channel to retrieve statistics for.

        Returns:
            tuple: A tuple containing:
                - str: The title of the YouTube channel.
                - dict: A dictionary of the channel's statistics, including:
                    - 'viewCount' (str): Total number of views.
                    - 'subscriberCount' (str): Total number of subscribers.
                    - 'hiddenSubscriberCount' (bool): Whether the subscriber count is hidden.
                    - 'videoCount' (str): Total number of videos.
        """
    request = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id
    )

    response = request.execute()
    return response['items'][0]['snippet']['title'], response['items'][0]['statistics']


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
    uploads_playlist_id = response['items'][0]
    #uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    return uploads_playlist_id


channel_stats = get_channel_stats(youtube, channel_id)
upload_playlist = get_uploads_playlist_id(youtube, channel_id)
print(channel_stats)
print(upload_playlist)
