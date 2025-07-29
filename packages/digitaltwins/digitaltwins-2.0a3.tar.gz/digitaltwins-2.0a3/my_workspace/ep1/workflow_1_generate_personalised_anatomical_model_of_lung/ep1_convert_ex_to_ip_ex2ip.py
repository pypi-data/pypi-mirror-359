from airflow import DAG
from airflow.operators.python import PythonOperator



def convert_ex_to_ip_ex2ip(assay_seek_id, workspace, platform_config_file):
    import time
    time.sleep(5)
    pass


def exec(**kwargs):
    assay_seek_id = kwargs['dag_run'].conf.get('assay_seek_id', kwargs['params'].get('assay_seek_id'))
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep1/workflow_1_generate_personalised_anatomical_model_of_lung/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    convert_ex_to_ip_ex2ip(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)


def get_task(dag: DAG):
    task_id = "convert_ex_to_ip_ex2ip"
    return PythonOperator(
        task_id=task_id,
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    pass
