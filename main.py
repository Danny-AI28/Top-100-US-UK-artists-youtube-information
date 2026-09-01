from ETL_Top_100.b_channel_extract import extract_channel_stats
from ETL_Top_100.c_video_extract import extract_video_stats
from ETL_Top_100.d_comment_extract import extract_comments

from ETL_Top_100.Load_artists import load_channel_stats
from ETL_Top_100.Load_video import load_videos
from ETL_Top_100.Load_comment import load_comments

from ETL_Top_100.Transform_artists import transform_channel
from ETL_Top_100.Transform_video import transform_video
from ETL_Top_100.Transform_comment import transform_comment
import logging
logger = logging.getLogger(__name__)

def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler("pipeline.log", encoding="utf-8")
        ]
    )
    logger.info("GIAI DOAN 1")
    extract_channel_stats(
        input_csv="Top100artists.csv",
        output_csv="Top100artistsStat.csv"
    )
    extract_video_stats(
        artist_csv="Top100artists.csv",
        output_csv="FULL_Video_Details_Stat.csv"
    )
    extract_comments(
        video_csv="FULL_Video_Details_Stat.csv",
        output_file="Comments_Stat.csv"
    )

    logger.info("GIAI DOAN 2")
    load_channel_stats()
    load_videos()
    load_comments()

    logger.info("GIAI DOAN 3")
    transform_channel()
    transform_video()
    transform_comment()

    print("\nHoan tat toan bo pipeline ETL.")


if __name__ == "__main__":
    main()