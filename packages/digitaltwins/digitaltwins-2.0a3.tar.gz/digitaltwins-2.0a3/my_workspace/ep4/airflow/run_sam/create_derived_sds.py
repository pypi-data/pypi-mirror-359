"""
Example for generating a SDS primary dataset
"""
import os
from pathlib import Path
import pandas as pd
from xlrd import XLRDError

from sparc_me import Dataset, Subject, Sample

from digitaltwins import QuerierFactory
from digitaltwins.gen3.metadata_convertor import MetadataConvertor

WORKSPACE = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/ep4/airflow/run_sam/workspace")

def fill_in_dataset_descriptions(dataset, connection_config, source_dataset):
    querier = QuerierFactory().create(connection_config)
    dataset_descriptions = querier.get_dataset_descriptions(source_dataset)

    metadata = dataset.get_metadata(metadata_file='dataset_description')
    for key, value in dataset_descriptions[0].items():
        print(key, ": ", value)
        if value:
            try:
                metadata.add_values(
                    element=key,
                    values=value)
            except ValueError:
                continue

    dataset_path = dataset.get_dataset_path()
    metadata.save(os.path.join(dataset_path, "dataset_description.xlsx"))

    print(dataset_descriptions)

def read_excel(path, sheet_name=None):
    """
    Reading Excel data as a python dataframe object

    :param path: Path to the Excel file
    :type path: str or pathlib.Path object
    :param sheet_name: Excel sheet name
    :type sheet_name: str
    :return: Data in dataframe object format
    :rtype: object
    """
    try:
        # the read_excel method return dict when sheet name is passed. otherwise a dataframe will be returned
        if sheet_name:
            metadata = pd.read_excel(path, sheet_name=sheet_name)
        else:
            metadata = pd.read_excel(path)
    except XLRDError:
        if sheet_name:
            metadata = pd.read_excel(path, sheet_name=sheet_name, engine='openpyxl')
        else:
            metadata = pd.read_excel(path, engine='openpyxl')

    return metadata
def fill_in_subjects_and_samples(dataset, connection_config, sample_uuids):
    subjects = []
    samples = []

    element_mapping_file = "/home/clin864/opt/digitaltwins-api/digitaltwins/resources/version_2_0_0/element_mapping.xlsx"
    mappings = read_excel(element_mapping_file, "subjects")
    mappings_dict = mappings.to_dict('records')

    # subjects_metadata = dataset.get_metadata(metadata_file='subjects')

    subject_uuids = list()
    querier = QuerierFactory().create(connection_config)
    for sam_idx, sample_uuid in enumerate(sample_uuids):
        # subject
        subject_metadata = querier.get_subject_by_sample(sample_uuid)[0]
        subject_uuid = subject_metadata.get("subject_uuid")

        if not subject_uuid in subject_uuids:
            subject_uuids.append(subject_uuid)

        subject = Subject()

        # mapping keys
        subject_metadata_new = dict()
        for key, value in subject_metadata.items():
            if not value:
                continue

            mapping = mappings[mappings["V2.0.0"] == key].to_dict()
            sds_key = mapping.get("element")
            if not sds_key:
                continue

            subject_metadata_new[sds_key] = value

        subject.set_values(subject_metadata_new)

        # sample
        sample = Sample()

        sample_path = WORKSPACE.joinpath(sample_uuid, "seg")
        # sample_path = WORKSPACE.joinpath(sample_uuid, "downloaded")

        sample.add_path(str(sample_path))
        samples.append(sample)

        subject.add_samples(samples)
        subjects.append(subject)

        dataset.add_subjects(subjects)

        # Updating sample metadata
        subject = dataset.get_subject("sub-" + str(len(subjects)))
        sample = subject.get_sample("sam-" + str(sam_idx+1))

        sample_metadata = querier.get_sample(sample_uuid)[0]

        sample_metadata = {k: v for k, v in sample_metadata.items() if v is not None}
        del sample_metadata["sample_uuid"]
        sample.set_values(sample_metadata)

        dataset.save()


if __name__ == '__main__':
    # samples = ["sam-001001", "sam-001002"]
    sample_uuids = ["015465ba-65ac-11ef-917d-484d7e9beb16"]

    save_dir = str(Path(r"./sds_derived"))
    if os.path.exists(save_dir):
        raise FileExistsError(f"Folder '{save_dir}' already exists.")

    # Creating a SDS dataset from template
    dataset = Dataset()
    dataset.load_dataset(from_template=True, version="2.0.0")
    dataset.set_path(save_dir)
    dataset.save()

    # fill in the dataset description from a source (workflow) dataset
    source_dataset = "ca555e58-5f51-11ef-917d-484d7e9beb16"
    # fill_in_dataset_descriptions(dataset=dataset, connection_config=r"/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini", source_dataset=source_dataset)

    fill_in_subjects_and_samples(dataset=dataset, connection_config=r"/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini", sample_uuids=sample_uuids)
