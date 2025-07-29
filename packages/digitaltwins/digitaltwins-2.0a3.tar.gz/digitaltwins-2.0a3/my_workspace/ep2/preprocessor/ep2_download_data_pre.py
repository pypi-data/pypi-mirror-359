import json
import os
import shutil

from collections import defaultdict

import requests
from requests.auth import HTTPBasicAuth

from airflow import DAG
from airflow.operators.python import PythonOperator



def run(assay_seek_id, workspace, platform_config_file):
    subject_uuid = "ep2_subject"
    workflow_dataset_uuid = "9ccb0f66-4581-11f0-917d-484d7e9beb16"

    # todo. get_assay will be replaced by digitaltwins API querier.get_assay

    # download data

    # trigger workflow

    params = {
        "subject_uuid": subject_uuid,
        "assay_seek_id": assay_seek_id,
        "workspace": None,
        # "platform_configs": None,
    }
    airflow_api_url = "http://130.216.208.137:8080/api/v1"
    dag_url = f"{airflow_api_url}/dags/{workflow_dataset_uuid}/dagRuns"
    response = requests.post(
        dag_url,
        auth=HTTPBasicAuth("admin", "PgKFTfe4B2C7ragN"),
        headers={"Content-Type": "application/json"},
        data=json.dumps({"conf": params})
    )



def exec(**kwargs):
    assay_seek_id = kwargs['dag_run'].conf.get('assay_seek_id', kwargs['params'].get('assay_seek_id'))
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep2/workflow_1_generate_personalised_model/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    run(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)


def get_task(dag: DAG):
    task_id = "download_data_pre"
    return PythonOperator(
        task_id=task_id,
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    assay_seek_id = 18
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/preprocessor/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    run(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)

