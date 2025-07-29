"""
- inputs:
    - data: sample (uuid)
    - workflow
- run the selected workflow with the sample
"""
import os
import json
import requests

from requests.auth import HTTPBasicAuth


BASE_URL = "http://localhost:8080"
USERNAME = "admin"
PASSWORD = "CYsWGZY7y23vB7Su"

if __name__ == '__main__':
    dag_id = "ep4"
    sample_uuid = "sam-001002"
    dicom_dir = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/ep4_sds_dicom/primary/sub-1/sam-1"
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/airflow/run_sam/out/" + str(sample_uuid)

    log_dir = os.path.join(workspace, "logs")
    os.makedirs(log_dir, exist_ok=True)

    body_model = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/body/imagewise/UNet/test_training_t1_batch16/best_accuracy-8"
    lung_model = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/lung/imagewise/UNet/test_training_T1_batch16/best_accuracy-5"

    params = {"sample_uuid": sample_uuid,
              "dicom_dir": dicom_dir,
              "workspace": workspace,
              "log_dir": log_dir,
              "body_model": body_model,
              "lung_model": lung_model}

    # Trigger workflow URL
    trigger_url = f"{BASE_URL}/api/v1/dags/{dag_id}/dagRuns"

    # Trigger the DAG via REST API
    response = requests.post(
        trigger_url,
        auth=HTTPBasicAuth(USERNAME, PASSWORD),
        headers={"Content-Type": "application/json"},
        data=json.dumps({"conf": params})  # Pass parameters here
    )

    if response.status_code == 200:
        print("DAGs fetched successfully!")
        dags = response.json()
        print("DAGs List:")
        for dag in dags.get("dags", []):
            print(f"- {dag['dag_id']}: {dag['description'] or 'No description'}")
    else:
        print("Failed to fetch DAGs")
        print("Response:", response.text)


