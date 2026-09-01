import os
import logging

import pandas as pd
from google.cloud import bigquery

DEFAULT_TABLE_ID = "project-a6d82bf1-1bcf-49bc-913.jdebigproject1.Dim_Artists"
logger = logging.getLogger(__name__)

def load_channel_stats(input_csv: str = "Top100artistsStat.csv",
                        table_id: str = DEFAULT_TABLE_ID,
                        key_path: str = None):
    key_path = key_path or os.getenv("GCP_KEY_PATH", "storage.json")
    client = bigquery.Client.from_service_account_json(key_path)

    df = pd.read_csv(input_csv)

    job_config = bigquery.LoadJobConfig(
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE
    )

    load_job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
    load_job.result()

    logger.info(f"Loaded {len(df)} rows into {table_id}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, 
                        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s")
    load_channel_stats()