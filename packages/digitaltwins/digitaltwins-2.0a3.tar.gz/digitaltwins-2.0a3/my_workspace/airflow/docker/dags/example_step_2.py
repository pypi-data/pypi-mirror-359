import json
import os
import shutil

from collections import defaultdict

import requests
from requests.auth import HTTPBasicAuth

from airflow import DAG
from airflow.operators.python import PythonOperator


def run():
    import time
    time.sleep(1)



def exec(**kwargs):
    run()


def get_task(dag: DAG):
    task_id = "example_step_2"
    return PythonOperator(
        task_id=task_id,
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    run()

