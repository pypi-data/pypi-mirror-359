import os
import json
import numpy as np
from shutil import copyfile

import breast_metadata
import breast_mech
import morphic

script_id = 'generate_point_cloud'
run_program = 'python3'
run_script = 'generate_point_cloud.py'
depends_on = ['segment']


def extract_metadata(process):
    process.clear_metadata()

    parent = process.parent
    for key in parent.metadata.keys():
        process.set_metadata(key, parent.metadata[key])


def update_metadata(process):
    pipeline = process.parent.metadata['pipeline_metadata']
    processes = pipeline['processes']
    proc_dict = {'id': process.id, 'label': process.label, 'script': process.script.label,
                 'root': process.root.id,
                 'params': process.params, 'status': process.status, 'message': process.message,
                 'started': process.started, 'duration': process.duration,
                 'workspaces': process.data['workspaces']}
    if process.parent is not None:
        proc_dict['parent'] = process.parent.id
    else:
        proc_dict['parent'] = None
    processes.append(proc_dict)
    pipeline['processes'] = processes
    process.set_metadata('pipeline_metadata', pipeline)


def save_cloud(cloud, output_file):
    # if output_file:
    #     data = {
    #         'Datapoints': cloud.tolist()
    #     }
    #     with open(output_file + ".data", 'w') as outfile:
    #         json.dump(data, outfile, indent=4)
    #     # save cloud to txt
    #     np.savetxt(output_file + ".txt", cloud)

    save_path = output_file + '.data'
    data = morphic.Data()
    data.values = cloud
    data.save(save_path)

    np.savetxt(output_file + ".txt", cloud)

def generate_point_cloud(source_path, dest_path):
    # num_of_points = 1000
    num_of_points = 5000
    # num_of_points = 300000

    for filename in os.listdir(source_path):
        input_file = os.path.join(source_path, filename)

        if not os.path.isfile(input_file):
            continue

        output_file = None
        if "rib" in filename.lower():
            output_file = os.path.join(dest_path, "rib_pts")
        if "lung" in filename.lower():
            output_file = os.path.join(dest_path, "lungs_pts")
        if "skin" in filename.lower() or "body" in filename.lower():
            output_file = os.path.join(dest_path, "skin_pts")
        if "nipple" in filename.lower():
            output_file = os.path.join(dest_path, filename)
            copyfile(input_file, output_file)
            continue

        try:
            image = breast_metadata.readNIFTIImage(input_file)
        except RuntimeError:
            continue
        cloud = breast_mech.extract_contour_points(image, num_of_points)

        # save
        save_cloud(cloud, output_file)


def run(process):
    extract_metadata(process)

    # get workspaces
    source_workspace = process.parent.get_workspace('segment')
    dest_workspace = process.get_workspace('generate_point_cloud', True)
    source_path = source_workspace.path()
    dest_path = dest_workspace.path()

    generate_point_cloud(source_path, dest_path)

    update_metadata(process)
    process.completed()


if __name__ == '__main__':
    import workflow_manager
    run(workflow_manager.get_project_process())

    # # Usage example
    # source_path = "/home/clin864/eresearch/sandbox/chinchien/workflow_Duke-Breast-Cancer-MRI/results/1.3.6.1.4.1.14519.5.2.1.160280964313719412347933524460119440797/segment"
    # dest_path = "/home/clin864/eresearch/sandbox/chinchien/workflow_Duke-Breast-Cancer-MRI/results/1.3.6.1.4.1.14519.5.2.1.160280964313719412347933524460119440797/cloud"
    #
    # generate_point_cloud(source_path, dest_path)