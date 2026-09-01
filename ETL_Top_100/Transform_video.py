import os
import logging

from google.cloud import bigquery
from google.oauth2 import service_account

PROJECT = "project-a6d82bf1-1bcf-49bc-913"
RAW_TABLE = f"{PROJECT}.jdebigproject1.Video"
VER2_TABLE = f"{PROJECT}.Ver2_jde_bigproject1.V2_Video"
logger = logging.getLogger(__name__)

def transform_video(raw_table: str = RAW_TABLE,
                     dest_table: str = VER2_TABLE,
                     project: str = PROJECT,
                     key_path: str = None):
    key_path = key_path or os.getenv("GCP_KEY_PATH", "storage.json")
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(project=project, credentials=credentials)

    sql_query = f"""
        SELECT
          CAST(`Video ID` AS STRING) AS video_id,
          CAST(`Artist` AS STRING) AS artist_name,
          TRIM(`Title`) AS video_title,
          CAST(`Published At` AS DATE) AS published_date,
          COALESCE(CAST(`View Count` AS INT64), 0) AS view_count,
          COALESCE(CAST(`Like Count` AS INT64), 0) AS like_count,
          COALESCE(CAST(`Comment Count` AS INT64), 0) AS comment_count,
          CAST(`Duration Sec` AS INT64) AS duration_seconds,
          CURRENT_TIMESTAMP() AS transformed_at
        FROM `{raw_table}`
        WHERE `Video ID` IS NOT NULL
    """

   
    logger.info("Dang thuc thi Transform server-side...")

    job_config = bigquery.QueryJobConfig(
        destination=dest_table,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED
    )

    query_job = client.query(sql_query, job_config=job_config)
    query_job.result()

    logger.info(f"Hoan tat! Luong du lieu sach da duoc do vao: {dest_table}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, 
                        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    transform_video()