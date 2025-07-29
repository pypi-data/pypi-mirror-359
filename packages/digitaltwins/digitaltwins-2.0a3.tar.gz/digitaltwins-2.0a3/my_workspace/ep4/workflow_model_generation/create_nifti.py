import os
import dicom2nifti

import shutil
import pandas as pd
from xlrd import XLRDError

from airflow import DAG
from airflow.operators.python import PythonOperator

from sparc_me import Dataset, Subject, Sample


def get_sample_metadata(metadata_file):
    try:
        metadata = pd.read_excel(metadata_file)
    except XLRDError:
        metadata = pd.read_excel(metadata_file, engine='openpyxl')

    return metadata
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

def exec(**kwargs):
    sample_uuid = kwargs['dag_run'].conf.get('sample_uuid', kwargs['params'].get('sample_uuid'))
    workspace = kwargs['dag_run'].conf.get('workspace', kwargs['params'].get('workspace'))
    dicom_dir = workspace.joinpath(sample_uuid, "downloaded")

    workspace_nifti = os.path.join(workspace, "nifti")

    os.makedirs(workspace_nifti, exist_ok=True)

    temp_dir = os.path.join(workspace_nifti, "temp_dir")
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, sample_uuid + ".nii.gz")

    convert_DICOM_to_Nifti(dicom_dir, temp_file)

    os.makedirs(workspace_nifti, exist_ok=True)
    nifti_file = os.path.join(workspace_nifti, sample_uuid + ".nii.gz")
    shutil.copyfile(temp_file, nifti_file)

    shutil.rmtree(temp_dir)

    # Push data to XCom
    try:
        kwargs['ti'].xcom_push(key='workspace_create_nifti', value=workspace_nifti)
        kwargs['ti'].xcom_push(key='nifti_file', value=nifti_file)
    except:
        pass


def get_task(dag: DAG):
    # sample_uuid = dag.params.get("sample_uuid")
    # task_id = "create_nifti_" + str(sample_uuid)
    task_id = "create_nifti"
    return PythonOperator(
        task_id=task_id,
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    sample_uuid = "sam-001001"
    source = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/ep4_sds_dicom/primary/sub-1/sam-1"
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/airflow/single_input/out/sam-001001/nifti"
    log_dir = os.path.join(workspace, "logs")
    exec(sample_uuid = sample_uuid, dicom_dir=source, workspace=workspace, log_dir = log_dir)
