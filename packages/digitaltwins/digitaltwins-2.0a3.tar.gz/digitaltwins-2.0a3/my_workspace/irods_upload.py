import os
import configparser
from pathlib import Path


# from digitaltwins.irods.irods import IRODS
from digitaltwins.irods.uploader import Uploader as IRODSUploader

if __name__ == '__main__':
    local_file_path = "/home/clin864/opt/cwl/cwltool/my_workspace/workflows/ep4/v2/workflow_1.cwl"
    irods_path = "/tempZone/home/rods/test/d15dbdd2-ed7a-11ef-917d-484d7e9beb16/primary/workflow.cwl"
    config_file = Path(r"./configs.ini")

    configs = configparser.ConfigParser()
    configs.read(config_file)

    irodsuploader = IRODSUploader(config_file)

    # irodsuploader.upload_file(local_file_path, irods_path)

    dataset_path = "/home/clin864/opt/digitaltwins-api/my_workspace/ep2/datasets/measurement_dataseta/ecc89f5e-457e-11f0-917d-484d7e9beb16"
    irodsuploader.upload_collection(dataset_path)
