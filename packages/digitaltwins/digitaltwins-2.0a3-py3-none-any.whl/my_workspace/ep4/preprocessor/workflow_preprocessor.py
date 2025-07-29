from pathlib import Path
import configparser
import os
from datetime import timedelta

from airflow.models.dag import DAG

import preprocessor, initialise_dataset, download_data_pre

assay_seek_id = None

with DAG(
        dag_id="preprocessor",
        dag_display_name="Preprocessor",
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
        description="Preprocessor",
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
    # t1 = preprocessor.get_task(dag)
    #
    # t1

    t1 = initialise_dataset.get_task(dag)
    t2 = download_data_pre.get_task(dag)

    t1 >> t2


if __name__ == "__main__":
    dag.test()
