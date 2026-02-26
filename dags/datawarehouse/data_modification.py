from psycopg2 import sql
import logging

logger = logging.getLogger(__name__)
table = "yt_api"


def insert_rows(cur, conn, schema, row):
    try:
        if schema == "staging":
            query = sql.SQL("""
                INSERT INTO {}.{} (video_id, title, publishedat, duration, viewcount, likecount, commentcount)
                VALUES (%(video_id)s, %(title)s, %(publishedAt)s, %(duration)s, %(viewCount)s, %(likeCount)s, %(commentCount)s);
            """).format(sql.Identifier(schema), sql.Identifier(table))
        else:
            query = sql.SQL("""
                INSERT INTO {}.{} (video_id, video_title, upload_date, duration, video_type, video_views, likes_count, comments_count)
                VALUES (%(video_id)s, %(video_title)s, %(upload_date)s, %(duration)s, %(video_type)s, %(video_views)s, %(likes_count)s, %(comments_count)s);
            """).format(sql.Identifier(schema), sql.Identifier(table))

        cur.execute(query, row)
        conn.commit()
        logger.info(f"Inserted row with video_id: {row['video_id']}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error inserting row with video_id: {row.get('video_id', 'unknown')} - {e}")
        raise e


def update_rows(cur, conn, schema, row):
    try:
        if schema == "staging":
            query = sql.SQL("""
                UPDATE {}.{}
                SET title = %(title)s,
                    viewcount = %(viewCount)s,
                    likecount = %(likeCount)s,
                    commentcount = %(commentCount)s
                WHERE video_id = %(video_id)s AND publishedat = %(publishedAt)s;
            """).format(sql.Identifier(schema), sql.Identifier(table))
        else:
            query = sql.SQL("""
                UPDATE {}.{}
                SET video_title = %(video_title)s,
                    video_views = %(video_views)s,
                    likes_count = %(likes_count)s,
                    comments_count = %(comments_count)s,
                    duration = %(duration)s,
                    video_type = %(video_type)s
                WHERE video_id = %(video_id)s AND upload_date = %(upload_date)s;
            """).format(sql.Identifier(schema), sql.Identifier(table))

        cur.execute(query, row)
        conn.commit()
        logger.info(f"Updated row with video_id: {row['video_id']}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error updating row with video_id: {row.get('video_id', 'unknown')} - {e}")
        raise e


def delete_rows(cur, conn, schema, ids_to_delete):
    try:
        query = sql.SQL("DELETE FROM {}.{} WHERE video_id = ANY(%s);").format(
            sql.Identifier(schema), sql.Identifier(table)
        )
        cur.execute(query, (list(ids_to_delete),))
        conn.commit()
        logger.info(f"Deleted rows with video_ids: {ids_to_delete}")
    except Exception as e:
        conn.rollback()
        logger.error(f"Error deleting rows with video_ids: {ids_to_delete} - {e}")
        raise e