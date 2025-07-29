"""
- inputs:
    - data: list of samples (uuid)
    - workflow
- loop through the samples
- run the selected workflow with the sample
"""
import os
import json
import requests

from requests.auth import HTTPBasicAuth


BASE_URL = "http://localhost:8080"
USERNAME = "admin"
PASSWORD = "CYsWGZY7y23vB7Su"

BASE_WORKSPACE = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/airflow/run_sam/out"


def get_sample_data(sample_uuid):
    """
    TODO
        here we hardcode the data location
        in the DigitalTWINS platform, sample data will be accessible via API calls
    """

    dicom_dir = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/ep4_sds_dicom/primary/sub-1/sam-1"

    return dicom_dir


if __name__ == '__main__':
    samples = ["sam-001001", "sam-001002", "sam-001003"]
    dag_id = "ep4"
    dag_url = f"{BASE_URL}/api/v1/dags/{dag_id}/dagRuns"
    body_model = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/body/imagewise/UNet/test_training_t1_batch16/best_accuracy-8"
    lung_model = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/lung/imagewise/UNet/test_training_T1_batch16/best_accuracy-5"

    for sample in samples:
        dicom_dir = get_sample_data(sample)
        workspace = os.path.join(BASE_WORKSPACE, str(sample))

        # log_dir = os.path.join(workspace, "logs")
        # os.makedirs(log_dir, exist_ok=True)

        params = {"sample_uuid": sample,
                  "dicom_dir": dicom_dir,
                  "workspace": workspace,
                  # "log_dir": log_dir,
                  "body_model": body_model,
                  "lung_model": lung_model}

        # Trigger the DAG via REST API
        response = requests.post(
            dag_url,
            auth=HTTPBasicAuth(USERNAME, PASSWORD),
            headers={"Content-Type": "application/json"},
            data=json.dumps({"conf": params})  # Pass parameters here
        )


