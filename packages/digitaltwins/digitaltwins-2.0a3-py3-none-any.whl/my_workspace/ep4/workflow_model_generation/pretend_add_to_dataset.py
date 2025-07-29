import shutil

from airflow import DAG
from airflow.operators.python import PythonOperator

from pathlib import Path

# from irods.session import iRODSSession
# import os
import configparser

# from digitaltwins import Querier


def add_subject(assay_seek_id, workspace, platform_config_file):
    # todo
    pass


def exec(**kwargs):
    assay_seek_id = kwargs['dag_run'].conf.get('assay_seek_id', kwargs['params'].get('assay_seek_id'))
    # workspace = kwargs['dag_run'].conf.get('workspace', kwargs['params'].get('workspace'))
    # platform_config_file = kwargs['dag_run'].conf.get('platform_config_file', kwargs['params'].get('platform_config_file'))
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/workflow_model_generation/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    add_subject(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)


def get_task(dag: DAG):
    task_id = "add_to_dataset"
    return PythonOperator(
        task_id=task_id,
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    assay_seek_id = 2
    assay_uuid = "25e0cb08-f486-11ef-917d-484d7e9beb16"
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/workflow_model_generation/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    add_subject(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)

