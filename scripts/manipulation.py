import isodate
import pandas as pd
import os


def load_data(file_path: str) -> pd.DataFrame:
    """
    Load data from a CSV file into a DataFrame.

    Args:
        file_path (str): Path to the CSV file (can be a file name or an absolute path).

    Returns:
        pd.DataFrame: DataFrame containing the data from the CSV file.
    """
    try:
        return pd.read_csv(file_path)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise


def process_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Process data to clean and add necessary columns.

    Args:
        df (pd.DataFrame): DataFrame containing statistics.

    Returns:
        pd.DataFrame: Processed DataFrame with additional columns and cleaned data.
    """
    # drop unnecessary columns
    df = df.drop(columns=['dislikes'])
    # fill missing values in description to add sponsor column
    df['description'] = df['description'].fillna('')
    df['sponsor'] = df['description'].apply(lambda x: 'XTB' if 'XTB' in x else None)
    # drop description column after processing
    df = df.drop(columns=['description'])
    # convert date to datetime and extract date only
    df['date'] = pd.to_datetime(df['date']).dt.date
    # convert duration from ISO8601 to seconds
    df['duration'] = df['duration'].apply(lambda x: isodate.parse_duration(x).total_seconds())
    # create cumulative views column
    df = df.sort_values(by='date').assign(cumulative_views=df['views'].cumsum())

    return df


def calculate_total_views(df: pd.DataFrame) -> int:
    return df['views'].sum()


def calculate_average_views_per_video(df: pd.DataFrame) -> float:
    return df['views'].mean()


def calculate_average_comments_per_video(df: pd.DataFrame) -> float:
    return df['comments'].mean()


def calculate_engagement_rate(df: pd.DataFrame) -> float:
    total_views = df['views'].sum()
    if total_views == 0:
        return 0.0
    return (df['likes'] + df['comments']).sum() / total_views


def calculate_total_video_time(df: pd.DataFrame) -> float:
    return df['duration'].sum()


def calculate_average_video_time(df: pd.DataFrame) -> float:
    return df['duration'].mean()


def calculate_likes_to_comments_ratio(df: pd.DataFrame) -> float:
    total_comments = df['comments'].sum()
    if total_comments == 0:
        return 0.0
    return df['likes'].sum() / total_comments


def calculate_all_metrics(df: pd.DataFrame) -> None:
    """
    Calculate and print all metrics.

    Args:
        df (pd.DataFrame): DataFrame containing processed statistics.
    """
    total_views = calculate_total_views(df)
    average_views_per_video = calculate_average_views_per_video(df)
    average_comments_per_video = calculate_average_comments_per_video(df)
    engagement_rate = calculate_engagement_rate(df)
    total_video_time = calculate_total_video_time(df)
    average_video_time = calculate_average_video_time(df)
    likes_to_comments_ratio = calculate_likes_to_comments_ratio(df)

    print(f"\nTotal views: {total_views}")
    print(f"Average views per video: {average_views_per_video:.2f}")
    print(f"Average comments per video: {average_comments_per_video:.2f}")
    print(f"Engagement rate: {engagement_rate:.4f}")
    print(f"Total video time (seconds): {total_video_time}")
    print(f"Average video time (seconds): {average_video_time:.2f}")
    print(f"Likes to comments ratio: {likes_to_comments_ratio:.2f}")


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    channel_stats_path = os.path.join(base_dir, 'data', 'channel_stats.csv')
    video_stats_path = os.path.join(base_dir, 'data', 'video_stats.csv')
    channel_info = load_data(channel_stats_path)
    video_info = load_data(video_stats_path)
    video_info = process_data(video_info)
    calculate_all_metrics(video_info)
