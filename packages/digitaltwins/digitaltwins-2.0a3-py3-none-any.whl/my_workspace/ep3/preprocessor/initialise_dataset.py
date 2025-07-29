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
    if str(assay_id) == "2":
        assay = {'id': '2', 'type': 'assays', 'attributes': {'policy': {'access': 'no_access', 'permissions': [{'resource': {'id': '4', 'type': 'projects'}, 'access': 'download'}, {'resource': {'id': '3', 'type': 'people'}, 'access': 'edit'}, {'resource': {'id': '2', 'type': 'people'}, 'access': 'manage'}, {'resource': {'id': '4', 'type': 'people'}, 'access': 'manage'}]}, 'discussion_links': [], 'snapshots': [], 'title': 'Assay 1: Run automated tumour position reporting (Model Generation) on Duke University breast MRI dataset', 'description': 'Using workflow 1: automated tumour position reporting (Model Generation)', 'other_creators': '', 'position': None, 'assay_class': {'title': 'Experimental assay', 'key': 'EXP', 'description': None}, 'assay_type': {'label': 'Experimental Assay Type', 'uri': 'http://jermontology.org/ontology/JERMOntology#Experimental_assay_type'}, 'technology_type': {'label': 'Technology Type', 'uri': 'http://jermontology.org/ontology/JERMOntology#Technology_type'}, 'tags': [], 'creators': [{'profile': '/people/1', 'family_name': 'Lin', 'given_name': 'Chinchien', 'affiliation': 'Default Institution, University of Auckland, Auckland Bioengineering Institute', 'orcid': None}, {'profile': '/people/2', 'family_name': 'Babarenda Gamage', 'given_name': 'Prasad', 'affiliation': 'University of Auckland, Auckland Bioengineering Institute', 'orcid': None}, {'profile': '/people/3', 'family_name': 'Xu', 'given_name': 'Jiali', 'affiliation': 'University of Auckland, Auckland Bioengineering Institute', 'orcid': None}]}, 'relationships': {'creators': {'data': [{'id': '1', 'type': 'people'}, {'id': '2', 'type': 'people'}, {'id': '3', 'type': 'people'}]}, 'submitter': {'data': [{'id': '1', 'type': 'people'}]}, 'organisms': {'data': []}, 'human_diseases': {'data': []}, 'people': {'data': [{'id': '1', 'type': 'people'}, {'id': '2', 'type': 'people'}, {'id': '3', 'type': 'people'}]}, 'projects': {'data': [{'id': '4', 'type': 'projects'}]}, 'investigation': {'data': {'id': '2', 'type': 'investigations'}}, 'study': {'data': {'id': '2', 'type': 'studies'}}, 'data_files': {'data': []}, 'samples': {'data': []}, 'models': {'data': []}, 'sops': {'data': [{'id': '1', 'type': 'sops'}]}, 'publications': {'data': []}, 'placeholders': {'data': []}, 'documents': {'data': []}}, 'links': {'self': '/assays/2'}, 'meta': {'created': '2024-12-04T02:54:23.000Z', 'modified': '2025-02-18T21:47:10.000Z', 'api_version': '0.3', 'base_url': 'http://localhost:3000', 'uuid': 'fd7095a0-9418-013d-75f3-0242ac120005'}, 'params': {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'assay_seek_id': 2, 'workflow_seek_id': 1, 'cohort': 2, 'ready': True, 'inputs': [{'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'pca_model', 'dataset_uuid': 'd8f0b6d4-65ae-11ef-917d-484d7e9beb16', 'sample_type': '', 'category': 'model'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'mri', 'dataset_uuid': '6ba38e34-ee5d-11ef-917d-484d7e9beb16', 'sample_type': 'ax dyn pre', 'category': 'measurement'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'segmentation_model_lung', 'dataset_uuid': '660eac41-5f53-11ef-917d-484d7e9beb16', 'sample_type': '', 'category': 'model'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'segmentation_model_skin', 'dataset_uuid': '660eac40-5f53-11ef-917d-484d7e9beb16', 'sample_type': '', 'category': 'model'}], 'outputs': [{'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'nrrd', 'dataset_name': 'New Dataset 1', 'sample_name': 'nrrd', 'category': 'measurement'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'nifti', 'dataset_name': 'New Dataset 1', 'sample_name': 'nifti', 'category': 'measurement'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'mesh', 'dataset_name': 'New Dataset 1', 'sample_name': 'mesh', 'category': 'measurement'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'point_cloud', 'dataset_name': 'New Dataset 1', 'sample_name': 'point_cloud', 'category': 'measurement'}, {'assay_uuid': '25e0cb08-f486-11ef-917d-484d7e9beb16', 'name': 'segmentation', 'dataset_name': 'New Dataset 1', 'sample_name': 'segmentation', 'category': 'measurement'}]}}
    return assay


def run(assay_seek_id, workspace, platform_config_file):
    # todo.
    import time
    time.sleep(5)



def exec(**kwargs):
    assay_seek_id = kwargs['dag_run'].conf.get('assay_seek_id', kwargs['params'].get('assay_seek_id'))
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/preprocessor/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    run(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)


def get_task(dag: DAG):
    task_id = "initialise_dataset"
    return PythonOperator(
        task_id=task_id,
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    assay_seek_id = 2
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/preprocessor/workspace"
    platform_config_file = "/home/clin864/opt/digitaltwins-api/my_workspace/configs.ini"

    run(assay_seek_id=assay_seek_id, workspace=workspace, platform_config_file=platform_config_file)

