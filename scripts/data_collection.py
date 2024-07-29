import logging
import os
from typing import List, Dict
import pandas as pd
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/youtube_api.log"),
        logging.StreamHandler()
    ]
)


def load_api_key() -> str:
    api_key = os.environ.get('YouTubeAPI')
    if not api_key:
        raise ValueError("YouTube API key not found in environment variables.")
    return api_key


def build_youtube_service(api_key: str) -> Resource:
    return build('youtube', 'v3', developerKey=api_key)


def get_channel_stats(youtube: Resource, channel_id: str) -> Dict[str, any]:
    """Retrieve the title and statistics of a specified YouTube channel."""
    try:
        request = youtube.channels().list(part='snippet,statistics', id=channel_id)
        response = request.execute()
        channel_info = response['items'][0]
        return {
            'title': channel_info['snippet']['title'],
            'subscriberCount': channel_info['statistics']['subscriberCount'],
            'viewCount': channel_info['statistics']['viewCount'],
            'videoCount': channel_info['statistics']['videoCount']
        }
    except HttpError as e:
        logging.error(f"An error occurred while fetching channel stats: {e}")
        return {}


def get_uploads_playlist_id(youtube: Resource, channel_id: str) -> str:
    """Retrieve the uploads playlist ID for a specified YouTube channel."""
    try:
        request = youtube.channels().list(part='contentDetails', id=channel_id)
        response = request.execute()
        uploads_playlist_id = response['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        return uploads_playlist_id
    except HttpError as e:
        logging.error(f"An error occurred while fetching uploads playlist ID: {e}")
        return ""


def get_videos_in_playlist(youtube: Resource, playlist_id: str) -> List[Dict]:
    """Retrieve all videos in a specified YouTube playlist."""
    videos = []
    request = youtube.playlistItems().list(part='snippet', playlistId=playlist_id, maxResults=50)
    while request is not None:
        try:
            response = request.execute()
            videos += response['items']
            request = youtube.playlistItems().list_next(request, response)
        except HttpError as e:
            logging.error(f"An error occurred while fetching videos in playlist: {e}")
            break
    return videos


def get_video_details(youtube: Resource, video_ids: List[str]) -> List[Dict]:
    """Retrieve details for a list of YouTube video IDs."""
    details = []
    for i in range(0, len(video_ids), 50):
        try:
            request = youtube.videos().list(part='snippet,contentDetails,statistics', id=','.join(video_ids[i:i + 50]))
            response = request.execute()
            details += response['items']
        except HttpError as e:
            logging.error(f"An error occurred while fetching video details: {e}")
            break
    return details


def get_all_videos_and_details(youtube: Resource, channel_id: str) -> List[Dict]:
    """Retrieve all videos and their details from a specified YouTube channel."""
    upload_playlist = get_uploads_playlist_id(youtube, channel_id)
    if not upload_playlist:
        return []
    all_videos = get_videos_in_playlist(youtube, upload_playlist)
    video_ids = [video['snippet']['resourceId']['videoId'] for video in all_videos]
    video_details = get_video_details(youtube, video_ids)
    return video_details


def save_data_to_csv(channel_stats: Dict[str, any], video_details: List[Dict], base_dir: str) -> None:
    """Save channel statistics and video details to CSV files."""
    channel_info = pd.DataFrame([channel_stats], columns=['title', 'subscriberCount', 'viewCount', 'videoCount'])
    video_data = [
        {
            'title': video['snippet']['title'],
            'date': video['snippet']['publishedAt'],
            'likes': int(video['statistics'].get('likeCount', 0)),
            'dislikes': int(video['statistics'].get('dislikeCount', 0)),  # Dislikes may not be available
            'comments': int(video['statistics'].get('commentCount', 0)),
            'views': int(video['statistics'].get('viewCount', 0)),
            'duration': video['contentDetails']['duration'],
            'description': video['snippet']['description']
        }
        for video in video_details
    ]
    video_df = pd.DataFrame(video_data)

    channel_info_path = os.path.join(base_dir, 'data', 'channel_stats.csv')
    video_stats_path = os.path.join(base_dir, 'data', 'video_stats.csv')

    channel_info.to_csv(channel_info_path, index=False)
    video_df.to_csv(video_stats_path, index=False)


def main():
    api_key = load_api_key()
    youtube = build_youtube_service(api_key)
    channel_id = 'UCHD-eeo8AnqR--UUn52FUTg'

    channel_stats = get_channel_stats(youtube, channel_id)
    video_details = get_all_videos_and_details(youtube, channel_id)

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_data_to_csv(channel_stats, video_details, base_dir)

    print("Channel Stats DataFrame")
    print(pd.read_csv(os.path.join(base_dir, 'data', 'channel_stats.csv')))
    print("Video Details DataFrame")
    print(pd.read_csv(os.path.join(base_dir, 'data', 'video_stats.csv')))


if __name__ == "__main__":
    main()
