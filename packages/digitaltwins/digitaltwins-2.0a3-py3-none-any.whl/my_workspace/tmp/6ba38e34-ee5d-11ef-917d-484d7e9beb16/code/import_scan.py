"""
This script will import dicom scans in a folder or a zip file (other archive
files can be added int he future). The script requires a path to the file or
folder and optionally a series uid if a specific series should be extracted.

The scan data will be extracted to a workspace called "scan".

Parameters:
 - path: source path to the folder or archive file
 - series: series instance uid to be filtered from the source [optional]

"""

import os
import pydicom

script_id = 'import_scan'
run_program = 'python3'
run_script = 'import_scan.py'


def set_metadata(process, path):
    process.clear_metadata()

    # project metadata
    process.set_metadata('project', process.params)

    # pipeline metadata
    proc_dict = {'id': process.id, 'label': process.label, 'script': process.script.label,
                 'root': process.root.id,
                 'params': process.params, 'status': process.status, 'message': process.message,
                 'started': process.started, 'duration': process.duration,
                 'workspaces': process.data['workspaces']}
    if process.parent is not None:
        proc_dict['parent'] = process.parent.id
    else:
        proc_dict['parent'] = None

    process.set_metadata('pipeline_metadata', {'name': process.project.name, 'processes': [proc_dict]})

    # subject metadata
    subject_tags = {
        'name': (0x10, 0x10),
        'id': (0x10, 0x20),
        'birth_date': (0x0010, 0x0030),
        'gender': (0x0010, 0x0040),
        'age': (0x0010, 0x1010),
        'height': (0x0010, 0x1020),
        'weight': (0x0010, 0x1030)
    }

    filename = os.listdir(path)[0]
    print(path, filename)
    dcm = pydicom.read_file(os.path.join(path, filename))
    dcmtags = dcm.keys()
    subject_dict = {}
    for key, tag in subject_tags.items():
        if tag in list(dcmtags):
            subject_dict[key] = str(dcm[tag].value)
    process.set_metadata('subject', subject_dict)

    # scan metadata
    scan_tags = {
        'body_part_examined': (0x0018, 0x0015),
        'modality': (0x0008, 0x0060),
        'sequence_name': (0x0018, 0x0024),
        'protocol_name': (0x0018, 0x1030),
        'subject_position': (0x0018, 0x5100),
        'study_instance_uid': (0x0020, 0x000d),
        'study_description': (0x0008, 0x1030),
        'series_instance_uid': (0x0020, 0x000e),
        'series_description': (0x0008, 0x103e),
        'series_date': (0x0008, 0x0021),
        'series_time': (0x0008, 0x0031)
    }

    scan_dict = {}
    for key, tag in scan_tags.items():
        if tag in list(dcmtags):
            scan_dict[key] = dcm[tag].value
    process.set_metadata('scan', scan_dict)


def get_scan_description(process):
    desc_keys = ['protocol_name', 'sequence_name', 'series_description', 'study_description']
    scan_keys = process.metadata['scan'].keys()
    for desc_key in desc_keys:
        if desc_key in scan_keys:
            return process.metadata['scan'][desc_key]
    return ''


def run(process):
    source = process.params.get('source')
    series = process.params.get('series')
    workspace = process.workspace('import_scan', True)
    workspace.clear()

    print(source)
    if os.path.isfile(source):  # Assumes any file is a zip file
        if series is not None:
            print('WARNING: Series filtering not supported for zip files')
        status, message = workspace.extract_zipfile(source)
        # Check if dicom has been extracted to a new folder in the workspace or if the dicoms have been extracted directly into the workspace directory (expected)
        if len(os.listdir(workspace.path())) == 1:
            # Move the dicom files into the workspace directory
            dicom_path = os.path.join(workspace.path(), os.listdir(workspace.path())[0])
            # import ipdb; ipdb.set_trace()
            dicom_files = os.listdir(dicom_path)
            import shutil
            for i, filename in enumerate(dicom_files):
                shutil.move(os.path.join(dicom_path, filename), os.path.join(workspace.path(), filename))
            os.rmdir(dicom_path)

    else:
        if series is None:
            files = os.listdir(source)
            filepaths = list()
            for file in files:
                fullpath = os.path.join(source, file)
                filepaths.append(fullpath)
            files = filepaths
        else:
            files = []
            for f in os.listdir(source):
                fullpath = os.path.join(source, f)
                dcm = pydicom.read_file(fullpath)
                if str(dcm.SeriesInstanceUID) == series:
                    files.append(fullpath)
        if len(files) == 0:
            process.completed(False, 'No files found')

        status, message = workspace.copy_files(files)

    set_metadata(process, workspace.path())

    process.completed(status, process.metadata['subject']['id'] + " (" +
                      process.metadata['scan']['subject_position'] + ", " +
                      get_scan_description(process) + ")")


if __name__ == "__main__":
    import workflow_manager

    run(workflow_manager.get_project_process())
