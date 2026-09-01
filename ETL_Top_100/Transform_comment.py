import os

from google.cloud import bigquery
from google.oauth2 import service_account

PROJECT = "project-a6d82bf1-1bcf-49bc-913"
RAW_TABLE = f"{PROJECT}.jdebigproject1.Comment"
VER2_TABLE = f"{PROJECT}.Ver2_jde_bigproject1.V2_Comment"


def transform_comment(raw_table: str = RAW_TABLE,
                       dest_table: str = VER2_TABLE,
                       project: str = PROJECT,
                       key_path: str = None):
    key_path = key_path or os.getenv("GCP_KEY_PATH", "storage.json")
    credentials = service_account.Credentials.from_service_account_file(key_path)
    client = bigquery.Client(project=project, credentials=credentials)

    sql_query = f"""
        SELECT
          CAST(`comment_id` AS STRING) AS comment_id,
          CAST(`video_id` AS STRING) AS video_id,
          CAST(`parent_id` AS STRING) AS parent_id,
          TRIM(CAST(`author` AS STRING)) AS author_name,
          CAST(`author_channel` AS STRING) AS author_channel,
          TRIM(CAST(`text` AS STRING)) AS comment_text,
          COALESCE(CAST(`like_count` AS INT64), 0) AS like_count,
          COALESCE(CAST(`reply_count` AS INT64), 0) AS reply_count,
          CAST(`published_at` AS DATE) AS published_date,
          CAST(`is_reply` AS BOOL) AS is_reply,
          CURRENT_TIMESTAMP() AS transformed_at
        FROM `{raw_table}`
        WHERE `comment_id` IS NOT NULL
    """

    print("Dang thuc thi Transform bang Comment...")

    job_config = bigquery.QueryJobConfig(
        destination=dest_table,
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        create_disposition=bigquery.CreateDisposition.CREATE_IF_NEEDED
    )

    query_job = client.query(sql_query, job_config=job_config)
    query_job.result()

    print(f"Hoan tat! Du lieu Comment sach da duoc do vao: {dest_table}")


if __name__ == "__main__":
    transform_comment()