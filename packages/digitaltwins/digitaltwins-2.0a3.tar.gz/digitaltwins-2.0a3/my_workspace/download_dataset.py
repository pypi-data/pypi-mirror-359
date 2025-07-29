from digitaltwins import Downloader

from pathlib import Path

if __name__ == '__main__':
    # dataset_id = "measurement_clinical_report/primary"
    # dataset_id = "6ba38e34-ee5d-11ef-917d-484d7e9beb16"
    # dataset_id = "6ba38e34-ee5d-11ef-917d-484d7e9beb16/primary/sub-1/sam-1"
    dataset_id = "6ba38e34-ee5d-11ef-917d-484d7e9beb16"

    config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini")

    downloader = Downloader(config_file)

    downloader.download_dataset(dataset_id, save_dir="./tmp")

    print("done")
