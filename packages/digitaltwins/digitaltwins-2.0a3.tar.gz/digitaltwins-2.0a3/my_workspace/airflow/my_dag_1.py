import textwrap
from datetime import datetime, timedelta

# The DAG object; we'll need this to instantiate a DAG
from airflow.models.dag import DAG

# Operators; we need this to operate!
from airflow.operators.bash import BashOperator

with DAG(
        "my_dag_1",
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
        description="My test DAG",
        schedule=timedelta(days=1),
        start_date=datetime(2024, 10, 1),
        catchup=False,
        tags=["example"],
) as dag:
    t1_templated_command = textwrap.dedent(
        """
    echo "creating nifti file"
    """
    )

    t1 = BashOperator(
        task_id="create_nifti",
        depends_on_past=False,
        bash_command=t1_templated_command,
    )

    t2_templated_command = textwrap.dedent(
        """
    echo "segmenting"
    """
    )

    t2 = BashOperator(
        task_id="segment",
        depends_on_past=False,
        bash_command=t2_templated_command,
    )

    t3_templated_command = textwrap.dedent(
        """
    echo "create_point_cloud"
    """
    )

    t3 = BashOperator(
        task_id="create_point_cloud",
        depends_on_past=False,
        bash_command=t3_templated_command,
    )

    t4_templated_command = textwrap.dedent(
        """
    echo "create_mesh"
    """
    )

    t4 = BashOperator(
        task_id="create_mesh",
        depends_on_past=False,
        bash_command=t4_templated_command,
    )

    t1 >> t2 >> t3 >> t4
