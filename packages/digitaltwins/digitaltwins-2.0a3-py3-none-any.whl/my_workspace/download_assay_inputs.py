from digitaltwins import Downloader

from pathlib import Path

if __name__ == '__main__':
    config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini")
    assay_uuid = "2788f298-0465-11f0-917d-484d7e9beb16"
    assay_id = "2" # the seek id

    downloader = Downloader(config_file)

    downloader.download_assay_inputs(assay_id=assay_id, save_dir="./tmp/assay_data")

    print("done")
