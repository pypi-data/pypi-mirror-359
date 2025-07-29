import os
import dicom2nifti

# import shutil
# import pandas as pd
# from xlrd import XLRDError

from airflow import DAG
from airflow.operators.python import PythonOperator

# from sparc_me import Dataset, Subject, Sample


def convert_DICOM_to_Nifti(dicom_folder, nii_file):
    """
    Convert a dicom folder to a single nifti file

    :param dicom_folder: path to source dicom folder
    :type dicom_folder: string
    :param nii_file: full path to the output nifti file
    :type nii_file: string
    :return:
    :rtype:
    """

    nii_folder, nii_filename = os.path.split(nii_file)

    print("Processing study {}".format(dicom_folder))
    aux_folder = nii_folder + '/temp_nifti_conv/'
    os.makedirs(os.path.dirname(aux_folder), exist_ok=True)
    # os.mkdir(os.path.dirname(aux_folder))
    # dicom2nifti.convert_directory(dicom_folder, aux_folder, compression=True, reorient=True)
    dicom2nifti.convert_directory(dicom_folder, aux_folder, compression=True, reorient=False)
    # renames the file
    for fname in os.listdir(aux_folder):
        if fname.endswith('.nii.gz'):
            print("Renaming study {} to {}".format(aux_folder + fname.title(), nii_folder + '/' + nii_filename))
            os.rename(aux_folder + fname, nii_folder + '/' + nii_filename)
            os.removedirs(aux_folder)


def create_nifti(assay_seek_id, workspace, platform_config_file):
    import time
    time.sleep(5)
    pass


def exec(**kwargs):
    assay_seek_id = kwargs['dag_run'].conf.get('assay_seek_id', kwargs['params'].get('assay_seek_id'))
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/workflow_model_generation/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    create_nifti(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)


def get_task(dag: DAG):
    task_id = "create_nifti"
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

    create_nifti(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)
