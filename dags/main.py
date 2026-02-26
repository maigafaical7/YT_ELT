
from dataquality.soda import yt_elt_data_quality

from airflow import DAG
import pendulum
from datetime import datetime, timedelta

from api.video_stats import get_playlist_id, get_video_ids, extract_video_data, save_to_json
from datawarehouse.dwh import core_table, staging_table
from airflow.operators.trigger_dagrun import TriggerDagRunOperator


local_tz = pendulum.timezone('Africa/Ouagadougou')

default_args = {
    'owner': 'dataengineers',
    'depends_on_past': False,
    'email_on_failure': False,
    'email_on_retry': False,
    'email': 'data@engineers.com',
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
    'max_active_runs': 1,
    'dagrun_timeout': timedelta(hours=1),
    'start_date': datetime(2026, 2, 5, tzinfo=local_tz),
}


#Variables
staging_schema = "staging"
core_schema = "core"


dag = DAG(
    dag_id='produce_json',
    default_args=default_args,
    description='DAG to produce JSON file with raw data',
    schedule='0 14 * * *',
    catchup=False,
    tags=['youtube', 'etl']
)


with dag:
    playlist_id_task = get_playlist_id()
    video_ids_task = get_video_ids(playlist_id_task)
    extract_data_task = extract_video_data(video_ids_task)
    save_to_json_result = save_to_json(extract_data_task)
    
    trigger_update_db = TriggerDagRunOperator(
        task_id="trigger_update_db",
        trigger_dag_id="update_db",
    )
    
    playlist_id_task >> video_ids_task >> extract_data_task >> save_to_json_result >> trigger_update_db


dag_update_db = DAG(
    dag_id='update_db',
    default_args=default_args,
    description='DAG to process JSON file and insert data into both staging and core schemas',
    schedule=None,
    catchup=False,
    tags=['youtube', 'etl']
)

with dag_update_db:
    update_staging = staging_table()
    update_core = core_table()
    
    trigger_data_quality = TriggerDagRunOperator(
        task_id="trigger_data_quality",
        trigger_dag_id="data_quality_check",
    )
    
    update_staging >> update_core >> trigger_data_quality
    
    

dag_data_quality = DAG(
    dag_id='data_quality_check',
    default_args=default_args,
    description='DAG to check data quality on both layers in the db',
    schedule=None,
    catchup=False,
    tags=['youtube', 'etl']
)

with dag_data_quality:
   soda_validate_staging = yt_elt_data_quality(staging_schema)
   soda_validate_core = yt_elt_data_quality(core_schema)
   
   soda_validate_staging >> soda_validate_core
    
