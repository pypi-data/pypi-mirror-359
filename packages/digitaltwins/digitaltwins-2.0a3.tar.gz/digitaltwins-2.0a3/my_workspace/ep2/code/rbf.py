import os
from subprocess import call

# change file path of segments
# root_dir = r"Y:\workflow\Segmented_CT_data\L_Clavicle"
root_dir = r"/home/clin864/eresearch-ep2/workflow/Segmented_CT_data/L_Clavicle"

file_names = os.listdir(root_dir)
full_paths = [os.path.join(root_dir, i) for i in file_names]

names = ('\n'.join(full_paths))
print(names)

# rbf_file = r"Y:\workflow\Segmented_CT_data\rbf_list.txt"
# rbf_file = r"/home/clin864/eresearch-ep2/workflow/Segmented_CT_data/rbf_list.txt"
rbf_file = r"/home/clin864/opt/digitaltwins-api/my_workspace/ep2/code/rbf_list.txt"

# Write the file base and names to the text file
with open(rbf_file, "w") as file:
    file.write(f"{names}")

# fitted_file = r"Y:\workflow\Fitted_meshes\Fitted_L_clavicle"
fitted_file = r"/home/clin864/opt/digitaltwins-api/my_workspace/ep2/code/fitted_meshes/Fitted_L_clavicle"
call(["gias-rbfreg", "-b", rbf_file, "-d", fitted_file, "--outext", '.ply'])
