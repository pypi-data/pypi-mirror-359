import json
from pathlib import Path
import requests

from requests.auth import HTTPBasicAuth

from digitaltwins import Downloader
from irods.session import iRODSSession
import os
import configparser


AIRFLOW_API_URL = "http://localhost:8080/api/v1"
USERNAME = "admin"
PASSWORD = "CYsWGZY7y23vB7Su"


def get_dataset_id(sample_id):
    dataset_id = "measurement_dicom"

    return dataset_id


def get_endpoint(sample_id):
    # todo: irods folder structure needs to be redefined by having dataset_uuid before dataset_name. Temporarily for
    #  now, the endpoint will be hardcoded

    id_mapping = {"sam-001001": {"dataset": "measurement_dicom", "subject": "sub-1", "sample": "sam-1"},
                  "sam-001002": {"dataset": "measurement_dicom", "subject": "sub-2", "sample": "sam-1"},
                  }
    id_mapping = {"015465ba-65ac-11ef-917d-484d7e9beb16": {"dataset": "93d49efa-5f4e-11ef-917d-484d7e9beb16", "subject": "sub-1", "sample": "sam-1"},
                  "08a6a35a-65ac-11ef-917d-484d7e9beb16": {"dataset": "93d49efa-5f4e-11ef-917d-484d7e9beb16", "subject": "sub-2", "sample": "sam-1"},
                  }

    dataset = id_mapping.get(sample_id).get("dataset")
    subject = id_mapping.get(sample_id).get("subject")
    sample = id_mapping.get(sample_id).get("sample")

    endpoint = f"{dataset}/primary/{subject}/{sample}"

    return endpoint


def download(sample, workspace):
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

    # for sample in samples:
    print(f"Downloading Sample {sample}")
    endpoint = get_endpoint(sample)

    save_dir = workspace.joinpath(sample, "downloaded")
    save_dir.mkdir(parents=True, exist_ok=True)

    with iRODSSession(host=host, port=port, user=user, password=password,
                      zone=zone) as session:
        irods_folder_path = f"{project_root}/{endpoint}"
        folder_contents = session.collections.get(irods_folder_path)

        # Iterate over the contents of the folder
        for item in folder_contents.data_objects:
            # Define the local file path
            local_file_path = os.path.join(save_dir, item.name)

            # Download the file
            with open(local_file_path, 'wb') as local_file:
                with item.open('r') as irods_file:
                    local_file.write(irods_file.read())

            print(f"Downloaded: {item.name}")


def get_sample_data(workspace, sample):
    dicom_dir = workspace.joinpath(sample, "downloaded")

    return dicom_dir


def trigger_workflow(workflow_id, sample, workspace):
    dag_url = f"{AIRFLOW_API_URL}/dags/{workflow_id}/dagRuns"

    body_model = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/body/imagewise/UNet/test_training_t1_batch16/best_accuracy-8"
    lung_model = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/lung/imagewise/UNet/test_training_T1_batch16/best_accuracy-5"

    # for sample in samples:
    print(f"Triggering workflow for Sample {sample}")
    dicom_dir = get_sample_data(workspace, sample)
    workspace = workspace.joinpath(str(sample))

    # log_dir = os.path.join(workspace, "logs")
    # os.makedirs(log_dir, exist_ok=True)

    params = {"sample_uuid": sample,
              "dicom_dir": str(dicom_dir),
              "workspace": str(workspace),
              # "log_dir": log_dir,
              "body_model": body_model,
              "lung_model": lung_model}

    # Trigger the DAG via REST API
    response = requests.post(
        dag_url,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        headers={"Content-Type": "application/json"},
        data=json.dumps({"conf": params})
    )


if __name__ == '__main__':
    # samples = ["sam-001001", "sam-001002"]
    samples = ["015465ba-65ac-11ef-917d-484d7e9beb16", "08a6a35a-65ac-11ef-917d-484d7e9beb16"]
    workspace = Path("/home/clin864/opt/digitaltwins-api/my_workspace/ep4/airflow/run_sam/workspace")

    workflow_id = "ep4"

    for sample in samples:
        # download samples
        download(sample, workspace)
        # trigger workflow
        trigger_workflow(workflow_id, sample, workspace)

    print("All tasks submitted")


