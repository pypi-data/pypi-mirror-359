import configparser
from datetime import timedelta

from airflow.models.dag import DAG

import ep1_download_data, ep1_create_seed_points, ep1_intensity_mapping_and_clustering, ep1_centreline_annotation, ep1_grow_into_clusters, ep1_convert_ex_to_ip_ex2ip

workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep1/workflow_1_generate_personalised_anatomical_model_of_lung/workspace"

assay_uuid = ""
assay_seek_id = 10


platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"
platform_configs = configparser.ConfigParser()
platform_configs.read(platform_config_file)

with DAG(
        dag_id="9fbefab4-4650-11f0-917d-484d7e9beb16",
        dag_display_name="EP1: generate personalised anatomical model of lung",
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
        description="Generate personalised anatomical model of lung",
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
    t1 = ep1_download_data.get_task(dag)
    t2 = ep1_create_seed_points.get_task(dag)
    t3 = ep1_intensity_mapping_and_clustering.get_task(dag)
    t4 = ep1_centreline_annotation.get_task(dag)
    t5 = ep1_grow_into_clusters.get_task(dag)
    t6 = ep1_convert_ex_to_ip_ex2ip.get_task(dag)

    t1 >> t2 >> t3 >> t4 >> t5 >> t6
