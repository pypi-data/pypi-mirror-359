'''
Created on 23/07/2020

@author: Gonzalo D. Maso Talou, Chinchien Lin
'''

import os
import dicom2nifti
# import dicom2nifti.settings as settings
# # disable the slice increment consistency check
# settings.disable_validate_slice_increment()

script_id = 'dicom_to_nifti'
run_program = 'python3'
run_script = 'dicom_to_nifti.py'
depends_on = ['import_scan']


def extract_metadata(process):
    process.clear_metadata()

    parent = process.parent
    for key in parent.metadata.keys():
        process.set_metadata(key, parent.metadata[key])


def update_metadata(process):
    # add/append process metadata
    pipeline = process.metadata['pipeline_metadata']
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


def convert_DICOM_to_Nifti(dicom_folder, nii_file):
    """
    Convert a dicom folder to a single nifti file

    :param dicom_folder: path to source dicom folder
    :type dicom_folder: string
    :param nii_file: full path to the output nifti file
    :type nii_file: string
    :return:
    :rtype:
    """

    nii_folder, nii_filename = os.path.split(nii_file)

    print("Processing study {}".format(dicom_folder))
    aux_folder = nii_folder + '/temp_nifti_conv/'
    os.makedirs(os.path.dirname(aux_folder), exist_ok=True)
    # dicom2nifti.convert_directory(dicom_folder, aux_folder, compression=True, reorient=True)
    dicom2nifti.convert_directory(dicom_folder, aux_folder, compression=True, reorient=False)
    # renames the file
    for fname in os.listdir(aux_folder):
        if fname.endswith('.nii.gz'):
            print("Renaming study {} to {}".format(aux_folder + fname.title(), nii_folder + '/' + nii_filename))
            os.rename(aux_folder + fname, nii_folder + '/' + nii_filename)
            os.removedirs(aux_folder)


def run(process):
    extract_metadata(process)

    source_workspace = process.parent.get_workspace('import_scan')
    dest_workspace = process.get_workspace('dicom_to_nifti', True)
    source_path = source_workspace.path()
    dest_path = dest_workspace.path()

    filename = process.metadata.get("subject").get("name") + ".nii.gz"
    file_path = os.path.join(dest_path, filename)

    convert_DICOM_to_Nifti(source_path, file_path)

    update_metadata(process)

    process.completed()


if __name__ == "__main__":
    import workflow_manager
    run(workflow_manager.get_project_process())

    # # Direct usage example
    # source = "/home/clin864/eresearch/Data/images/Duke_breast_cancer_dataset/manifest-1607053360376/Duke-Breast-Cancer-MRI//Breast_MRI_002/1.3.6.1.4.1.14519.5.2.1.29344851079648912610491979642001151972/1.3.6.1.4.1.14519.5.2.1.160280964313719412347933524460119440797"
    # dest = "/home/clin864/eresearch/sandbox/chinchien/workflow_Duke-Breast-Cancer-MRI/results/1.3.6.1.4.1.14519.5.2.1.160280964313719412347933524460119440797/1.3.6.1.4.1.14519.5.2.1.160280964313719412347933524460119440797.nii.gz"
    # convert_DICOM_to_Nifti(source, dest)



