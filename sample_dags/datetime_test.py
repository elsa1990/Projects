import os
import time
import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator, BranchPythonOperator
from airflow.operators.dummy_operator import DummyOperator


def check_weekday(date_stamp):
    today = datetime.strptime(date_stamp, '%Y%m%d')

    if today.isoweekday() <= 5:
        return 'is_workday'
    else:
        return 'is_holiday'


def get_metadata():
    logging.info('get_metadata'+'~'*30+'!!!')


def clean_data():
    logging.info('clean_data'+'~'*30+'!!!')


default_args = {
    'owner': 'AxotZero',
    'start_date': datetime(2020, 8, 21),
    'schedule_interval': '@daily',
    'retries': 2,
    'retry_delay': timedelta(minutes=5)
}

with DAG(dag_id='tutorial', default_args=default_args) as dag:

    tw_stock_start = DummyOperator(
        task_id='tw_stock_start'
    )

    check_weekday = BranchPythonOperator(
        task_id='check_weekday',
        python_callable=check_weekday,
        op_args=['{{ ds_nodash }}']
    )

    is_holiday = DummyOperator(
        task_id='is_holiday'
    )

    is_workday = DummyOperator(
        task_id='is_workday'
    )

    get_metadata = PythonOperator(
        task_id='get_metadata',
        python_callable=get_metadata,
    )

    clean_data = PythonOperator(
        task_id='clean_data',
        python_callable=clean_data,
    )

    tw_stock_end = DummyOperator(
        task_id='tw_stock_end',
        trigger_rule='one_success'
    )

    tw_stock_start >> check_weekday >> [is_workday, is_holiday]
    is_holiday >> tw_stock_end
    is_workday >> get_metadata >> clean_data >> tw_stock_end
