"""
Example for generating a SDS primary dataset
"""
import os
from pathlib import Path

from sparc_me import Dataset, Subject, Sample


def add_dataset_description(dataset, save_dir):
    """
    the values can be filled in by 2 methods, set_field() or set_field_using_row_name().

    This example will use Dataset.set_field()
    # You can get the row_index by looking at
    #   1. the saved metadata file dataset_description.xlsx. Excel index starts from 1 where index 1 is the header row. so actual data index starts from 2.
    #   2. or the DataFrame object in the python code. dataset._dataset.dataset_description.metadata
    """

    metadata = dataset.get_metadata(metadata_file='dataset_description')
    metadata.add_values(
        element='Type',
        values='Experimental')
    metadata.add_values(
        element='Title',
        values='Dynamic contrast-enhanced magnetic resonance images of breast cancer patients with tumor locations (Duke-Breast-Cancer-MRI)')
    metadata.add_values(
        element='Subtitle',
        values='')
    metadata.add_values(
        element='Keywords',
        values=['breast'])
    metadata.add_values(
        element='Funding',
        values='12L')
    metadata.add_values(
        element='Study purpose',
        values='')
    metadata.add_values(
        element='Study data Collection',
        values='')
    metadata.add_values(
        element='Study primary conclusion',
        values='')
    metadata.add_values(
        element='Study organ system',
        values='breast')
    metadata.add_values(
        element='Study approach',
        values='')
    metadata.add_values(
        element='Study technique',
        values='')
    metadata.add_values(
        element='Contributor name',
        values=['Lin, Chinchien', '', ''])
    metadata.add_values(
        element='Contributor orcid',
        values=['', '', ''])
    metadata.add_values(
        element='Identifier',
        values='')
    metadata.add_values(
        element='Identifier description',
        values='')
    metadata.add_values(
        element='Relation type',
        values='')
    metadata.add_values(
        element='Identifier type',
        values='')
    metadata.add_values(
        element='Contributor affiliation',
        values=['', '', ''])
    metadata.add_values(
        element='Contributor role',
        values=['', '', ''])

    # dataset.save_metadata(save_dir)
    metadata.save(os.path.join(save_dir, "dataset_description.xlsx"))
    return dataset


if __name__ == '__main__':
    save_dir = str(Path(r"./ep4_sds_dicom_tmp"))
    # save_dir = str(Path(r"T:\sandbox\clin864\ep4_sds_dicom"))

    # Creating a SDS dataset from template
    dataset = Dataset()
    dataset.load_dataset(from_template=True, version="2.0.0")
    dataset.set_path(save_dir)
    dataset.save()

    # dataset_descriptions
    add_dataset_description(dataset, save_dir=save_dir)

    # subjects & samples & manifests
    subjects = []

    # sub-001
    subject = Subject()
    subject.set_values({
        # "subject id": "sub-001",
        "age": "041Y",
        "sex": "F",
        "species": "human",
        "age category": "Middle Aged Stage",
        "age range (min)": "40",
        "age range (max)": "65"
    })

    samples = []
    sample = Sample()

    sample.add_path(str(Path(r"/home/clin864/eresearch/projects/clinical_Duke_cancer/manifest-1607053360376/Duke-Breast-Cancer-MRI/Breast_MRI_001/1.3.6.1.4.1.14519.5.2.1.186051521067863971269584893740842397538/1.3.6.1.4.1.14519.5.2.1.175414966301645518238419021688341658582")))
    samples.append(sample)

    subject.add_samples(samples)
    subjects.append(subject)

    dataset.add_subjects(subjects)

    # Updating sample metadata
    subject = dataset.get_subject("sub-1")
    sample = subject.get_sample("sam-1")
    sample.set_values({
        "sample experimental group": "experimental",
        "sample type": "mri",
        "sample anatomical location": "breast"
    })

    dataset.save()
