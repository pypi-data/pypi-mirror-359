import os
import shutil
from pathlib import Path
class Uploader(object):

    def __init__(self, connection):
        """
        Constructor
        """
        self._connection = connection


    def upload(self, dataset_dir):
        dataset_dir = Path(dataset_dir)
        self._verify_dataset(dataset_dir)

        # get dataset (submitter) id
        dataset_id = self._generate_dataset_id()

        os.makedirs(self._dir_tmp, exist_ok=True)

        dataset_dir_tmp = self._dir_tmp.joinpath(dataset_id)
        shutil.copytree(str(dataset_dir), str(dataset_dir_tmp))
        dataset_dir = dataset_dir_tmp

        # Upload metadata to Gen3
        self.upload_metadata(dataset_dir)
        # Upload the actual files to iRODS
        self.upload_dataset(dataset_dir)

        if self._dir_tmp.is_dir:
            shutil.rmtree(str(self._dir_tmp))

        print("Dataset uploaded: " + str(dataset_id))

    def upload_metadata(self, dataset_dir):
        meta_dir = self._meta_dir_tmp
        # convert sds metadata to gen3
        meta_convertor = MetadataConvertor(program=self._program, project=self._project, experiment=dataset_dir.name)
        meta_convertor.execute(source_dir=dataset_dir, dest_dir=meta_dir)

        # upload metadata
        meta_uploader = MetadataUploader(self._gen3_endpoint, str(self._gen3_cred_file))

        for filename in self._meta_files:
            print("Uploading: " + str(filename))
            file = meta_dir.joinpath(filename)
            meta_uploader.execute(program=self._program, project=self._project, file=str(file))

        # delete the temporary metadata dir
        if meta_dir.is_dir:
            shutil.rmtree(meta_dir)

    def upload_dataset(self, dataset_dir):
        irods = IRODS(self._configs)
        irods.upload(dataset_dir)

    def _verify_dataset(self, dataset_dir):
        if dataset_dir.is_dir():
            dataset_name = dataset_dir.name
        else:
            raise NotADirectoryError("Dataset directory not found")

        # check if dataset exists
        # todo
        pass

    def _generate_dataset_id(self, count=0):
        if count >= self._MAX_ATTEMPTS:
            raise ValueError("Max attempts {count} exceeded. Please try submitting again. If the error persists, "
                             "please contact the developers".format(count=count))
        # list datasets
        querier = Querier(self._config_file)

        datasets = list()
        try:
            datasets = querier.get_datasets(program=self._program, project=self._project)
        except Exception:
            time.sleep(2)
            self._generate_dataset_id(count=count + 1)

        dataset_ids = list()
        for dataset in datasets:
            id = dataset.get_id()
            dataset_ids.append(id)

        if len(datasets) > 0:
            dataset_ids.sort()
            latest_dataset = dataset_ids[-1]
            elements = re.split('_|-', latest_dataset)
            latest_id = elements[self._dataset_id_index]
            new_id = int(latest_id) + 1
            new_dataset_id = self._dataset_submitter_id_template.format(program=self._program, project=self._project, id=new_id)
        else:
            return self._dataset_submitter_id_template.format(program=self._program, project=self._project, id="1")

        return new_dataset_id
