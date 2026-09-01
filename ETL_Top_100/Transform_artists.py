import os
import logging

from google.cloud import bigquery
from google.oauth2 import service_account

PROJECT = "project-a6d82bf1-1bcf-49bc-913"
RAW_TABLE = f"{PROJECT}.jdebigproject1.Dim_Artists"
VER2_TABLE = f"{PROJECT}.Ver2_jde_bigproject1.V2_Artist"
logger = logging.getLogger(__name__)

def transform_channel(raw_table: str = RAW_TABLE,
                       dest_table: str = VER2_TABLE,
                       project: str = PROJECT,
                       key_path: str = None):
    key_path = key_path or os.getenv("GCP_KEY_PATH", "storage.json")
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(project=project, credentials=credentials)

    sql_query = f"""
        SELECT
          CAST(`Rank` AS INT64) AS rank,
          TRIM(CAST(`Name` AS STRING)) AS name,
          TRIM(CAST(`artist_name` AS STRING)) AS artist_name,
          TRIM(CAST(`Channel Name` AS STRING)) AS channel_name,
          COALESCE(CAST(`Subscribers` AS INT64), 0) AS subscribers,
          COALESCE(CAST(`Total Videos` AS INT64), 0) AS total_videos,
          COALESCE(CAST(`Total Views` AS INT64), 0) AS total_views,
          CURRENT_TIMESTAMP() AS transformed_at
        FROM `{raw_table}`
        WHERE `Channel Name` IS NOT NULL
    """

    logger.info("Dang thuc thi Transform bang Channel...")

    job_config = bigquery.QueryJobConfig(
        destination=dest_table,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED
    )

    query_job = client.query(sql_query, job_config=job_config)
    query_job.result()

    logger.info(f"Hoan tat! Du lieu Channel sach da duoc do vao: {dest_table}")


if __name__ == "__main__":
    transform_channel()