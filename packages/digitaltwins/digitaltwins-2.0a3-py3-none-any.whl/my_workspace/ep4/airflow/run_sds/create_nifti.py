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
    # TODO.
    try:
        source = kwargs['dag_run'].conf.get('primary_dataset', kwargs['params'].get('primary_dataset'))
    except:
        source = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/ep4_sds_dicom"

    try:
        project_dir = kwargs['dag_run'].conf.get('project_dir', kwargs['params'].get('project_dir'))
    except:
        project_dir = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/airflow"

    dest = os.path.join(project_dir, "ep4_sds_nifti")
    try:
        # Push data to XCom
        kwargs['ti'].xcom_push(key='sds_nifti', value=dest)
    except:
        pass
    # END OF TODO.

    # Creating an empty SDS dataset from template
    dataset = Dataset()
    dataset.load_dataset(from_template=True, version="2.0.0")
    dataset.set_path(dest)
    dataset.save()

    # get sample metadata
    samples_metadata_file = os.path.join(source, 'samples.xlsx')
    sample_metadata = get_sample_metadata(samples_metadata_file)

    # set temp dir & filename
    temp_dir = "./temp_dir"
    os.makedirs(temp_dir, exist_ok=True)
    temp_file = os.path.join(temp_dir, "temp.nii.gz")

    subjects = []
    subject_id_tmp = None
    for index, row in sample_metadata.iterrows():
        subject_id = row['subject id']
        sample_id = row['sample id']
        print("converting " + subject_id + "-" + sample_id)

        if subject_id_tmp is None:
            subject_id_tmp = subject_id
            subject = Subject()
            samples = []
        elif subject_id_tmp and subject_id_tmp != subject_id:
            sample = Sample()
            sample.add_path(temp_file)
            samples.append(sample)
            subject.add_samples(samples)
            subjects.append(subject)

            subject_id_tmp = subject_id
            subject = Subject()
            samples = []
        elif subject_id_tmp and subject_id_tmp == subject_id:
            subject.add_samples(samples)
            subjects.append(subject)

        dicom_folder = os.path.join(source, "primary", subject_id, sample_id)

        convert_DICOM_to_Nifti(dicom_folder, temp_file)


    sample = Sample()
    sample.add_path(temp_file)
    samples.append(sample)
    subject.add_samples(samples)
    subjects.append(subject)

    # adding to dataset
    dataset.add_subjects(subjects)
    dataset.save()

    # copy/overwrite metadata files
    shutil.copy(os.path.join(source, 'dataset_description.xlsx'),
                os.path.join(dest, 'dataset_description.xlsx'))
    shutil.copy(os.path.join(source, 'subjects.xlsx'),
                os.path.join(dest, 'subjects.xlsx'))
    shutil.copy(os.path.join(source, 'samples.xlsx'),
                os.path.join(dest, 'samples.xlsx'))

    shutil.rmtree(temp_dir)


def get_task(dag: DAG):
    return PythonOperator(
        task_id='create_nifti',
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    exec()
