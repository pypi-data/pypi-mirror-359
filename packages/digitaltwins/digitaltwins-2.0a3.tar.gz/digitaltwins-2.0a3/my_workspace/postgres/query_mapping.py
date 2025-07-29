from pathlib import Path

from digitaltwins.core.connection import Connection
from digitaltwins.metadata.querier import Querier

if __name__ == '__main__':
    config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/postgres/configs.ini")

    connection = Connection(config_file)
    connection.connect()

    querier = Querier(connection)

    programs = querier.get_programs()
    print("programs: " + str(programs))

    projects = querier.get_projects()
    print("projects: " + str(projects))

    datasets = querier.get_datasets()
    print("datasets: " + str(datasets))

    datasets = querier.get_datasets(mappings={"title": "male"})
    print("filtered datasets (title containing 'male'): " + str(datasets))
    datasets = querier.get_datasets(mappings={"title": "heart"})
    print("filtered datasets (title containing 'heart'): : " + str(datasets))
    # datasets = querier.get_datasets(mappings={"keyword": "electrophysiology"})
    # print("filtered datasets (keyword containing 'electrophysiology'): : " + str(datasets))
    datasets = querier.get_datasets(mappings={"dataset_type": "workflow"})
    print("filtered datasets (dataset_type == 'workflow'): : " + str(datasets))

    dataset_descriptions = querier.get_dataset_descriptions(dataset_uuid="b958057a-0753-11ef-9766-484d7e9beb16")
    print("dataset_descriptions: ")
    print(dataset_descriptions)

    subjects = querier.get_subjects(dataset_uuid="b958057a-0753-11ef-9766-484d7e9beb16")
    print("subjects: " + str(subjects))

    samples = querier.get_samples(dataset_uuid="b958057a-0753-11ef-9766-484d7e9beb16")
    print("samples: " + str(samples))

    connection.disconnect()

    print("done")
