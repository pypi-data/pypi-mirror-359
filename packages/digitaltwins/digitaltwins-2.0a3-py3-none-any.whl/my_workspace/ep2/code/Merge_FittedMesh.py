import os
from gias3.mesh import vtktools
from gias3.mesh import simplemesh
import numpy as np

# root_dir= r"C:\Users\rrag962\Documents\shapemodel\model\Shoulder 3\Segmentations\SSM\Thorax"
root_dir = r"/home/clin864/opt/digitaltwins-api/my_workspace/ep2/code/thorax"

#set directories for bones to be merged
# rib = r"C:\Users\rrag962\Documents\shapemodel\model\Shoulder 3\Segmentations\SSM\Thorax\rib_fitted_meshes"
# sternum = r"C:\Users\rrag962\Documents\shapemodel\model\Shoulder 3\Segmentations\SSM\Thorax\sternum_fitted_meshes"
rib = r"/home/clin864/eresearch-ep2/workflow/Segmented_CT_data/Ribs"
sternum = r"/home/clin864/eresearch-ep2/workflow/Segmented_CT_data/Sternum"

#set directory where you want the merged meshes to go
thorax = os.path.join(root_dir, 'test')

rib_files = [f for f in os.listdir(rib)]
sternum_files = [f for f in os.listdir(sternum)]


#loop through first bone and make sure the case is present in the rest of the bones
for rib_file in rib_files:
    case = rib_file[:7]
    matching_cases = [sternum_file for sternum_file in sternum_files if sternum_file.startswith(case)]

    for matching_case in matching_cases:
        #load first mesh
        rib_path = os.path.join(rib, rib_file)
        rib_mesh = vtktools.loadpoly(rib_path)

        #load second mesh
        sternum_path = os.path.join(sternum, matching_case)
        sternum_mesh = vtktools.loadpoly(sternum_path)

        # create a new merged mesh object
        merged_mesh = simplemesh.SimpleMesh()
        # merge vertices of all meshes
        merged_mesh_vert = np.concatenate((rib_mesh.v, sternum_mesh.v), axis=0)
        # merge faces of all meshes, need to add number of vertices for all previous meshes so the face numbers are correct
        merged_mesh_faces = np.concatenate((rib_mesh.f, sternum_mesh.f + len(rib_mesh.v)), axis=0)
        # assign vertices and faces to new mesh
        merged_mesh.v = merged_mesh_vert
        merged_mesh.f = merged_mesh_faces
        # save merged mesh
        save_path = os.path.join(thorax, case + '_thorax')
        vtktools.savepoly(merged_mesh, save_path + '.ply')
        print("finished case:", case)

