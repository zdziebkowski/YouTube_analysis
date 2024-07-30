import logging
import os

import isodate
import pandas as pd

import config

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/data_processing.log"),
        logging.StreamHandler()
    ]
)


def check_read_permissions(file_path: str) -> None:
    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"Read permission denied for file {file_path}")


def check_write_permissions(file_path: str) -> None:
    dir_name = os.path.dirname(file_path)
    if not os.access(dir_name, os.W_OK):
        raise PermissionError(f"Write permission denied for directory {dir_name}")


def load_data(file_path: str, encoding: str = config.CSV_ENCODING) -> pd.DataFrame:
    """
    Load data from a CSV file into a DataFrame.

    Args:
        file_path (str): Path to the CSV file (can be a file name or an absolute path).

    Returns:
        pd.DataFrame: DataFrame containing the data from the CSV file.
    """
    if not os.path.exists(file_path):
        logging.error(f"The file {file_path} does not exist.")
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    check_read_permissions(file_path)

    try:
        return pd.read_csv(file_path, encoding=encoding)
    except pd.errors.ParserError as e:
        logging.error(f"Error parsing the file {file_path}: {e}")
        raise ValueError(f"Error parsing the file {file_path}: {e}")


def save_data(df: pd.DataFrame, file_path: str, encoding: str = config.CSV_ENCODING) -> None:
    """
    Save DataFrame to a CSV file.

    Args:
        df (pd.DataFrame): DataFrame to be saved.
        file_path (str): Path to the CSV file (can be a file name or an absolute path).
    """
    dir_name = os.path.dirname(file_path)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)
    check_write_permissions(file_path)

    try:
        df.to_csv(file_path, index=False, encoding=encoding)
    except IOError as e:
        logging.error(f"Error writing the file {file_path}: {e}")
        raise IOError(f"Error writing the file {file_path}: {e}")


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


if __name__ == "__main__":
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    video_stats_path = os.path.join(base_dir, 'data', 'video_stats.csv')

    try:
        video_info = load_data(video_stats_path)
        video_info = process_data(video_info)
    except Exception as e:
        logging.error(f"An error occurred while loading or processing data: {e}")
        exit(1)

    processed_video_stats_path = os.path.join(base_dir, 'data', 'processed_video_stats.csv')

    try:
        save_data(video_info, processed_video_stats_path)
    except Exception as e:
        logging.error(f"An error occurred while saving data: {e}")
        exit(1)
