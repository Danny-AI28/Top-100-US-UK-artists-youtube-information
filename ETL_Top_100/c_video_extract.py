import os
import time
import re
import urllib.parse
import logging

import pandas as pd
import requests
from dotenv import load_dotenv
from googleapiclient.discovery import build
from ETL_Top_100.b_channel_extract import get_channel_id_free

load_dotenv()
API_key = os.getenv("my_api_key")  
youtube = build('youtube', 'v3', developerKey=API_key)
logger = logging.getLogger(__name__)

#Ham xu ly
def parse_duration(pt_str):
    m = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', pt_str)
    if not m: return 0, "00:00"
    s = int(m.group(1) or 0)*3600 + int(m.group(2) or 0)*60 + int(m.group(3) or 0)
    fmt = f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}" if s >= 3600 else f"{s//60:02d}:{s%60:02d}"
    return s, fmt

def extract_videos(artist):
    ch_id = get_channel_id_free(artist)
    if not ch_id: return []
    
    ch_res = youtube.channels().list(part='contentDetails', id=ch_id).execute()
    if not ch_res.get('items'): return []
    pl_id = ch_res['items'][0]['contentDetails']['relatedPlaylists']['uploads']
    vid_ids, token = [], None
    while True:
        pl_res = youtube.playlistItems().list(part="contentDetails", playlistId=pl_id, maxResults=50, pageToken=token).execute()
        vid_ids.extend([i['contentDetails']['videoId'] for i in pl_res.get('items', [])])
        token = pl_res.get('nextPageToken')
        if not token: break

    # 4. Lấy chi tiết Video (Batch 50)
    videos = []
    for i in range(0, len(vid_ids), 50):
        v_res = youtube.videos().list(part='snippet,statistics,contentDetails', id=','.join(vid_ids[i:i+50])).execute()
        for item in v_res.get('items', []):
            s, st, cd = item['snippet'], item.get('statistics', {}), item['contentDetails']
            sec, fmt = parse_duration(cd['duration'])
            videos.append({
                'Artist': artist, 
                'Video ID': item['id'], 
                'Title': s.get('title', ''),
                'Published At': s.get('publishedAt', '')[:10], 
                'Duration Sec': sec, 
                'Duration': fmt,
                'View Count': int(st.get('viewCount', 0)), 
                'Like Count': int(st.get('likeCount', 0)),
                'Comment Count': int(st.get('commentCount', 0)), 
                'URL': f"https://www.youtube.com/watch?v={item['id']}"
            })
    return videos


def extract_video_stats(artist_csv: str = "Top100artists.csv", output_csv: str = "FULL_Video_Details_Stat.csv") -> pd.DataFrame:
    logger.info("Bat dau trich xuat du lieu Video...")
    df_artists = pd.read_csv(artist_csv)
    master_list = []
 
    for idx, artist in enumerate(df_artists["artist_name"], 1):
        logger.info(f"[{idx}/100] Dang quet: {artist}...")
        try:
            data = extract_videos(artist)
            master_list.extend(data)
            logger.info(f"Thanh cong ({len(data)} videos)")
        except Exception as e:
            logger.warning(f"Loi: {e}")
        time.sleep(1)  # Nghi de khong bi Google danh dau spam API
 
    df_result = pd.DataFrame(master_list)
 
    if master_list and output_csv:
        df_result.to_csv(output_csv, index=False, encoding="utf-8-sig")
        logger.info(f"\nHoan tat! Da luu tong cong {len(master_list)} videos vao {output_csv}")
 
    return df_result
 
 
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, 
                        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    extract_video_stats()
 