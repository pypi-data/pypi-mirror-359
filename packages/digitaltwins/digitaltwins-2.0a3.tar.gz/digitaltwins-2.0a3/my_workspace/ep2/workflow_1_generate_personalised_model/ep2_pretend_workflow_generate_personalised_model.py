from pathlib import Path
import configparser
import os
from datetime import timedelta

from airflow.models.dag import DAG

import ep2_pretend_download_data, ep2_pretend_join_sternum_and_ribs, ep2_pretend_mesh_fitting, ep2_pretend_add_to_dataset

workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep2/workflow_1_generate_personalised_model/workspace"

# log_dir = os.path.join(workspace, "logs")
# os.makedirs(log_dir, exist_ok=True)

assay_seek_id = 18

platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"
platform_configs = configparser.ConfigParser()
platform_configs.read(platform_config_file)

with DAG(
        dag_id="9ccb0f66-4581-11f0-917d-484d7e9beb16",
        dag_display_name="EP2: generate personalised model",
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
        description="Generate personalised model",
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
    t1 = ep2_pretend_download_data.get_task(dag)
    t2 = ep2_pretend_join_sternum_and_ribs.get_task(dag)
    t3 = ep2_pretend_mesh_fitting.get_task(dag)
    t4 = ep2_pretend_add_to_dataset.get_task(dag)

    t1 >> t2 >> t3 >> t4
