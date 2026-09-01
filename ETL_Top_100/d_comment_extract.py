import os
import time
import logging

import pandas as pd
from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv()
API_key = os.getenv("my_api_key")
youtube = build('youtube', 'v3', developerKey=API_key)
logger = logging.getLogger(__name__)


# HAM TRICH XUAT COMMENT (theo tung video)

def get_all_comments(video_id, max_comments=None):
    comments = []
    next_page_token = None

    while True:
        try:
            request = youtube.commentThreads().list(
                part='snippet,replies',
                videoId=video_id,
                maxResults=100,
                order='relevance',
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response.get('items', []):
                top = item['snippet']['topLevelComment']['snippet']
                comments.append({
                    'comment_id':     item['id'],
                    'video_id':       video_id,
                    'parent_id':      None,
                    'author':         top.get('authorDisplayName', ''),
                    'author_channel': top.get('authorChannelId', {}).get('value', ''),
                    'text':           top.get('textDisplay', ''),
                    'like_count':     top.get('likeCount', 0),
                    'reply_count':    item['snippet'].get('totalReplyCount', 0),
                    'published_at':   top.get('publishedAt', '')[:10],
                    'is_reply':       False,
                })

                if item['snippet']['totalReplyCount'] > 0 and 'replies' in item:
                    for reply in item['replies']['comments']:
                        r = reply['snippet']
                        comments.append({
                            'comment_id':     reply['id'],
                            'video_id':       video_id,
                            'parent_id':      item['id'],
                            'author':         r.get('authorDisplayName', ''),
                            'author_channel': r.get('authorChannelId', {}).get('value', ''),
                            'text':           r.get('textDisplay', ''),
                            'like_count':     r.get('likeCount', 0),
                            'reply_count':    0,
                            'published_at':   r.get('publishedAt', '')[:10],
                            'is_reply':       True,
                        })

            next_page_token = response.get('nextPageToken')
            if not next_page_token or (max_comments and len(comments) >= max_comments):
                break

        except HttpError as e:
            error_msg = str(e).lower()
            # Neu Google bao het Quota, nem loi nay ra ngoai luong chinh de dung chuong trinh
            if 'quotaexceeded' in error_msg:
                logger.warning("    -> \U0001F6D1 CANH BAO: API KEY DA HET QUOTA TRONG NGAY!")
                raise e
            # Neu chi la loi 403 thong thuong (tat binh luan) thi bo qua video nay
            elif e.resp.status == 403:
                logger.warning("    -> Bo qua: Video nay da bi tat binh luan.")
                break
            else:
                logger.warning(f"    -> Loi API Comment: {e}")
                break

    return comments[:max_comments] if max_comments else comments


def extract_comments(video_csv: str = "FULL_Video_Details_Stat.csv", output_file: str = "Comments_Stat.csv", max_comments=None):
    logger.info("Dang tai danh sach Video...")
    try:
        df_videos = pd.read_csv(video_csv)
        df_top_videos = df_videos.sort_values(['Artist', 'View Count'], ascending=[True, False])
        df_top_videos = df_top_videos.groupby('Artist').head(5)
        target_video_ids = df_top_videos['Video ID'].tolist()
    except FileNotFoundError:
        logger.warning(f"Loi: Khong tim thay file {video_csv}!")
        return

    processed_ids = set()

    # BUOC CHECKPOINT: Doc file cu de tim cac video da xu ly
    if os.path.exists(output_file):
        try:
            df_existing = pd.read_csv(output_file)
            if 'video_id' in df_existing.columns:
                processed_ids = set(df_existing['video_id'].dropna().unique())
                logger.warning(f"\U0001F50D Du lieu cu: Da co san binh luan cua {len(processed_ids)} video trong may.")
        except Exception as e:
            logger.warning(f"Khong the doc file {output_file} cu. Loi: {e}")

    # Loc bo cac video da cao
    remaining_video_ids = [vid for vid in target_video_ids if vid not in processed_ids]
    logger.info(f"\U0001F680 Tien hanh quet {len(remaining_video_ids)} video con lai...\n")

    try:
        for idx, vid_id in enumerate(remaining_video_ids, 1):
            logger.info(f"[{idx}/{len(remaining_video_ids)}] Dang quet comment Video: {vid_id}...")

            video_comments = get_all_comments(vid_id, max_comments=max_comments)

            if video_comments:
                df_temp = pd.DataFrame(video_comments)
                write_header = not os.path.exists(output_file)
                df_temp.to_csv(output_file, mode='a', index=False, header=write_header, encoding="utf-8-sig")

                logger.info(f"    -> Da nap & luu {len(video_comments)} binh luan vao file.")

            time.sleep(1)  # Nghi de tranh Rate Limit

        logger.info("\n\U0001F389 HOAN TAT XUAT SAC! Toan bo binh luan da duoc lay.")

    except HttpError as e:
        # Bat dung loi Quota tu trong ham nem ra
        if 'quotaexceeded' in str(e).lower():
            logger.info("\n=======================================================")
            logger.warning("\u23F8 HE THONG DA TAM DUNG VI HET HAN MUC (QUOTA) GOOGLE API")
            logger.info(f"\u2705 Dung lo! Du lieu cua cac video truoc do da duoc luu an toan vao {output_file}.")
            logger.warning("\U0001F552 Han muc se duoc Google reset vao khoang 2:00 PM (14h00) chieu mai.")
            logger.info("\u25B6 Ngay mai ban chi can chay lai dung file nay, he thong se tu dong quet tiep cac video con lai!")
            logger.info("=======================================================\n")
        else:
            raise


if __name__ == "__main__":
    extract_comments()