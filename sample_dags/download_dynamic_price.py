"""
### My First DAG
This DAG reads data from an testing API and save the downloaded data into a JSON file.
"""

import yfinance as yf
from airflow import DAG
from airflow.operators.python import PythonOperator
# from airflow.utils.dates import days_ago
from airflow.models import Variable
import mysql.connector, pendulum
from airflow.providers.mysql.operators.mysql import MySqlOperator
from airflow.operators.email import EmailOperator
from datetime import timedelta
import pendulum, os

os.environ["no_proxy"]="*"

def get_tickers(context):
    stock_list = Variable.get("stock_list_json", deserialize_json=True)

    stocks = context["dag_run"].conf.get("stocks", None) if ("dag_run" in context and context["dag_run"] is not None ) else None

    if stocks:
        stock_list = stocks
    return stock_list

def download_prices(*args, **context):
    stock_list = get_tickers(context)
    valid_tickers = []

    for ticker in stock_list:
        dat = yf.Ticker(ticker)
        hist = dat.history(period="1mo")

        if hist.shape[0]>0:
            valid_tickers.append(ticker)
        else:
            continue

        with open(get_file_path(ticker), 'w') as writer:
            hist.to_csv(writer, index=True)
        print(f"Downloaded {ticker}")
    return valid_tickers


def get_file_path(ticker):
    # NOT SAVE in distributed system.
    return f'logs/{ticker}.csv'

def load_price_data(ticker):
    with open(get_file_path(ticker) , 'r') as reader:
        lines = reader.readlines()
        return [[ticker]+line.split(',')[:5] for line in lines if line[:4]!='Date']


def save_to_mysql_stage(*args, **context):
    # tickers = get_tickers(context)
    # Pulls the return_value XCOM from "pushing_task"
    tickers = context['ti'].xcom_pull(task_ids='download_prices')
    print(f"received tickers: {tickers}")

    from airflow.hooks.base import BaseHook
    conn = BaseHook.get_connection('demodb')

    mydb = mysql.connector.connect(
    host=conn.host,
    user=conn.login,
    password=conn.password,
    database=conn.schema,
    port=conn.port
    )

    mycursor = mydb.cursor()
    for ticker in tickers: 
        val = load_price_data(ticker)
        print(f"{ticker} length={len(val)}   {val[1]}")

        sql = """INSERT INTO stock_prices_stage
            (ticker, as_of_date, open_price,high_price, low_price, close_price) 
            VALUES (%s, %s, %s, %s, %s, %s)"""
        mycursor.executemany(sql, val)

        mydb.commit()

        print(mycursor.rowcount, "record inserted.")



default_args = {
    'owner' : 'ELsa',
    'email': ['iriscat1990@gmail.com'],
    'email_on_failure': True,
    'email_on_retry': True,
    'retries': 1,
    'retry_delay': timedelta(seconds=30),
}


def generate_dag(investment_type):
    with DAG(
        dag_id =  f'Download_{investment_type}_Price',
        default_args=default_args,
        description=f'This DAG downloads {investment_type} prices and save them into text files.',
        schedule=timedelta(days=1),
        start_date=pendulum.today('UTC').add(days=-2),
        tags=['elsa.com'],
        catchup=False,
        max_active_runs=1,
    ) as dag:
        download_task = PythonOperator(
            task_id=f'download_{investment_type}_prices',
            python_callable=download_prices,
        ) 
        save_to_mysql_task =PythonOperator(
            task_id='save_to_database',
            python_callable=save_to_mysql_stage,
        )
        mysql_task = MySqlOperator(
                task_id=f'merge_{investment_type}_price',
                mysql_conn_id='demodb',
                sql='merge_stock_price.sql',
                dag=dag,
            )
        email_task = EmailOperator(
            task_id='send_email',
            to='harry.tan.data@gmail.com',
            subject='Stock {investment_type} is downloaded - {{ds}}',
            html_content=""" <h3>Email Test</h3> {{ ds_nodash }}<br/>{{ dag }}<br/>{{ conf }}<br/>{{ next_ds }}<br/>{{ yesterday_ds }}<br/>{{ tomorrow_ds }}<br/>{{ execution_date }}<br/>""",
            dag=dag
        )
        download_task >> save_to_mysql_task >> mysql_task >> email_task
        return dag

investment_types= ['Equity', 'ETF']
for _type in investment_types:
    globals()["Dynamic_DAG"+_type] = generate_dag(_type)