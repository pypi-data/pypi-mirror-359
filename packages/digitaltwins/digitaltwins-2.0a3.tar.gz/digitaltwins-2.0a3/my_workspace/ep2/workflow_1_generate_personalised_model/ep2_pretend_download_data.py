import shutil

from airflow import DAG
from airflow.operators.python import PythonOperator

from pathlib import Path

# from irods.session import iRODSSession
# import os
import configparser

# from digitaltwins import Querier


def download(assay_seek_id, workspace, platform_config_file):
    # irods configs
    config_file = Path(platform_config_file)
    configs = configparser.ConfigParser()
    configs.read(config_file)

    configs = configs["irods"]
    host = configs.get("irods_host")
    port = configs.get("irods_port")
    user = configs.get("irods_user")
    password = configs.get("irods_password")
    zone = configs.get("irods_zone")
    project_root = configs.get("irods_project_root")

    ## todo download datasets/samples into the workspace
    pass


def exec(**kwargs):
    assay_seek_id = kwargs['dag_run'].conf.get('assay_seek_id', kwargs['params'].get('assay_seek_id'))
    # workspace = kwargs['dag_run'].conf.get('workspace', kwargs['params'].get('workspace'))
    # platform_config_file = kwargs['dag_run'].conf.get('platform_config_file', kwargs['params'].get('platform_config_file'))
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep2/workflow_1_generate_personalised_model/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    download(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)


def get_task(dag: DAG):
    task_id = "download_data"
    return PythonOperator(
        task_id=task_id,
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    assay_seek_id = 2
    assay_uuid = "25e0cb08-f486-11ef-917d-484d7e9beb16"
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep2/workflow_1_generate_personalised_model/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    # log_dir = os.path.join(workspace, "logs")
    # os.makedirs(log_dir, exist_ok=True)

    download(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)

    # dataset_uuid = "6ba38e34-ee5d-11ef-917d-484d7e9beb16"
    # sample_uuid = "015465ba-65ac-11ef-917d-484d7e9beb16"
    #
    # download(dataset_uuid=dataset_uuid, sample_uuid=sample_uuid, workspace=workspace)
