import os


from airflow import DAG
from airflow.operators.python import PythonOperator


def create_mesh(assay_seek_id, workspace, platform_config_file):
    import time
    time.sleep(5)


def exec(**kwargs):
    assay_seek_id = kwargs['dag_run'].conf.get('assay_seek_id', kwargs['params'].get('assay_seek_id'))
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/workflow_model_generation/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    create_mesh(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)


def get_task(dag: DAG):
    task_id = "create_mesh"
    return PythonOperator(
        task_id=task_id,
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    assay_seek_id = 2
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/workflow_model_generation/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    # log_dir = os.path.join(workspace, "logs")
    # os.makedirs(log_dir, exist_ok=True)

    create_mesh(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)
