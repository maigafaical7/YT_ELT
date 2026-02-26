from airflow.providers.postgres.hooks.postgres import PostgresHook
from psycopg2.extras import RealDictCursor
from psycopg2 import sql
import logging

logger = logging.getLogger(__name__)
table = "yt_api"


def get_conn_cursor():
    hook = PostgresHook(postgres_conn_id="postgres_db_yt_elt", database="youtube_elt")
    conn = hook.get_conn()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    logger.info("Database connection established")
    return conn, cur


def close_conn_cursor(conn, cur):
    cur.close()
    conn.close()
    logger.info("Database connection closed")


def create_schema(cur, conn, schema):
    query = sql.SQL("CREATE SCHEMA IF NOT EXISTS {};").format(sql.Identifier(schema))
    cur.execute(query)
    conn.commit()
    logger.info(f"Schema {schema} created or already exists")


def create_table(cur, conn, schema):
    if schema == "staging":
        table_sql = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.{} (
                video_id VARCHAR(11) PRIMARY KEY NOT NULL,
                title TEXT NOT NULL,
                publishedat TIMESTAMP NOT NULL,
                duration VARCHAR(20) NOT NULL,
                viewcount INT,
                likecount INT,
                commentcount INT
            );
        """).format(sql.Identifier(schema), sql.Identifier(table))
    else:
        table_sql = sql.SQL("""
            CREATE TABLE IF NOT EXISTS {}.{} (
                video_id VARCHAR(11) PRIMARY KEY NOT NULL,
                video_title TEXT NOT NULL,
                upload_date TIMESTAMP NOT NULL,
                duration VARCHAR(20) NOT NULL,
                video_type VARCHAR(20),
                video_views INT,
                likes_count INT,
                comments_count INT
            );
        """).format(sql.Identifier(schema), sql.Identifier(table))

    cur.execute(table_sql)
    conn.commit()
    logger.info(f"Table {schema}.{table} created or already exists")


def get_video_ids(cur, schema):
    query = sql.SQL("SELECT video_id FROM {}.{};").format(
        sql.Identifier(schema), sql.Identifier(table)
    )
    cur.execute(query)
    ids = cur.fetchall()
    video_ids = [row["video_id"] for row in ids]
    logger.info(f"Retrieved {len(video_ids)} video IDs from {schema}")
    return video_ids