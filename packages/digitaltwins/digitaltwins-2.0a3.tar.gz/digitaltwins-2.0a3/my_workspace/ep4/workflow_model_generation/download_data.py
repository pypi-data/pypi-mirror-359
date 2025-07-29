import shutil

from airflow import DAG
from airflow.operators.python import PythonOperator

from pathlib import Path

from irods.session import iRODSSession
import os
import configparser

from digitaltwins import Querier


def download(assay, workspace=None):
    # irods configs
    config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini")
    configs = configparser.ConfigParser()
    configs.read(config_file)

    configs = configs["irods"]
    host = configs.get("irods_host")
    port = configs.get("irods_port")
    user = configs.get("irods_user")
    password = configs.get("irods_password")
    zone = configs.get("irods_zone")
    project_root = configs.get("irods_project_root")

    inputs = assay.get("params").get("input")
    for input in inputs:
        if not input.get("category") == "measurement":
            continue
        dataset_uuid = input.get("dataset_uuid")
        sample_type = input.get("sample_type")

        querier = Querier(config_file)
        querier.get_dataset_samples(dataset_uuid, sample_type)

        sql = (r"SELECT * "
               r"FROM dataset_mapping "
               r"INNER JOIN sample ON dataset_mapping.sample_uuid = sample.sample_uuid "
               r"WHERE sample_type='{sample_type}'").format(sample_type=sample_type)


        # get subject id & sample id

def download_assay_input(index, assay, workspace=None):
    pass



# def download(dataset_uuid, sample_uuid, workspace=None):
#     config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini")
#     configs = configparser.ConfigParser()
#     configs.read(config_file)
#
#     configs = configs["irods"]
#     host = configs.get("irods_host")
#     port = configs.get("irods_port")
#     user = configs.get("irods_user")
#     password = configs.get("irods_password")
#     zone = configs.get("irods_zone")
#     project_root = configs.get("irods_project_root")
#
#     print(f"Downloading Sample {sample_uuid}")
#     subject_id = "sub-1"
#     sample_id = "sam-1"
#     endpoint = f"{dataset_uuid}/primary/{subject_id}/{sample_id}"
#
#     save_dir = workspace.joinpath(sample_uuid, "downloaded")
#     save_dir.mkdir(parents=True, exist_ok=True)
#
#     with iRODSSession(host=host, port=port, user=user, password=password,
#                       zone=zone) as session:
#         irods_folder_path = f"{project_root}/{endpoint}"
#         folder_contents = session.collections.get(irods_folder_path)
#
#         # Iterate over the contents of the folder
#         for item in folder_contents.data_objects:
#             # Define the local file path
#             local_file_path = os.path.join(save_dir, item.name)
#
#             # Download the file
#             with open(local_file_path, 'wb') as local_file:
#                 with item.open('r') as irods_file:
#                     local_file.write(irods_file.read())
#
#             print(f"Downloaded: {item.name}")


def exec(**kwargs):
    assay = kwargs['dag_run'].conf.get('assay', kwargs['params'].get('assay'))
    workspace = kwargs['dag_run'].conf.get('workspace', kwargs['params'].get('workspace'))
    platform_configs = kwargs['dag_run'].conf.get('platform_configs', kwargs['params'].get('platform_configs'))

    download(assay=assay, workspace=workspace)


def get_task(dag: DAG):
    task_id = "download_data"
    return PythonOperator(
        task_id=task_id,
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    workspace = Path("./workspace")
    assay = {}

    download(assay=assay, workspace=workspace)

    # dataset_uuid = "6ba38e34-ee5d-11ef-917d-484d7e9beb16"
    # sample_uuid = "015465ba-65ac-11ef-917d-484d7e9beb16"
    #
    # download(dataset_uuid=dataset_uuid, sample_uuid=sample_uuid, workspace=workspace)
