import json
import os
import shutil

from collections import defaultdict

import requests
from requests.auth import HTTPBasicAuth

from airflow import DAG
from airflow.operators.python import PythonOperator


def get_assay(assay_id, get_params):
    # TODO. this will be replaced by digitaltwins.querier.get_assay(assay_id, get_params=get_params)
    assay = None
    if str(assay_id) == "2":
        assay = {'id': '2', 'type': 'assays', 'attributes': {'policy': {'access': 'no_access', 'permissions': [{'resource': {'id': '4', 'type': 'projects'}, 'access': 'download'}, {'resource': {'id': '3', 'type': 'people'}, 'access': 'edit'}, {'resource': {'id': '2', 'type': 'people'}, 'access': 'manage'}, {'resource': {'id': '4', 'type': 'people'}, 'access': 'manage'}]}, 'discussion_links': [], 'snapshots': [], 'title': 'Assay 1: Run automated tumour position reporting (Model Generation) on Duke University breast MRI dataset', 'description': 'Using workflow 1: automated tumour position reporting (Model Generation)', 'other_creators': '', 'position': None, 'assay_class': {'title': 'Experimental assay', 'key': 'EXP', 'description': None}, 'assay_type': {'label': 'Experimental Assay Type', 'uri': 'http://jermontology.org/ontology/JERMOntology#Experimental_assay_type'}, 'technology_type': {'label': 'Technology Type', 'uri': 'http://jermontology.org/ontology/JERMOntology#Technology_type'}, 'tags': [], 'creators': [{'profile': '/people/1', 'family_name': 'Lin', 'given_name': 'Chinchien', 'affiliation': 'Default Institution, University of Auckland, Auckland Bioengineering Institute', 'orcid': None}, {'profile': '/people/2', 'family_name': 'Babarenda Gamage', 'given_name': 'Prasad', 'affiliation': 'University of Auckland, Auckland Bioengineering Institute', 'orcid': None}, {'profile': '/people/3', 'family_name': 'Xu', 'given_name': 'Jiali', 'affiliation': 'University of Auckland, Auckland Bioengineering Institute', 'orcid': None}]}, 'relationships': {'creators': {'data': [{'id': '1', 'type': 'people'}, {'id': '2', 'type': 'people'}, {'id': '3', 'type': 'people'}]}, 'submitter': {'data': [{'id': '1', 'type': 'people'}]}, 'organisms': {'data': []}, 'human_diseases': {'data': []}, 'people': {'data': [{'id': '1', 'type': 'people'}, {'id': '2', 'type': 'people'}, {'id': '3', 'type': 'people'}]}, 'projects': {'data': [{'id': '4', 'type': 'projects'}]}, 'investigation': {'data': {'id': '2', 'type': 'investigations'}}, 'study': {'data': {'id': '2', 'type': 'studies'}}, 'data_files': {'data': []}, 'samples': {'data': []}, 'models': {'data': []}, 'sops': {'data': [{'id': '1', 'type': 'sops'}]}, 'publications': {'data': []}, 'placeholders': {'data': []}, 'documents': {'data': []}}, 'links': {'self': '/assays/2'}, 'meta': {'created': '2024-12-04T02:54:23.000Z', 'modified': '2025-02-18T21:47:10.000Z', 'api_version': '0.3', 'base_url': 'http://localhost:3000', 'uuid': 'fd7095a0-9418-013d-75f3-0242ac120005'}, 'params': {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'assay_seek_id': 2, 'workflow_seek_id': 1, 'cohort': 2, 'ready': True, 'inputs': [{'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'pca_model', 'dataset_uuid': 'd8f0b6d4-65ae-11ef-917d-484d7e9beb16', 'sample_type': '', 'category': 'model'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'mri', 'dataset_uuid': '6ba38e34-ee5d-11ef-917d-484d7e9beb16', 'sample_type': 'ax dyn pre', 'category': 'measurement'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'segmentation_model_lung', 'dataset_uuid': '660eac41-5f53-11ef-917d-484d7e9beb16', 'sample_type': '', 'category': 'model'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'segmentation_model_skin', 'dataset_uuid': '660eac40-5f53-11ef-917d-484d7e9beb16', 'sample_type': '', 'category': 'model'}], 'outputs': [{'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'nrrd', 'dataset_name': 'New Dataset 1', 'sample_name': 'nrrd', 'category': 'measurement'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'nifti', 'dataset_name': 'New Dataset 1', 'sample_name': 'nifti', 'category': 'measurement'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'mesh', 'dataset_name': 'New Dataset 1', 'sample_name': 'mesh', 'category': 'measurement'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'point_cloud', 'dataset_name': 'New Dataset 1', 'sample_name': 'point_cloud', 'category': 'measurement'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'segmentation', 'dataset_name': 'New Dataset 1', 'sample_name': 'segmentation', 'category': 'measurement'}]}}
    elif str(assay_id) == "18":
        # ep2
        assay = {'id': '18', 'type': 'assays', 'attributes': {'policy': {'access': 'no_access', 'permissions': [{'resource': {'id': '7', 'type': 'projects'}, 'access': 'manage'}]}, 'discussion_links': [], 'snapshots': [], 'title': 'Generate personalised model', 'description': '', 'other_creators': '', 'position': None, 'assay_class': {'title': 'Experimental assay', 'key': 'EXP', 'description': None}, 'assay_type': {'label': 'Experimental Assay Type', 'uri': 'http://jermontology.org/ontology/JERMOntology#Experimental_assay_type'}, 'technology_type': {'label': 'Technology Type', 'uri': 'http://jermontology.org/ontology/JERMOntology#Technology_type'}, 'tags': [], 'creators': [{'profile': '/people/1', 'family_name': 'Lin', 'given_name': 'Chinchien', 'affiliation': 'Auckland Bioengineering Institute', 'orcid': None}]}, 'relationships': {'creators': {'data': [{'id': '1', 'type': 'people'}]}, 'submitter': {'data': [{'id': '1', 'type': 'people'}]}, 'organisms': {'data': []}, 'human_diseases': {'data': []}, 'people': {'data': [{'id': '1', 'type': 'people'}]}, 'projects': {'data': [{'id': '7', 'type': 'projects'}]}, 'investigation': {'data': {'id': '4', 'type': 'investigations'}}, 'study': {'data': {'id': '5', 'type': 'studies'}}, 'data_files': {'data': []}, 'samples': {'data': []}, 'models': {'data': []}, 'sops': {'data': [{'id': '21', 'type': 'sops'}]}, 'publications': {'data': []}, 'placeholders': {'data': []}, 'documents': {'data': []}}, 'links': {'self': '/assays/18'}, 'meta': {'created': '2025-03-25T00:44:59.000Z', 'modified': '2025-06-10T03:50:41.000Z', 'api_version': '0.3', 'base_url': 'http://localhost:3000', 'uuid': '4dfc76e0-eb40-013d-755e-0242ac1c0004'}, 'params': {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'assay_seek_id': 18, 'workflow_seek_id': 21, 'cohort': 2, 'ready': True, 'inputs': [{'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'sternum_mesh', 'dataset_uuid': 'ecc89f5e-457e-11f0-917d-484d7e9beb16', 'sample_type': 'Sternum', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'ribs_mesh', 'dataset_uuid': 'ecc89f5e-457e-11f0-917d-484d7e9beb16', 'sample_type': 'Ribs', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_stl_l_scapula', 'dataset_uuid': 'ecc89f5e-457e-11f0-917d-484d7e9beb16', 'sample_type': 'L_Scapula', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_stl_r_scapula', 'dataset_uuid': 'ecc89f5e-457e-11f0-917d-484d7e9beb16', 'sample_type': 'R_Scapula', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_stl_r_humerus', 'dataset_uuid': 'ecc89f5e-457e-11f0-917d-484d7e9beb16', 'sample_type': 'R_Humerus', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_stl_l_clavicle', 'dataset_uuid': 'ecc89f5e-457e-11f0-917d-484d7e9beb16', 'sample_type': 'L_Clavicle', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_stl_r_clavicle', 'dataset_uuid': 'ecc89f5e-457e-11f0-917d-484d7e9beb16', 'sample_type': 'R_Clavicle', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_stl_l_humerus', 'dataset_uuid': 'ecc89f5e-457e-11f0-917d-484d7e9beb16', 'sample_type': 'L_Humerus', 'category': 'measurement'}], 'outputs': [{'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_ply_thorax', 'dataset_name': 'New Dataset 1', 'sample_name': 'surface_mesh_ply_thorax', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_ply_r_humerus', 'dataset_name': 'New Dataset 1', 'sample_name': 'surface_mesh_ply_r_humerus', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_ply_l_humerus', 'dataset_name': 'New Dataset 1', 'sample_name': 'surface_mesh_ply_l_humerus', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_ply_r_scapula', 'dataset_name': 'New Dataset 1', 'sample_name': 'surface_mesh_ply_r_scapula', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_ply_l_scapula', 'dataset_name': 'New Dataset 1', 'sample_name': 'surface_mesh_ply_l_scapula', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_ply_r_clavicle', 'dataset_name': 'New Dataset 1', 'sample_name': 'surface_mesh_ply_r_clavicle', 'category': 'measurement'}, {'assay_uuid': '2375b52e-4646-11f0-917d-484d7e9beb16', 'name': 'surface_mesh_ply_l_clavicle', 'dataset_name': 'New Dataset 1', 'sample_name': 'surface_mesh_ply_l_clavicle', 'category': 'measurement'}]}}
    elif str(assay_id) == "10":
        #ep1
        assay = {'id': '10', 'type': 'assays', 'attributes': {'policy': {'access': 'no_access', 'permissions': [{'resource': {'id': '6', 'type': 'projects'}, 'access': 'manage'}]}, 'discussion_links': [], 'snapshots': [], 'title': 'Generate personalised anatomical model of lung on ASPIRE data', 'description': '', 'other_creators': '', 'position': None, 'assay_class': {'title': 'Experimental assay', 'key': 'EXP', 'description': None}, 'assay_type': {'label': 'Experimental Assay Type', 'uri': 'http://jermontology.org/ontology/JERMOntology#Experimental_assay_type'}, 'technology_type': {'label': 'Technology Type', 'uri': 'http://jermontology.org/ontology/JERMOntology#Technology_type'}, 'tags': [], 'creators': [{'profile': '/people/1', 'family_name': 'Lin', 'given_name': 'Chinchien', 'affiliation': 'Auckland Bioengineering Institute', 'orcid': None}]}, 'relationships': {'creators': {'data': [{'id': '1', 'type': 'people'}]}, 'submitter': {'data': [{'id': '1', 'type': 'people'}]}, 'organisms': {'data': []}, 'human_diseases': {'data': []}, 'people': {'data': [{'id': '1', 'type': 'people'}]}, 'projects': {'data': [{'id': '6', 'type': 'projects'}]}, 'investigation': {'data': {'id': '3', 'type': 'investigations'}}, 'study': {'data': {'id': '4', 'type': 'studies'}}, 'data_files': {'data': []}, 'samples': {'data': []}, 'models': {'data': []}, 'sops': {'data': [{'id': '22', 'type': 'sops'}]}, 'publications': {'data': []}, 'placeholders': {'data': []}, 'documents': {'data': []}}, 'links': {'self': '/assays/10'}, 'meta': {'created': '2025-03-24T21:42:30.000Z', 'modified': '2025-06-10T23:11:06.000Z', 'api_version': '0.3', 'base_url': 'http://localhost:3000', 'uuid': 'cf9aafe0-eb26-013d-755f-0242ac1c0004'}, 'params': {'assay_uuid': '08573ca4-4655-11f0-917d-484d7e9beb16', 'assay_seek_id': 10, 'workflow_seek_id': 22, 'cohort': 2, 'ready': True, 'inputs': [{'assay_uuid': '08573ca4-4655-11f0-917d-484d7e9beb16', 'name': 'lobe_ply_meshes', 'dataset_uuid': '1666a328-4652-11f0-917d-484d7e9beb16', 'sample_type': 'segmented', 'category': 'measurement'}, {'assay_uuid': '08573ca4-4655-11f0-917d-484d7e9beb16', 'name': 'mpa_segmentations', 'dataset_uuid': '1666a328-4652-11f0-917d-484d7e9beb16', 'sample_type': 'segmented', 'category': 'measurement'}, {'assay_uuid': '08573ca4-4655-11f0-917d-484d7e9beb16', 'name': 'masked_mha_image', 'dataset_uuid': '1666a328-4652-11f0-917d-484d7e9beb16', 'sample_type': 'segmented', 'category': 'measurement'}], 'outputs': [{'assay_uuid': '08573ca4-4655-11f0-917d-484d7e9beb16', 'name': 'clusters', 'dataset_name': 'New Dataset 1', 'sample_name': 'clusters', 'category': 'measurement'}, {'assay_uuid': '08573ca4-4655-11f0-917d-484d7e9beb16', 'name': '1d_personalised_full_arterial_mesh_ip_format', 'dataset_name': 'New Dataset 1', 'sample_name': '1d_personalised_full_arterial_mesh_ip_format', 'category': 'measurement'}, {'assay_uuid': '08573ca4-4655-11f0-917d-484d7e9beb16', 'name': 'annotations_txt', 'dataset_name': 'New Dataset 1', 'sample_name': 'annotations_txt', 'category': 'measurement'}]}}

    return assay


def get_dataset_samples(dataset_uuid, sample_type):
    samples = [{'dataset_uuid': '6ba38e34-ee5d-11ef-917d-484d7e9beb16', 'subject_uuid': '02ad0960-ee70-11ef-917d-484d7e9beb16', 'sample_uuid': 'f4137f72-ee71-11ef-917d-484d7e9beb16', 'subject_id': 'sub-1', 'sample_id': 'sam-1', 'was_derived_from_sample': None, 'pool_id': None, 'sample_experimental_group': None, 'sample_type': 'ax dyn pre', 'sample_anatomical_location': 'breast', 'also_in_dataset': None, 'member_of': None, 'laboratory_internal_id': None, 'date_of_derivation': None, 'experimental_log_file_path': None, 'reference_atlas': None, 'pathology': None, 'laterality': None, 'cell_type': None, 'plane_of_section': None, 'protocol_title': None, 'protocol_url_or_doi': None}, {'dataset_uuid': '6ba38e34-ee5d-11ef-917d-484d7e9beb16', 'subject_uuid': '02ad0961-ee70-11ef-917d-484d7e9beb16', 'sample_uuid': 'f4137f77-ee71-11ef-917d-484d7e9beb16', 'subject_id': 'sub-2', 'sample_id': 'sam-1', 'was_derived_from_sample': None, 'pool_id': None, 'sample_experimental_group': None, 'sample_type': 'ax dyn pre', 'sample_anatomical_location': 'breast', 'also_in_dataset': None, 'member_of': None, 'laboratory_internal_id': None, 'date_of_derivation': None, 'experimental_log_file_path': None, 'reference_atlas': None, 'pathology': None, 'laterality': None, 'cell_type': None, 'plane_of_section': None, 'protocol_title': None, 'protocol_url_or_doi': None}]
    return samples


def download(remote_sample_path, assay_input_dir, sample_id):
    sample_path = os.path.join(assay_input_dir, sample_id)
    os.makedirs(sample_path, exist_ok=True)



def run(assay_seek_id, workspace, platform_config_file):
    # todo. get_assay will be replaced by digitaltwins API querier.get_assay
    assay = get_assay(assay_seek_id, get_params=True)
    print(assay)
    assay_params = assay.get("params")
    assay_uuid = assay_params.get("assay_uuid")
    cohort = assay_params.get("cohort")
    assay_inputs = assay_params.get("inputs")

    if str(assay_seek_id) == "2": # ep4
        workflow_dataset_uuid = "d15dbdd2-ed7a-11ef-917d-484d7e9beb16"

        assay_dir = os.path.join(workspace, assay_uuid)
        assay_inputs_dir = os.path.join(assay_dir, "inputs")

        # categorized by "category"
        categorized = defaultdict(list)
        for entry in assay_inputs:
            categorized[entry['category']].append(entry)

        inputs_model = categorized['model']
        inputs_measurement = categorized['measurement']

        # todo. downloading models
        for input in inputs_model:
            pass

        # downloading measurements
        for idx_inputs_measurement, input in enumerate(inputs_measurement):
            input_name = input.get("name")
            assay_input_dir = os.path.join(assay_inputs_dir, input_name)

            os.makedirs(assay_input_dir, exist_ok=True)

            dataset_uuid = input.get("dataset_uuid")
            sample_type = input.get("sample_type")

            # todo. this will be replaced by digitaltwins querier.get_dataset_samples
            samples = get_dataset_samples(dataset_uuid, sample_type)
            samples = samples[0:cohort]
            for sample in samples:
                subject_id = sample.get("subject_id")
                sample_id = sample.get("sample_id")
                subject_uuid = sample.get("subject_uuid")
                sample_uuid = sample.get("sample_uuid")

                remote_sample_path = dataset_uuid + "/primary/" + subject_id + "/" + sample_id
                local_sample_path_tmp = assay_input_dir + "/" + sample_id
                if os.path.exists(local_sample_path_tmp):
                    shutil.rmtree(local_sample_path_tmp)

                # todo
                download(remote_sample_path, assay_input_dir, sample_id)

                local_sample_path = assay_input_dir + "/" + subject_uuid + "/" + sample_uuid
                if os.path.exists(local_sample_path):
                    shutil.rmtree(local_sample_path)
                os.makedirs(os.path.dirname(local_sample_path), exist_ok=True)

                shutil.move(local_sample_path_tmp, local_sample_path)

                if idx_inputs_measurement == len(inputs_measurement)-1:
                    params = {
                        "subject_uuid": subject_uuid,
                        "assay_seek_id": assay_seek_id,
                        "workspace": None,
                        # "platform_configs": None,
                    }

                    # trigger workflow
                    airflow_api_url = "http://130.216.208.137:8080/api/v1"
                    dag_url = f"{airflow_api_url}/dags/{workflow_dataset_uuid}/dagRuns"
                    response = requests.post(
                        dag_url,
                        auth=HTTPBasicAuth("admin", "PgKFTfe4B2C7ragN"),
                        headers={"Content-Type": "application/json"},
                        data=json.dumps({"conf": params})
                    )
    elif str(assay_seek_id) == "18": # ep2
        workflow_dataset_uuid = "9ccb0f66-4581-11f0-917d-484d7e9beb16"
        params = {
            "assay_seek_id": assay_seek_id,
            # "workspace": None,
        }
        airflow_api_url = "http://130.216.208.137:8080/api/v1"
        dag_url = f"{airflow_api_url}/dags/{workflow_dataset_uuid}/dagRuns"

        for cohort_idx in range(cohort):
            response = requests.post(
                dag_url,
                auth=HTTPBasicAuth("admin", "PgKFTfe4B2C7ragN"),
                headers={"Content-Type": "application/json"},
                data=json.dumps({"conf": params})
            )
    elif str(assay_seek_id) == "10": # ep1
        workflow_dataset_uuid = "9fbefab4-4650-11f0-917d-484d7e9beb16"
        params = {
            "assay_seek_id": assay_seek_id,
            # "workspace": None,
        }
        airflow_api_url = "http://130.216.208.137:8080/api/v1"
        dag_url = f"{airflow_api_url}/dags/{workflow_dataset_uuid}/dagRuns"

        print("Triggering workflow" + workflow_dataset_uuid)
        for cohort_idx in range(cohort):
            response = requests.post(
                dag_url,
                auth=HTTPBasicAuth("admin", "PgKFTfe4B2C7ragN"),
                headers={"Content-Type": "application/json"},
                data=json.dumps({"conf": params})
            )




def exec(**kwargs):
    assay_seek_id = kwargs['dag_run'].conf.get('assay_seek_id', kwargs['params'].get('assay_seek_id'))
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/preprocessor/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    run(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)


def get_task(dag: DAG):
    task_id = "download_data_pre"
    return PythonOperator(
        task_id=task_id,
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    # assay_seek_id = 2 # ep4
    assay_seek_id = 18 # ep2
    # assay_seek_id = 10 # ep1
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/preprocessor/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    run(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)

