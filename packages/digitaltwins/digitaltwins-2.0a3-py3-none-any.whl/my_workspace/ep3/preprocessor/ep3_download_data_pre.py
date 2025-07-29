import json
import os
import shutil

from collections import defaultdict

import requests
from requests.auth import HTTPBasicAuth

from airflow import DAG
from airflow.operators.python import PythonOperator


def get_assay(assay_id, get_params):
    assay = None
    if str(assay_id) == "21":
        assay = {'id': '21', 'type': 'assays', 'attributes': {'policy': {'access': 'no_access', 'permissions': [{'resource': {'id': '8', 'type': 'projects'}, 'access': 'manage'}]}, 'discussion_links': [], 'snapshots': [], 'title': 'Selection of electrodes measured from 6 Spague-Dawley/Wistar rats', 'description': '', 'other_creators': '', 'position': None, 'assay_class': {'title': 'Experimental assay', 'key': 'EXP', 'description': None}, 'assay_type': {'label': 'Experimental Assay Type', 'uri': 'http://jermontology.org/ontology/JERMOntology#Experimental_assay_type'}, 'technology_type': {'label': 'Technology Type', 'uri': 'http://jermontology.org/ontology/JERMOntology#Technology_type'}, 'tags': [], 'creators': [{'profile': '/people/1', 'family_name': 'Lin', 'given_name': 'Chinchien', 'affiliation': 'Auckland Bioengineering Institute', 'orcid': None}]}, 'relationships': {'creators': {'data': [{'id': '1', 'type': 'people'}]}, 'submitter': {'data': [{'id': '1', 'type': 'people'}]}, 'organisms': {'data': []}, 'human_diseases': {'data': []}, 'people': {'data': [{'id': '1', 'type': 'people'}]}, 'projects': {'data': [{'id': '8', 'type': 'projects'}]}, 'investigation': {'data': {'id': '5', 'type': 'investigations'}}, 'study': {'data': {'id': '6', 'type': 'studies'}}, 'data_files': {'data': []}, 'samples': {'data': []}, 'models': {'data': []}, 'sops': {'data': [{'id': '14', 'type': 'sops'}]}, 'publications': {'data': []}, 'placeholders': {'data': []}, 'documents': {'data': []}}, 'links': {'self': '/assays/21'}, 'meta': {'created': '2025-03-25T00:51:55.000Z', 'modified': '2025-05-05T23:36:03.000Z', 'api_version': '0.3', 'base_url': 'http://localhost:3000', 'uuid': '45d5f1c0-eb41-013d-755f-0242ac1c0004'}, 'params': {'assay_uuid': '0c2acb1e-2a0a-11f0-917d-484d7e9beb16', 'assay_seek_id': 21, 'workflow_seek_id': 14, 'cohort': 6, 'ready': True, 'inputs': [], 'outputs': []}}
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

    # download data
    # todo. here temporarily copying data to jupyter env
    source = "/home/clin864/opt/digitaltwins-api/my_workspace/ep3/ep3_data_sds"
    dest = "/home/clin864/opt/digitaltwins-api/my_workspace/ep3/jupyter/ep3/ep3_data_sds"
    shutil.copytree(source, dest, dirs_exist_ok=True)


    # workflow_dataset_uuid = "d15dbdd2-ed7a-11ef-917d-484d7e9beb16"
    # cohort = assay_params.get("cohort")
    # assay_inputs = assay_params.get("inputs")
    #
    # assay_dir = os.path.join(workspace, assay_uuid)
    # assay_inputs_dir = os.path.join(assay_dir, "inputs")
    #
    # # categorized by "category"
    # categorized = defaultdict(list)
    # for entry in assay_inputs:
    #     categorized[entry['category']].append(entry)
    #
    # inputs_model = categorized['model']
    # inputs_measurement = categorized['measurement']

    # # todo. downloading models
    # for input in inputs_model:
    #     pass
    #
    # # downloading measurements
    # for idx_inputs_measurement, input in enumerate(inputs_measurement):
    #     input_name = input.get("name")
    #     assay_input_dir = os.path.join(assay_inputs_dir, input_name)
    #
    #     os.makedirs(assay_input_dir, exist_ok=True)
    #
    #     dataset_uuid = input.get("dataset_uuid")
    #     sample_type = input.get("sample_type")
    #
    #     # todo. this will be replaced by digitaltwins querier.get_dataset_samples
    #     samples = get_dataset_samples(dataset_uuid, sample_type)
    #     samples = samples[0:cohort]
    #     for sample in samples:
    #         subject_id = sample.get("subject_id")
    #         sample_id = sample.get("sample_id")
    #         subject_uuid = sample.get("subject_uuid")
    #         sample_uuid = sample.get("sample_uuid")
    #
    #         remote_sample_path = dataset_uuid + "/primary/" + subject_id + "/" + sample_id
    #         local_sample_path_tmp = assay_input_dir + "/" + sample_id
    #         if os.path.exists(local_sample_path_tmp):
    #             shutil.rmtree(local_sample_path_tmp)
    #
    #         # todo
    #         download(remote_sample_path, assay_input_dir, sample_id)
    #
    #         local_sample_path = assay_input_dir + "/" + subject_uuid + "/" + sample_uuid
    #         if os.path.exists(local_sample_path):
    #             shutil.rmtree(local_sample_path)
    #         os.makedirs(os.path.dirname(local_sample_path), exist_ok=True)
    #
    #         shutil.move(local_sample_path_tmp, local_sample_path)
    #
    #         if idx_inputs_measurement == len(inputs_measurement)-1:
    #             params = {
    #                 "subject_uuid": subject_uuid,
    #                 "assay_seek_id": assay_seek_id,
    #                 "workspace": None,
    #                 # "platform_configs": None,
    #             }
    #
    #             # trigger workflow
    #             airflow_api_url = "http://130.216.208.137:8080/api/v1"
    #             dag_url = f"{airflow_api_url}/dags/{workflow_dataset_uuid}/dagRuns"
    #             response = requests.post(
    #                 dag_url,
    #                 auth=HTTPBasicAuth("admin", "PgKFTfe4B2C7ragN"),
    #                 headers={"Content-Type": "application/json"},
    #                 data=json.dumps({"conf": params})
    #             )




def exec(**kwargs):
    assay_seek_id = kwargs['dag_run'].conf.get('assay_seek_id', kwargs['params'].get('assay_seek_id'))
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/preprocessor/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    run(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)


def get_task(dag: DAG):
    task_id = "ep3_download_data_pre"
    return PythonOperator(
        task_id=task_id,
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    assay_seek_id = 21
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/preprocessor/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    run(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)

