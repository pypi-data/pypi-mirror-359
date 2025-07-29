from pathlib import Path

from digitaltwins import Querier

if __name__ == '__main__':
    config_file = Path(r"/home/clin864/opt/digitaltwins-api/my_workspace/configs-public-demo.ini")

    querier = Querier(config_file)

    print("programs:")
    programs = querier.get_programs(get_details=True)
    print(programs)

    print("program 1:")
    program_id = 1
    program = querier.get_program(program_id)
    print(program)

    print("projects:")
    projects = querier.get_projects(get_details=True)
    print(projects)

    print("project 2:")
    project_id = 2
    project = querier.get_project(project_id)
    print(project)

    print("investigations:")
    investigations = querier.get_investigations()
    print(investigations)

    print("investigation 1:")
    investigation_id = 1
    investigation = querier.get_investigation(investigation_id)
    print(investigation)

    print("studies:")
    studies = querier.get_investigations()
    print(studies)

    print("study 1:")
    study_id = 1
    study = querier.get_study(study_id)
    print(study)

    print("assays:")
    assays = querier.get_assays()
    print(assays)

    print("assay 1:")
    assay_id = 1
    assay = querier.get_assay(assay_id)
    print(assay)
    # print("assay params:")
    # assay = querier.get_assay(assay_id, get_params=True)
    # print(assay)

    print("SOPs:")
    sops = querier.get_sops()
    print(sops)

    # # workflow dataset
    print("SOP 1:")
    sop_id = 1
    sop = querier.get_sop(sop_id, get_cwl=False)
    # sop = querier.get_sop(sop_id, get_cwl=True)
    print(sop)


    # # Object dependencies can be collected by get_dependencies(data, target). e.g.
    # # EX 1
    # print("projects in program: {program_id}".format(program_id=program_id))
    # program = querier.get_program(program_id=program_id)
    # projects = querier.get_dependencies(program, "projects")
    # print(projects)
    # # EX 2
    # print("investigations in projects: {project_id}".format(project_id=project_id))
    # project = querier.get_project(project_id=project_id)
    # investigations = querier.get_dependencies(project, "investigations")
    # print(investigations)
    #
    # print("datasets:")
    # datasets = querier.get_datasets()
    # print(datasets)
    # print("dataset:")
    # dataset = querier.get_dataset(dataset_uuid=datasets[0].get("dataset_uuid"))
    # print(dataset)
    # print("workflow datasets:")
    # datasets = querier.get_datasets(categories=["workflow"])
    # print(datasets)
    #
    # print("sample types:")
    # sample_types = querier.get_dataset_sample_types(dataset_uuid="6ba38e34-ee5d-11ef-917d-484d7e9beb16")
    # print(sample_types)
    #
    # print("dataset samples with sample_type==:'ax dyn pre'")
    # samples = querier.get_dataset_samples(dataset_uuid="6ba38e34-ee5d-11ef-917d-484d7e9beb16", sample_type="ax dyn pre")
    # print(samples)


