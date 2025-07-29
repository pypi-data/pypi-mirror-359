import configparser
from datetime import timedelta

from airflow.models.dag import DAG

import pretend_download_data, pretend_create_nifti, pretend_segment, pretend_create_point_cloud, pretend_create_mesh, pretend_add_to_dataset

with DAG(
        dag_id="2",
        dag_display_name="EP4: automated torso model generation",
        default_args={
            "retries": 1,
            "retry_delay": timedelta(minutes=5)
        },
        description="EP4: automated torso model generation",
        schedule_interval=None,  # Ensures the DAG only runs manually
        catchup=False,  # Avoids running past dates if backfilling is enabled
        tags=["12L"],
        params={
            "assay_seek_id": 2
        }
) as dag:
    t1 = pretend_download_data.get_task(dag)
    t2 = pretend_create_nifti.get_task(dag)
    t3 = pretend_segment.get_task(dag)
    t4 = pretend_create_point_cloud.get_task(dag)
    t5 = pretend_create_mesh.get_task(dag)
    t6 = pretend_add_to_dataset.get_task(dag)

    t1 >> t2 >> t3 >> t4 >> t5 >> t6
