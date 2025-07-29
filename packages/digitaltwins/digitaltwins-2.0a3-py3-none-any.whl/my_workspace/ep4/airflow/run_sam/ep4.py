import os
from datetime import datetime, timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator

import create_nifti, segment


sample_uuid = "sam-001001"
dicom_dir = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/ep4_sds_dicom/primary/sub-1/sam-1"
workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/airflow/run_sam/out/" + str(sample_uuid)

# Airflow automatically saves logs per task under: $AIRFLOW_HOME/logs/{dag_id}/{task_id}/{execution_date}/
# log_dir = os.path.join(workspace, "logs")
# os.makedirs(log_dir, exist_ok=True)

body_model = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/body/imagewise/UNet/test_training_t1_batch16/best_accuracy-8"
lung_model = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/lung/imagewise/UNet/test_training_T1_batch16/best_accuracy-5"

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
        params={"sample_uuid": sample_uuid,
                "dicom_dir": dicom_dir,
                "workspace": workspace,
                # "log_dir": log_dir,
                "body_model": body_model,
                "lung_model": lung_model}
) as dag:
    t1 = create_nifti.get_task(dag)
    t2 = segment.get_task(dag)
    # t3 = create_point_cloud.get_task(dag)
    # t4 = create_mesh.get_task(dag)
    #
    # t1 >> t2 >> t3 >> t4

    t1 >> t2
