from pathlib import Path
import configparser
import os
from datetime import timedelta

from airflow.models.dag import DAG

import pretend_download_data, pretend_create_nifti, pretend_segment, pretend_create_point_cloud, pretend_create_mesh, pretend_add_to_dataset

workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/workflow_model_generation/workspace"

# log_dir = os.path.join(workspace, "logs")
# os.makedirs(log_dir, exist_ok=True)

assay_uuid = "25e0cb08-f486-11ef-917d-484d7e9beb16"
assay_seek_id = 2
# subject_uuid = ""

# dicom_dir = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/workflow_model_generation/workspace/source"
# body_model = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/body/imagewise/UNet/test_training_t1_batch16/best_accuracy-8"
# lung_model = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/lung/imagewise/UNet/test_training_T1_batch16/best_accuracy-5"

platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"
platform_configs = configparser.ConfigParser()
platform_configs.read(platform_config_file)

with DAG(
        dag_id="d15dbdd2-ed7a-11ef-917d-484d7e9beb16",
        dag_display_name="Automated tumour position reporting - model generation",
        # These args will get passed on to each operator
        # You can override them on a per-task basis during operator initialization
        default_args={
            "depends_on_past": False,
            "email": ["clin864@aucklanduni.ac.nz"],
            "email_on_failure": False,
            "email_on_retry": False,
            "retries": 1,
            "retry_delay": timedelta(minutes=5)
        },
        description="Automated tumour position reporting - model generation",
        # schedule_interval='@once',
        schedule_interval=None,  # Ensures the DAG only runs manually
        catchup=False,  # Avoids running past dates if backfilling is enabled
        # schedule=timedelta(days=1),
        # start_date=datetime(2024, 10, 9),
        # catchup=False,
        tags=["12L"],
        params={
            # "subject_uuid": subject_uuid,
            "assay_seek_id": assay_seek_id,
            # "dicom_dir": dicom_dir,
            # "body_model": body_model,
            # "lung_model": lung_model,
            # "workspace": workspace,
            # "platform_configs": platform_configs,
            # "log_dir": log_dir,
        }
) as dag:
    t1 = pretend_download_data.get_task(dag)
    t2 = pretend_create_nifti.get_task(dag)
    t3 = pretend_segment.get_task(dag)
    t4 = pretend_create_point_cloud.get_task(dag)
    t5 = pretend_create_mesh.get_task(dag)
    t6 = pretend_add_to_dataset.get_task(dag)

    t1 >> t2 >> t3 >> t4 >> t5 >> t6
    # t2 >> t3 >> t4 >> t5
