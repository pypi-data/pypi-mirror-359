import os
from datetime import datetime, timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator

import create_nifti, segment


primary_dataset = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/ep4_sds_dicom"
project_dir = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/airflow"
log_dir = os.path.join(project_dir, "logs")
os.makedirs(log_dir, exist_ok=True)


with DAG(
        "ep4",
        # These args will get passed on to each operator
        # You can override them on a per-task basis during operator initialization
        default_args={
            "depends_on_past": False,
            "email": ["clin864@aucklanduni.ac.nz"],
            "email_on_failure": False,
            "email_on_retry": False,
            "retries": 1,
            "retry_delay": timedelta(minutes=5),
            # 'queue': 'bash_queue',
            # 'pool': 'backfill',
            # 'priority_weight': 10,
            # 'end_date': datetime(2016, 1, 1),
            # 'wait_for_downstream': False,
            # 'sla': timedelta(hours=2),
            # 'execution_timeout': timedelta(seconds=300),
            # 'on_failure_callback': some_function, # or list of functions
            # 'on_success_callback': some_other_function, # or list of functions
            # 'on_retry_callback': another_function, # or list of functions
            # 'sla_miss_callback': yet_another_function, # or list of functions
            # 'on_skipped_callback': another_function, #or list of functions
            # 'trigger_rule': 'all_success'
        },
        description="12L EP4 Workflow",
        # schedule_interval='@once',
        schedule_interval=None,  # Ensures the DAG only runs manually
        catchup=False,  # Avoids running past dates if backfilling is enabled
        # schedule=timedelta(days=1),
        # start_date=datetime(2024, 10, 9),
        # catchup=False,
        tags=["12L"],
        params={"project_dir": project_dir, "log_dir": log_dir, "primary_dataset": primary_dataset},
) as dag:
    t1 = create_nifti.get_task(dag)
    t2 = segment.get_task(dag)
    # t3 = create_point_cloud.get_task(dag)
    # t4 = create_mesh.get_task(dag)
    #
    # t1 >> t2 >> t3 >> t4

    t1 >> t2
