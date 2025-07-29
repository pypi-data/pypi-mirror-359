from pathlib import Path

from digitaltwins import Uploader

def upload_assay(uploader):
    assay_data = {
        "assay_uuid": "74fbad3c-f3cf-11ef-917d-484d7e9beb16",
        # "assay_uuid": "",
        "assay_seek_id": 2,
        "workflow_seek_id": 1,
        "cohort": 2,
        "ready": True,
        "inputs": [
            {"name": "mri",
             "category": "measurement",
             "dataset_uuid": "6ba38e34-ee5d-11ef-917d-484d7e9beb16",
             "sample_type": "ax dyn pre"},
            {"name": "segmentation_model_lung",
             "category": "model",
             "dataset_uuid": "660eac40-5f53-11ef-917d-484d7e9beb16",
             "sample_type": ""},
            {"name": "segmentation_model_skin",
             "category": "model",
             "dataset_uuid": "660eac41-5f53-11ef-917d-484d7e9beb16",
             "sample_type": ""},
            {"name": "pca_model",
             "category": "model",
             "dataset_uuid": "d8f0b6d4-65ae-11ef-917d-484d7e9beb16",
             "sample_type": ""}
        ],
        "outputs": [
            {"name": "nrrd",
             "category": "measurement",
             "dataset_name": "duke_breast_mri_demo_nrrd",
             "sample_name": "nrrd"},
            {"name": "nifti",
             "category": "measurement",
             "dataset_name": "duke_breast_mri_demo_nifti",
             "sample_name": "nifti"},
            {"name": "segmentation",
             "category": "measurement",
             "dataset_name": "duke_breast_mri_demo_segmentation",
             "sample_name": "segmentation"},
            {"name": "point_cloud",
             "category": "measurement",
             "dataset_name": "duke_breast_mri_demo_point_cloud",
             "sample_name": "point_cloud"},
            {"name": "mesh",
             "category": "measurement",
             "dataset_name": "duke_breast_mri_demo_mesh",
             "sample_name": "mesh"}
        ]
    }
    uploader.upload_assay(assay_data)


if __name__ == '__main__':
    config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini")

    uploader = Uploader(config_file)
    upload_assay(uploader)


