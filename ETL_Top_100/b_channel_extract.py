import os
import time
import re
import urllib.parse
import logging

import pandas as pd
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build

load_dotenv()
API_key = os.getenv("my_api_key")
youtube = build('youtube', 'v3', developerKey=API_key)
logger = logging.getLogger(__name__)


# --- HAM LAY ID KENH MIEN PHI ---
def get_channel_id_free(artist_name):
    # Da tu dong them chu "official channel" vao day
    query = urllib.parse.quote(f"{artist_name} official channel")
    url = f"https://www.youtube.com/results?search_query={query}"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    try:
        response = requests.get(url, headers=headers)
        match = re.search(r'"channelId":"(UC[\w-]+)"', response.text)
        if match:
            return match.group(1)
    except Exception as e:
        logger.warning(f"  -> Loi mang khi quet: {e}")
    return None


# --- HAM LAY THONG KE TU API ---
def get_channel_info(channel_id):
    response = youtube.channels().list(
        part='snippet,statistics',
        id=channel_id
    ).execute()

    if not response.get('items'):
        return None

    ch = response['items'][0]
    return {
        'Channel Name': ch['snippet']['title'],
        'Subscribers': int(ch['statistics'].get('subscriberCount', 0)),
        'Total Videos': int(ch['statistics'].get('videoCount', 0)),
        'Total Views': int(ch['statistics'].get('viewCount', 0))
    }


def extract_channel_stats(input_csv: str = "Top100artists.csv", output_csv: str = None) -> pd.DataFrame:

    logger.info(f"Dang tai danh sach tu {input_csv}...")
    df1 = pd.read_csv(input_csv)

    df1['Channel Name'] = ""
    df1['Subscribers'] = 0
    df1['Total Videos'] = 0
    df1['Total Views'] = 0

    for index, artist in enumerate(df1["artist_name"]):
        logger.info(f"[{index + 1}/100] Dang xu ly: {artist}")

        try:
            channel_id = get_channel_id_free(artist)

            if channel_id:
                stats = get_channel_info(channel_id)

                if stats:
                    df1.at[index, 'Channel Name'] = stats['Channel Name']
                    df1.at[index, 'Subscribers'] = stats['Subscribers']
                    df1.at[index, 'Total Videos'] = stats['Total Videos']
                    df1.at[index, 'Total Views'] = stats['Total Views']

                    logger.info(f"  -> Ten: {stats['Channel Name']} | Sub: {stats['Subscribers']:,} | Video: {stats['Total Videos']:,} | View: {stats['Total Views']:,}")
                else:
                    logger.warning("  -> Loi: Khong the lay so lieu tu API.")
            else:
                logger.warning("  -> Khong tim thay kenh tren YouTube.")

        except Exception as e:
            logger.warning(f"  -> Loi: {e}")

        time.sleep(1)

    logger.info("Hoan tat crawl channel stats.")

    if output_csv:
        df1.to_csv(output_csv, index=False, encoding="utf-8-sig")
        logger.info(f"Da luu vao {output_csv}")

    return df1


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    extract_channel_stats(output_csv="Top100artistsStat.csv")