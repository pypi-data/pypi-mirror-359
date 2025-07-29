from pathlib import Path
import configparser
import os
from datetime import timedelta

from airflow.models.dag import DAG

import example_step_1, example_step_2

assay_seek_id = None

with DAG(
        dag_id="example_workflow",
        dag_display_name="example_workflow",
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
        description="example_workflow",
        # schedule_interval='@once',
        # schedule_interval=None,  # Ensures the DAG only runs manually
        catchup=False,  # Avoids running past dates if backfilling is enabled
        # schedule=timedelta(days=1),
        # start_date=datetime(2024, 10, 9),
        # catchup=False,
        tags=["12L"],
        # params={
        #
        #   }
) as dag:
    t1 = example_step_1.get_task(dag)
    t2 = example_step_2.get_task(dag)

    t1 >> t2


if __name__ == "__main__":
    dag.test()
