from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Define the default_args dictionary
default_args = {
    'owner': 'airflow',
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define a simple Python function to use in tasks
def say_hello():
    print("Hello from Airflow!")

def say_goodbye():
    print("Goodbye from Airflow!")

# Instantiate the DAG
with DAG(
    dag_id='my_example_dag',
    default_args=default_args,
    description='A simple example DAG',
    # schedule_interval='@daily',   # You can use cron as well, e.g., '0 12 * * *'
    # start_date=datetime(2024, 1, 1),
    catchup=False,   # Don't try to "catch up" missed runs
    tags=['example'],
) as dag:

    task_1 = PythonOperator(
        task_id='say_hello_task',
        python_callable=say_hello
    )

    task_2 = PythonOperator(
        task_id='say_goodbye_task',
        python_callable=say_goodbye
    )

    task_1 >> task_2  # Define task dependencies (task_1 runs before task_2)
