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
    df['sponsor'] = df['description'].apply(lambda x: 'XTB' if 'XTB' in x else 'No sponsor')
    # drop description column after processing
    df = df.drop(columns=['description'])
    # convert date to datetime and extract date only
    df['date'] = pd.to_datetime(df['date']).dt.date
    # convert duration from ISO8601 to seconds
    df['duration'] = df['duration'].apply(lambda x: isodate.parse_duration(x).total_seconds())
    # create cumulative views column
    df = df.sort_values(by='date')
    df['cumulative_views'] = df['views'].cumsum()
    df['cumulative_views_XTB'] = df.apply(lambda row: row['views'] if row['sponsor'] == 'XTB' else 0, axis=1).cumsum()
    df['cumulative_views_No_sponsor'] = df.apply(lambda row: row['views'] if row['sponsor'] == 'No sponsor' else 0,
                                                 axis=1).cumsum()

    # fill the cumulative columns to ensure they do not reset to zero
    df['cumulative_views_XTB'] = df['cumulative_views_XTB'].replace(0, pd.NA).ffill().fillna(0).infer_objects(
        copy=False)
    df['cumulative_views_No_sponsor'] = df['cumulative_views_No_sponsor'].replace(0, pd.NA).ffill().fillna(
        0).infer_objects(copy=False)

    # add and ID column
    df['ID'] = range(1, len(df) + 1)
    # add ID to title
    df['title'] = df['ID'].astype(str) + '. ' + df['title']
    return df


def save_data(df: pd.DataFrame, file_path: str) -> None:
    """
    Save DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame to be saved.
        file_path (str): Path to the CSV file (can be a file name or an absolute path).
    """
    df.to_csv(file_path, index=False)


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    video_stats_path = os.path.join(base_dir, 'data', 'video_stats.csv')

    video_info = load_data(video_stats_path)
    video_info = process_data(video_info)

    processed_video_stats_path = os.path.join(base_dir, 'data', 'processed_video_stats.csv')
    save_data(video_info, processed_video_stats_path)
