from pathlib import Path
from digitaltwins.metadata.metadata_convertor import MetadataConvertor

if __name__ == '__main__':
    program = "program_1"
    project = "project_1"
    dataset_id = "dataset_1"
    source_dir = Path(r"../resources/example_sds_dataset")
    dest_dir = Path(r"./tmp")

    meta_convertor = MetadataConvertor(program=program, project=project, experiment=dataset_id)
    meta_convertor.execute(source_dir=source_dir, dest_dir=dest_dir)
