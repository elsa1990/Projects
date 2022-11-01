"""
This DAG reads data from an testing API and save the downloaded data into a JSON file.
"""

# import yfinance as yf
from airflow import DAG
# from airflow.utils.dates import days_ago
from airflow.providers.amazon.aws.operators.s3 import S3ListOperator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor
from datetime import timedelta
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
import pendulum, os

os.environ["no_proxy"]="*"

default_args = {
    'owner' : 'elsa.com',
    'email': ['iriscat1990@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
}


with DAG(
    dag_id =  'Download_Stock_List',
    default_args=default_args,
    description='This DAG provies samples operations in AWS S3. ',
    schedule=timedelta(days=1),
    start_date=pendulum.today('UTC').add(days=-2),
    tags=['elsa.com'],
    catchup=False,
    max_active_runs=1,
) as dag:
    s3_sensor = S3KeySensor(
        task_id='new_s3_file',
        bucket_key='Airflow/stockprice/{{ds_nodash}}/*.csv',
        wildcard_match=True,
        bucket_name='stock-bucket-elsa',
        aws_conn_id='s3_conn',
        timeout=18*60*60,
        poke_interval=30,
        dag=dag)
    list_s3_file = S3ListOperator(
        task_id='list_s3_files',
        bucket='stock-bucket-elsa',
        prefix='Airflow/stockprice/{{ds_nodash}}/',
        delimiter='/',
        aws_conn_id='s3_conn'
    )
    
    trigger_next_dag = TriggerDagRunOperator(
        trigger_dag_id = "Download_Stock_Price",
        task_id = "download_prices",
        execution_date = "{{ds}}",
        reset_dag_run=True,
        wait_for_completion =False
    )
    s3_sensor >> list_s3_file >> trigger_next_dag