import logging

logger = logging.getLogger(__name__)


def parse_duration(duration_str):

    duration_str = duration_str.replace("P", "").replace("T", "")

    components = ["D", "H", "M", "S"]
    values = {"D": 0, "H": 0, "M": 0, "S": 0}

    for component in components:
        if component in duration_str:
            value, duration_str = duration_str.split(component)
            values[component] = int(value)

    total_duration = timedelta(
        days=values["D"], hours=values["H"], minutes=values["M"], seconds=values["S"]
    )

    return total_duration


def transform_data(row):
    """Transform data from staging to core schema"""
    try:
        transformed_row = {
            "video_id": row.get("video_id"),
            "video_title": row.get("title"),
            "upload_date": row.get("publishedat"),
            "duration": row.get("duration"),
            "video_type": "Music" if "music" in (row.get("title") or "").lower() else "Standard",
            "video_views": int(row.get("viewcount") or 0),
            "likes_count": int(row.get("likecount") or 0),
            "comments_count": int(row.get("commentcount") or 0),
        }
        return transformed_row

    except Exception as e:
        logger.error(f"Error transforming data: {e}")
        raise e