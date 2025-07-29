"""
Fitting meshes to segmented data.
"""
import os
import json
import numpy as np
import scipy
import h5py
import importlib
import mesh_tools

from shutil import copyfile
from sklearn.cross_decomposition import PLSRegression

import automesh
import morphic
import bmw

importlib.reload(morphic)

script_id = 'generate_mesh_cl'
run_script = 'generate_mesh_cl.py'
cores = 1
depends_on = ['generate_point_cloud']
run_program = 'python3'

def transformPointToImageSpace(point, image_origin, image_spacing, image_size):
    transformed_point = [-point[1] + image_origin[0] + image_spacing[0] * image_size[0],
        point[0] + image_origin[1],
        point[2] + image_origin[2]]
    return transformed_point


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

def init_pca_mesh(meshes, nipple_pts):

    sternum_pt = nipple_pts[2, :]
    dx = sternum_pt - meshes['left'].nodes[21].values[:, 0]
    for side in ['left', 'right', 'lungs']:
        mesh = meshes[side]
        if 'dx' not in mesh.nodes.keys():
            mesh.add_stdnode('dx', [0, 0, 0])
        mesh.nodes['dx'].values = dx
        mesh.translate('dx', groups=['std', 'pca'], update=True)

    return meshes


def pca_fit_skin_lungs(meshes, data, num_modes=3):

    Xi = meshes['left'].grid(6, method='center')
    Xi_nipple = meshes['left'].grid(10, method='center')
    Xi_sternum = np.array([np.zeros((20)), np.linspace(0, 1, 20)]).T
    elem_anterior = range(36)
    # elem_anterior.extend([42, 43, 47, 48])
    elem_axilla = []#[39, 44, 49]
    elem_nipple = [7, 8, 9, 10, 13, 14, 15, 16, 19, 20, 21, 22, 25, 26, 27, 28]
    elem_sternum = [6, 12, 18, 24]

    dx = np.array(meshes['left'].nodes['dx'].values)

    Xnipple = data['nipples']['data']

    right_nipple_arg = Xnipple[:, 1].argmax()
    left_nipple_arg = Xnipple[:, 1].argmin()
    sternum_arg = range(3)
    # TODO. chinchien
    # sternum_arg.remove(left_nipple_arg)
    # sternum_arg.remove(right_nipple_arg)
    sternum_arg = [i for i in sternum_arg if i != left_nipple_arg]
    sternum_arg = [i for i in sternum_arg if i != right_nipple_arg]
    # end todo
    sternum_arg = sternum_arg[0]

    data['nipple_right'] = {'data': np.array([Xnipple[right_nipple_arg, :]])}
    data['nipple_left'] = {'data': np.array([Xnipple[left_nipple_arg, :]])}
    data['sternum'] = {'data': np.array([Xnipple[sternum_arg, :]])}
    data['weights'] = {'data': np.ones(num_modes)}
    data['dx'] = {'data': dx}

    dofs = [
        {'mesh': 'left', 'nodes': 'all', 'fix': 'all'},
        {'mesh': 'right', 'nodes': 'all', 'fix': 'all'},
        {'data': 'weights', 'var': 'all'},
        {'data': 'dx', 'var': 'all'}
    ]

    left_weights_pids = meshes['left'].nodes['weights'].cids[1:num_modes + 1]
    right_weights_pids = meshes['right'].nodes['weights'].cids[1:num_modes + 1]
    lungs_weights_pids = meshes['lungs'].nodes['weights'].cids[1:num_modes + 1]

    left_dx_pids = meshes['left'].nodes['dx'].cids
    right_dx_pids = meshes['right'].nodes['dx'].cids
    lungs_dx_pids = meshes['lungs'].nodes['dx'].cids

    fits = [
        {'type': 'update_pids_from_data', 'mesh': 'left', 'pids': left_weights_pids, 'data': 'weights'},
        {'type': 'update_pids_from_data', 'mesh': 'right', 'pids': right_weights_pids, 'data': 'weights'},
        {'type': 'update_pids_from_data', 'mesh': 'lungs', 'pids': lungs_weights_pids, 'data': 'weights'},

        {'type': 'update_pids_from_data', 'mesh': 'left', 'pids': left_dx_pids, 'data': 'dx'},
        {'type': 'update_pids_from_data', 'mesh': 'right', 'pids': right_dx_pids, 'data': 'dx'},
        {'type': 'update_pids_from_data', 'mesh': 'lungs', 'pids': lungs_dx_pids, 'data': 'dx'},

        {'type': 'update_pca', 'mesh': ['left', 'right', 'lungs'], 'translation_node': 'dx', 'group': 'pca', 'weight': 100},

        {'type': 'closest_data', 'mesh': ['left', 'right'], 'data': 'skin', 'elements': elem_anterior, 'xi': Xi, 'limit': 10},
        {'type': 'closest_data', 'mesh': 'lungs', 'data': 'lungs', 'elements': range(24), 'xi': Xi, 'weight': 1, 'limit': 10},

        {'type': 'closest_mesh', 'mesh': 'right', 'data': 'nipple_right', 'elements': elem_nipple, 'xi': Xi_nipple, 'weight': 1, 'k': 3},
        {'type': 'closest_mesh', 'mesh': 'left', 'data': 'nipple_left', 'elements': elem_nipple, 'xi': Xi_nipple, 'weight': 1, 'k': 3},
        {'type': 'closest_mesh', 'mesh': 'left', 'data': 'sternum', 'elements': elem_sternum, 'xi': Xi_sternum, 'weight': 1, 'k':3},

        # {'type': 'function', 'mesh': 'left', 'function': constrain_torso_height, 'weight': 10},
    ]
    meshes = automesh.fit.fit_mesh(meshes, data, fits, dofs=dofs, ftol=1e-4, xtol=1e-4, maxiter=2000, dt=10, output=True)

    return meshes


def pca_fit_skin_stage2(meshes, data, num_modes=3):

    Xi = meshes['left'].grid(6, method='center')
    Xi2 = meshes['left'].grid(2, method='center')
    Xi_nipple = meshes['left'].grid(10, method='center')
    Xi_sternum = np.array([np.zeros((20)), np.linspace(0, 1, 20)]).T
    elem_anterior = range(36)

    elem_mid = range(6, 30)
    elem_top_bot = [0, 1, 2, 3, 4, 5, 30, 31, 32, 33, 34, 35]
    elem_back = [el for el in range(42, 54)]

    elem_nipple = [7, 8, 9, 10, 13, 14, 15, 16, 19, 20, 21, 22, 25, 26, 27, 28]
    elem_sternum = [6, 12, 18, 24]

    Xnipple = data['nipples']['data']

    right_nipple_arg = Xnipple[:, 1].argmax()
    left_nipple_arg = Xnipple[:, 1].argmin()
    sternum_arg = range(3)
    # TODO. chinchien
    # sternum_arg.remove(left_nipple_arg)
    # sternum_arg.remove(right_nipple_arg)
    sternum_arg = [i for i in sternum_arg if i != left_nipple_arg]
    sternum_arg = [i for i in sternum_arg if i != right_nipple_arg]
    # end todo
    sternum_arg = sternum_arg[0]

    # 1/0
    data['nipple_right'] = {'data': np.array([Xnipple[right_nipple_arg, :]])}
    data['nipple_left'] = {'data': np.array([Xnipple[left_nipple_arg, :]])}
    data['sternum'] = {'data': np.array([Xnipple[sternum_arg, :]])}

    left_const_pids = []
    right_const_pids = []
    for nid in range(54, 74):
        for cid in meshes['left'].nodes[nid].cids:
            if cid not in left_const_pids:
                left_const_pids.append(cid)
        for cid in meshes['right'].nodes[nid].cids:
            if cid not in right_const_pids:
                right_const_pids.append(cid)

    left_const_values = np.array(meshes['left']._core.P[left_const_pids])
    right_const_values = np.array(meshes['right']._core.P[right_const_pids])

    dofs = [
        {'mesh': 'left', 'nodes': 'all', 'fix': 'all'},
        {'mesh': 'right', 'nodes': 'all', 'fix': 'all'},
        {'mesh': 'left', 'nodes': ['weights'], 'var': range(1, num_modes + 1)},
        {'mesh': 'right', 'nodes': ['weights'], 'var': range(1, num_modes + 1)}
    ]

    fits = [
        {'type': 'update_pca', 'mesh': ['left', 'right', 'lungs'], 'translation_node': 'dx', 'group': 'pca', 'weight': 10},

        {'type': 'closest_data', 'mesh': ['left', 'right'], 'data': 'skin', 'elements': elem_mid, 'xi': Xi, 'weight': 10},
        {'type': 'closest_data', 'mesh': ['left', 'right'], 'data': 'skin', 'elements': elem_top_bot, 'xi': Xi, 'limit': 10},
        {'type': 'closest_data', 'mesh': ['left', 'right'], 'data': 'skin', 'elements': range(36, 42), 'xi': Xi, 'limit': 10},

        {'type': 'closest_mesh', 'mesh': 'right', 'data': 'nipple_right', 'elements': elem_nipple, 'xi': Xi_nipple, 'weight': 10, 'k': 3},
        {'type': 'closest_mesh', 'mesh': 'left', 'data': 'nipple_left', 'elements': elem_nipple, 'xi': Xi_nipple, 'weight': 10, 'k': 3},
        {'type': 'closest_mesh', 'mesh': ['left', 'right'], 'data': 'sternum', 'elements': elem_sternum, 'xi': Xi_sternum, 'weight': 10, 'k':3},

        {'type': 'join_mesh_coordinates', 'mesh': ['left', 'right'], 'nodes': [[0, 42, 57, 73], [0, 42, 57, 73]], 'weight': 10},

        # {'type': 'constrain', 'mesh': 'left', 'elements': [44], 'xi': Xi2, 'values': 'self', 'weight': 1},
        {'type': 'constrain', 'mesh': 'left', 'elements': elem_back, 'xi': Xi, 'values': 'self', 'weight': 1},
        {'type': 'constrain', 'mesh': 'right', 'elements': elem_back, 'xi': Xi, 'values': 'self', 'weight': 1},

        # {'type': 'constrain', 'mesh': 'left', 'pids': left_const_pids, 'values': left_const_values, 'weight': 10},
        # {'type': 'constrain', 'mesh': 'right', 'pids': right_const_pids, 'values': right_const_values, 'weight': 1000},
    ]

    # for mesh in meshes.itervalues():
    #     mesh.update_pca_nodes()
    #     mesh.translate('dx', groups='std')
    #     mesh._core.update_dependent_nodes()

    meshes = automesh.fit.fit_mesh(meshes, data, fits, dofs=dofs, ftol=1e-4, xtol=1e-4, maxiter=4000, dt=10, output=True)

    return meshes


def pca_fit_skin(meshes, skin_pts, nipple_pts, num_modes=3):

    Xi = meshes['left'].grid(6, method='center')
    Xi_nipple = meshes['left'].grid(10, method='center')
    Xi_sternum = np.array([np.zeros((20)), np.linspace(0, 1, 20)]).T
    elem_anterior = range(36)
    # elem_anterior.extend([42, 43, 47, 48])
    elem_axilla = []#[39, 44, 49]
    elem_nipple = [7, 8, 9, 10, 13, 14, 15, 16, 19, 20, 21, 22, 25, 26, 27, 28]
    elem_sternum = [6, 12, 18, 24]

    # ii = skin_pts[:, 0] < (nipple_pts[2, 0] + 50)
    # print skin_pts.size, skin_pts[ii, :].size
    data = {
        'skin': {'data': skin_pts},
        'nipple_right': {'data': np.array([nipple_pts[0, :]])},
        'nipple_left': {'data': np.array([nipple_pts[1, :]])},
        'sternum': {'data': np.array([nipple_pts[2, :]])},
    }

    dofs = [
        {'mesh': 'left', 'nodes': 'all', 'fix': 'all'},
        {'mesh': 'right', 'nodes': 'all', 'fix': 'all'},
        {'mesh': 'left', 'nodes': ['weights'], 'var': range(1, num_modes + 1)},
        {'mesh': 'right', 'nodes': ['weights'], 'var': range(1, num_modes + 1)},
        {'mesh': 'left', 'nodes': ['dx'], 'var': [0, 1, 2]},
        {'mesh': 'right', 'nodes': ['dx'], 'var': [0, 1, 2]},
    ]

    fits = [
        {'type': 'update_pca', 'mesh': ['left', 'right'], 'translation_node': 'dx', 'group': 'pca'},
        {'type': 'closest_data', 'mesh': ['left', 'right'], 'data': 'skin', 'elements': elem_anterior, 'xi': Xi},
        # {'type': 'closest_data', 'mesh': ['left', 'right'], 'data': 'skin', 'elements': elem_axilla, 'xi': Xi, 'weight': 0.1},
        {'type': 'join_mesh_coordinates', 'mesh': ['left', 'right'], 'nodes': [[0, 42, 57, 73], [0, 42, 57, 73]], 'weight': 10},
        {'type': 'closest_mesh', 'mesh': ['right'], 'data': 'nipple_right', 'elements': elem_nipple, 'xi': Xi_nipple, 'weight': 1, 'k':3},
        {'type': 'closest_mesh', 'mesh': ['left'], 'data': 'nipple_left', 'elements': elem_nipple, 'xi': Xi_nipple, 'weight': 1, 'k':3},
        # {'type': 'closest_mesh', 'mesh': ['left'], 'data': 'sternum', 'elements': elem_sternum, 'xi': Xi_sternum, 'weight': 1, 'k':3},
        # {'type': 'fix_params', 'pids': [minz_pid], 'data': minz, 'mesh': 'skin_right', 'weight': 1000},
    ]

    meshes = automesh.fit.fit_mesh(meshes, data, fits, dofs=dofs, ftol=1e-4, xtol=1e-4, maxiter=2000, dt=10, output=True)

    return meshes


def collapse_pca_mesh(pca_mesh, node_ids, element_ids):
    pca_mesh.update_pca_nodes(True)
    if 'dx' in pca_mesh.nodes.keys():
        pca_mesh.translate('dx', groups=['std', 'pca'])

    mesh = morphic.Mesh()
    for nid in node_ids:
        node = pca_mesh.nodes[nid]
        if node.is_depnode():
            mesh.add_depnode(node.id, node.element, node.node)
        else:
            mesh.add_node(node.id, node.values)

    for eid in element_ids:
        element = pca_mesh.elements[eid]
        mesh.add_element(element.id, element.basis, element.node_ids)

    mesh.generate(True)

    return mesh


def collapse_skin_pca_mesh(pca_mesh):
    pca_mesh.update_pca_nodes(True)
    if 'dx' in pca_mesh.nodes.keys():
        pca_mesh.translate('dx', groups=['std', 'pca'])

    mesh = morphic.Mesh()
    copy_nids = [nid for nid in range(74) if nid not in [50, 52]]
    copy_nids.extend(['h49', 'h49xi', 'h50', 'h50xi', 'h51', 'h51xi', 'h52', 'h52xi', 'h53', 'h53xi'])
    for nid in copy_nids:
        node = pca_mesh.nodes[nid]
        if node.is_depnode():
            mesh.add_depnode(node.id, node.element, node.node)
        else:
            mesh.add_node(node.id, node.values)

    for eid in range(54):
        element = pca_mesh.elements[eid]
        mesh.add_element(element.id, element.basis, element.node_ids)

    mesh.generate(True)

    return mesh


def initialise_nodes(mesh):

    def center_node(mesh, elems, nodes):
        Nxi = 10
        xi = np.array([np.ones(Nxi), np.linspace(0, 1., Nxi)]).T

        midz = 0.5 * (mesh.nodes[nodes[0]].values[2, 0] + mesh.nodes[nodes[2]].values[2, 0])
        Xl = np.concatenate((mesh.evaluate(elems[0], xi), mesh.evaluate(elems[1], xi)))
        dz = np.absolute(Xl[:, 2] - midz)
        ii = dz.argmin()
        mesh.nodes[nodes[1]].values[:, 0] = Xl[ii, :]
        mesh.nodes[nodes[1]].values[2, 0] = midz
        return mesh

    def update_dzdxi2(mesh, nids):
        if len(nids) == 2:
            dz = mesh.nodes[nids[1]].values[2, 0] - mesh.nodes[nids[0]].values[2, 0]
            mesh.nodes[nids[0]].values[2, 2] = -dz

        elif len(nids) == 3:
            dz = mesh.nodes[nids[2]].values[2, 0] - mesh.nodes[nids[0]].values[2, 0]
            mesh.nodes[nids[1]].values[2, 2] = dz

        return mesh

    # Set dx/dx1 and dz/dx1 for sternal and spine nodes to 0
    for nid in [0, 7, 14, 21, 28, 35, 42, 57, 61, 65, 69, 73]:
        mesh.nodes[nid].values[0, 1] = 0
        mesh.nodes[nid].values[2, 1] = 0

    # For nodes 0-6, set equal y-spacing and dy/dxi2 = 0, top nodes
    dy = (1./6.) * (mesh.nodes[6].values[1, 0] - mesh.nodes[0].values[1, 0])
    for nid in range(1, 6):
        mesh.nodes[nid].values[1, 0] = mesh.nodes[0].values[1, 0] + nid * dy
        mesh.nodes[nid].values[1, 2] = 0
        mesh.nodes[nid].values[1, 3] = 0
    mesh.nodes[6].values[1, 2] = 0
    mesh.nodes[6].values[1, 3] = 0

    # set equal z-spacing for node 7 between nodes 0 and 14, upper sternum
    mesh.nodes[7].values[2, 0] = 0.5 * (mesh.nodes[0].values[2, 0] + mesh.nodes[14].values[2, 0])

    # set equal z-spacing for nodes 21, 28, 35 between nodes 14 and 42, lower sternum
    z0 = mesh.nodes[14].values[2, 0]
    dz = mesh.nodes[42].values[2, 0] - z0
    mesh.nodes[21].values[2, 0] = z0 + 0.25 * dz
    mesh.nodes[28].values[2, 0] = z0 + 0.5 * dz
    mesh.nodes[35].values[2, 0] = z0 + 0.75 * dz

    # set equal z-spacing for nodes 61, 65, 69 between nodes 57 and 73, spinal nodes
    z0 = mesh.nodes[57].values[2, 0]
    dz = mesh.nodes[73].values[2, 0] - z0
    mesh.nodes[61].values[2, 0] = z0 + 0.25 * dz
    mesh.nodes[65].values[2, 0] = z0 + 0.5 * dz
    mesh.nodes[69].values[2, 0] = z0 + 0.75 * dz

    # center axilla nodes 27 and 41
    mesh = center_node(mesh, [17, 23], [20, 27, 34])
    mesh = center_node(mesh, [29, 35], [34, 41, 48])

    # update dz/dxi2 for axilla nodes 27, 34, 41, 48
    mesh = update_dzdxi2(mesh, (20, 27, 34))
    mesh = update_dzdxi2(mesh, (27, 34, 41))
    mesh = update_dzdxi2(mesh, (34, 41, 48))
    mesh = update_dzdxi2(mesh, (48, 41))

    return mesh


def fit_skin_mesh_normals(mesh, X, pca_mesh):
    print('Fitting skin normals')

    elem_node_xi = [
        np.array([[0., 0]]), np.array([[1., 0]]), np.array([[0., 1]]), np.array([[1., 1]])
    ]

    def insert_normal(node, zero=[[], [], []]):
        def normalise(v):
            return v / np.sqrt((v * v).sum())

        for elem in mesh.elements:
            if node in elem.node_ids:
                eid = elem.id
                idx = elem.node_ids.index(node)
                break

        nva = mesh.nodes[node].values[:, 0]
        vec = normalise(mesh.elements[eid].normal(elem_node_xi[idx]))[0]
        for ax in [0, 1, 2]:
            if node in zero[ax]:
                vec[ax] = 0.
        nvb = nva + vec
        mesh.add_stdnode('nv%sa' % node, nva)
        mesh.add_stdnode('nv%sb' % node, nvb)
        mesh.add_element('nv%selem' % node, ['L1'], ['nv%sa' % node, 'nv%sb' % node])
        mesh.add_stdnode('xi%s' % node, [0.])
        mesh.add_depnode('nv%sd' % node, 'nv%selem' % node, 'xi%s' % node)
        mesh.generate()
        mesh.add_map(('nv%sd' % node, 0), (node, 0, 0))
        mesh.add_map(('nv%sd' % node, 1), (node, 1, 0))
        mesh.add_map(('nv%sd' % node, 2), (node, 2, 0))
        mesh.update_maps()

    # nodes = [i for i in range(0, 74) if i not in [49, 50, 52]]

    # Generate smmother derivative values to constrain to
    pca_mesh.nodes['weights'].values[7:] *= 0
    pca_mesh.update_pca_nodes(True)
    pca_mesh.translate('dx', groups=['std', 'pca'])
    mesh = collapse_skin_pca_mesh(pca_mesh)

    zmin = X[:, 2].min()
    zmax = X[:, 2].max()

    for nid in [0, 7, 14, 21]:
        if mesh.nodes[nid].values[2, 0] < zmax:
            node_top = nid
            break

    for nid in [42, 35, 28, 21]:
        if mesh.nodes[nid].values[2, 0] > zmin:
            node_bottom = nid
            break

    print(node_top, node_bottom)

    # nodes = [i for i in range(node_top, node_bottom) if i not in [7, 14, 21, 28, 35, 49, 50, 52]]
    nodes = [i for i in range(7, 42) if i not in [7, 14, 21, 28, 35, 49, 50, 52]]
    # nodes = [i for i in range(0, 49) if i not in [49, 50, 52]]
    elements = range(0, 36)
    zero = [
        [],
        [0, 6, 13, 7, 14, 21, 28, 35, 42, 57, 61, 65, 69, 73],
        [0, 1, 2, 3, 4, 5, 6, 42, 43, 44, 45, 46, 47, 48, 53, 54, 55, 56, 57, 70, 71, 72, 73, 20, 49, 62]
    ]
    for nid in nodes:
        insert_normal(nid, zero)
    var_nodes = ['xi%d' % i for i in nodes]

    Xi_data = mesh.grid(6, method='center')
    Xi_beta = mesh.grid(6, method='center')
    data = {'X': {'data': X}}

    elems_a = [0, 1, 2, 3, 4, 5, 30, 31, 32, 33, 34, 35]
    elems_a.extend(range(36, 42))
    elems_b = range(6, 30)

    dX10a = np.sqrt((pca_mesh.evaluate(elems_a, Xi_beta, deriv=[1, 0])**2).sum(1))
    dX01a = np.sqrt((pca_mesh.evaluate(elems_a, Xi_beta, deriv=[1, 0])**2).sum(1))
    dX20a = np.sqrt((pca_mesh.evaluate(elems_a, Xi_beta, deriv=[1, 0])**2).sum(1))
    dX02a = np.sqrt((pca_mesh.evaluate(elems_a, Xi_beta, deriv=[1, 0])**2).sum(1))

    dX10b = np.sqrt((pca_mesh.evaluate(elems_b, Xi_beta, deriv=[1, 0])**2).sum(1))
    dX01b = np.sqrt((pca_mesh.evaluate(elems_b, Xi_beta, deriv=[1, 0])**2).sum(1))
    dX20b = np.sqrt((pca_mesh.evaluate(elems_b, Xi_beta, deriv=[1, 0])**2).sum(1))
    dX02b = np.sqrt((pca_mesh.evaluate(elems_b, Xi_beta, deriv=[1, 0])**2).sum(1))

    alpha_a = 1e-2
    beta_a = 5e-1
    alpha_b = 1e-7
    beta_b = 5e-6
    fits = [
        {'type': 'update_dep_nodes', 'mesh': ['left']},
        {'type': 'update_maps', 'mesh': ['left']},
        {'type': 'closest_data', 'mesh': 'left', 'data': 'X', 'elements': elements, 'xi': Xi_data, 'out': 3, 'k': 1, 'limit': 5},
        {'type': 'constrain', 'mesh': 'left', 'elements': elems_a, 'xi': Xi_beta, 'deriv': [1, 0], 'values': dX10a, 'weight': alpha_a},
        {'type': 'constrain', 'mesh': 'left', 'elements': elems_a, 'xi': Xi_beta, 'deriv': [0, 1], 'values': dX01a, 'weight': alpha_a},
        {'type': 'constrain', 'mesh': 'left', 'elements': elems_a, 'xi': Xi_beta, 'deriv': [2, 0], 'values': dX20a, 'weight': beta_a},
        {'type': 'constrain', 'mesh': 'left', 'elements': elems_a, 'xi': Xi_beta, 'deriv': [0, 2], 'values': dX02a, 'weight': beta_a},
        {'type': 'constrain', 'mesh': 'left', 'elements': elems_b, 'xi': Xi_beta, 'deriv': [1, 0], 'values': dX10b, 'weight': alpha_b},
        {'type': 'constrain', 'mesh': 'left', 'elements': elems_b, 'xi': Xi_beta, 'deriv': [0, 1], 'values': dX01b, 'weight': alpha_b},
        {'type': 'constrain', 'mesh': 'left', 'elements': elems_b, 'xi': Xi_beta, 'deriv': [2, 0], 'values': dX20b, 'weight': beta_b},
        {'type': 'constrain', 'mesh': 'left', 'elements': elems_b, 'xi': Xi_beta, 'deriv': [0, 2], 'values': dX02b, 'weight': beta_b},
    ]

    dofs = [
        {'mesh': 'left', 'nodes': 'all', 'fix': 'all'},
        {'mesh': 'left', 'nodes': var_nodes, 'var': [0]}
    ]

    meshes = automesh.fit.fit_mesh({'left': mesh}, data, fits, dofs=dofs, ftol=1e-9, xtol=1e-9, maxiter=5000, dt=20, output=True)

    return meshes['left']


def fit_skin_mesh(mesh, X, stage=1):
    print('Fitting skin surface')

    elements = range(0, 36)
    nodes_internal = [8, 9, 10, 11, 12, 15, 16, 17, 18, 19, 22, 23, 24, 25, 26, 29, 30, 31, 32, 33, 36, 37, 38, 39, 40]
    if stage == 2:
        elements = range(0, 42)
        nodes_internal.extend([27, 34, 41, 51])

    Xi_data = mesh.grid(5, method='center')
    Xi_beta = mesh.grid(3, method='center')
    data = {'X': {'data': X}}

    alpha = 1e-3
    beta = 1e-2
    fits = [
        {'type': 'update_dep_nodes', 'mesh': ['skin']},
        {'type': 'update_maps', 'mesh': ['skin']},
        {'type': 'closest_data', 'mesh': 'skin', 'data': 'X', 'elements': elements, 'xi': Xi_data, 'out': 3, 'k': 1},
        {'type': 'constrain', 'mesh': 'skin', 'elements': elements, 'xi': Xi_beta, 'deriv': [1, 0], 'values': 'self', 'weight': alpha},
        {'type': 'constrain', 'mesh': 'skin', 'elements': elements, 'xi': Xi_beta, 'deriv': [0, 1], 'values': 'self', 'weight': alpha},
        {'type': 'constrain', 'mesh': 'skin', 'elements': elements, 'xi': Xi_beta, 'deriv': [2, 0], 'values': 'self', 'weight': beta},
        {'type': 'constrain', 'mesh': 'skin', 'elements': elements, 'xi': Xi_beta, 'deriv': [0, 2], 'values': 'self', 'weight': beta},
        {'type': 'constrain', 'mesh': 'skin', 'elements': elements, 'xi': Xi_beta, 'deriv': [1, 1], 'values': 'self', 'weight': 10 * beta},
    ]

    dofs = [
        {'mesh': 'skin', 'nodes': 'all', 'fix': 'all'},
        {'mesh': 'skin', 'nodes': nodes_internal, 'var': range(12)}
    ]
    if stage == 1:
        dofs.append({'mesh': 'skin', 'nodes': [0, 1, 2, 3, 4, 5, 42, 43, 44, 45, 46, 47], 'var': [2, 6, 10]})
    elif stage == 2:
        dofs.append({'mesh': 'skin', 'nodes': [48, 49, 53, 70], 'var': [0, 1, 4, 5, 2, 6, 10]})
        dofs.append({'mesh': 'skin', 'nodes': [6, 13, 20], 'var': [0, 1, 4, 5]})

    meshes = automesh.fit.fit_mesh({'skin': mesh}, data, fits, dofs=dofs, ftol=1e-9, xtol=1e-9, maxiter=5000, dt=30, output=True)

    return meshes['skin']


def fit_skin_seam(seam, left_mesh, right_mesh, X):

    if seam == 'anterior':
        left_mesh_xi1_dir = 1
        right_mesh_xi1_dir = -1
        nodes = [[1, 0, 1], [8, 7, 8], [15, 14, 15], [22, 21, 22], [29, 28, 29], [36, 35, 36], [43, 42, 43]]
        first_element_nodes = range(0, 18, 3)
        num_xi = 10
        fit_elements = range(12)
        var_nodes = [1, 4, 7, 10, 13, 16, 19]
    elif seam == 'posterior':
        left_mesh_xi1_dir = -1
        right_mesh_xi1_dir = 1
        nodes = [[56, 57, 56], [60, 61, 60], [64, 65, 64], [68, 69, 68], [72, 73, 72]]
        first_element_nodes = range(0, 12, 3)
        num_xi = 20
        fit_elements = range(8)
        var_nodes = [1, 4, 7, 10, 13]

    mesh = morphic.Mesh()
    node_id = 0
    for nids in nodes:
        x = np.array(right_mesh.nodes[nids[0]].values)
        x[:, 1] *= right_mesh_xi1_dir  # reverse xi1 direction
        mesh.add_node(node_id, x)
        node_id += 1

        xr = np.array(right_mesh.nodes[nids[1]].values)
        xr[:, 1] *= right_mesh_xi1_dir  # reverse xi1 direction
        xl = np.array(left_mesh.nodes[nids[1]].values)
        xl[:, 1] *= left_mesh_xi1_dir  # reverse xi1 direction
        x = 0.5 * (xr + xl)  # average of seam node values
        x[2, 1] = 0  # rate of change of z wrt to xi1 is 0
        mesh.add_node(node_id, x)
        node_id += 1

        x = np.array(left_mesh.nodes[nids[2]].values)
        x[:, 1] *= left_mesh_xi1_dir  # reverse xi1 direction
        mesh.add_node(node_id, x)
        node_id += 1

    elem_id = 0
    for nid in first_element_nodes:
        node_ids = [nid, nid + 1, nid + 3, nid + 4]
        mesh.add_element(elem_id, ['H3', 'H3'], node_ids)
        elem_id += 1

        node_ids = [nid + 1, nid + 2, nid + 4, nid + 5]
        mesh.add_element(elem_id, ['H3', 'H3'], node_ids)
        elem_id += 1

    mesh.generate()

    # filter data
    pad = 30
    beta = 2e-3
    x = []
    for node in mesh.nodes:
        x.append(node.values[:, 0])
    x = np.array(x)
    xmin, xmax = x.min(0), x.max(0)
    for idx in [0, 1, 2]:
        X = np.array(X[X[:, idx] > (xmin[idx] - pad), :])
        X = np.array(X[X[:, idx] < (xmax[idx] + pad), :])

    Xi = left_mesh.grid(num_xi, method='center')
    Xid = left_mesh.grid(3, method='center')

    # if there is no back data, it will generate some from the patch mesh.
    if X.shape[0] == 0:
        X = mesh.evaluate(fit_elements, Xi)

    data = {'X': {'data': X}}
    fits = [
            {'type': 'closest_data', 'data': 'X', 'elements': fit_elements, 'xi': Xi, 'out': 3, 'k': 1, 'limit': 5},

            {'type': 'penalise_derivatives', 'elements': fit_elements, 'xi': Xid, 'deriv': [2, 0], 'weight': 10 * beta},
            {'type': 'penalise_derivatives', 'elements': fit_elements, 'xi': Xid, 'deriv': [0, 2], 'weight': beta},
            {'type': 'penalise_derivatives', 'elements': fit_elements, 'xi': Xid, 'deriv': [1, 1], 'weight': 5 * beta},
        ]

    dofs = [
        {'nodes': 'all', 'fix': 'all'},
        {'nodes': var_nodes, 'var': [0, 1, 2, 3, 5, 7, 10, 11]},
    ]

    mesh = automesh.fit.fit_mesh(mesh, data, fits, dofs=dofs, ftol=1e-6, xtol=1e-6, maxiter=10000, dt=100, output=True)

    for src_node, dst_node in zip(var_nodes, nodes):
        x = np.array(mesh.nodes[src_node].values)
        x[:, 1] *= left_mesh_xi1_dir
        left_mesh.nodes[dst_node[1]].values = x
        x = np.array(mesh.nodes[src_node].values)
        x[:, 1] *= right_mesh_xi1_dir
        right_mesh.nodes[dst_node[1]].values = x

    return left_mesh, right_mesh


def count_axis(X, axis, dx=10):
    xmin, xmax = X.min(0)[axis], X.max(0)[axis]
    xr = np.arange(xmin - dx, xmax + dx, dx)
    count = []
    for i in range(xr.shape[0] - 1):
        ii1 = xr[i] < X[:, axis]
        ii2 = X[:, axis] < xr[i + 1]
        ii = ii1 * ii2
        count.append(ii.sum())
    count = np.array(count)
    dc = count[1:] - count[:-1]

    threshold = 0.2 * count.max()
    if axis == 0:
        for i, cc in enumerate(count):
            if cc > threshold:
                x0 = xr[i]
                break
        for i, cc in enumerate(count[::-1]):
            if cc > threshold:
                x1 = xr[::-1][i]
                break
        x = np.array([x0, x1])
        return 0.5 * (xr[1:] + xr[:-1]), count, dc, x

    if axis == 1:
        for i, cc in enumerate(count):
            if cc > threshold:
                i0 = i
                x0 = xr[i]
                break
        for i, cc in enumerate(count[::-1]):
            if cc > threshold:
                i1 = i
                x1 = xr[::-1][i]
                break
        y = np.array([x0, x1, 0])

        return 0.5 * (xr[1:] + xr[:-1]), count, dc, y


def pca_fit_lungs(pca_mesh, lung_pts, z_base, num_modes=3):

    x, xc, dx, xx = count_axis(lung_pts, 0, 1)
    y, yc, dy, yy = count_axis(lung_pts, 1, 1)

    if 'dx' not in pca_mesh.nodes.keys():
        pca_mesh.add_stdnode('dx', [0, 0, 0], group='_translation')
    mean_x = lung_pts.mean(0)
    dz = lung_pts.min(0)[2] - pca_mesh.nodes[24].values[2, 0]
    pca_mesh.nodes['dx'].values = np.array([mean_x[0], mean_x[1], dz])

    Xi = pca_mesh.grid(10, method='center')
    minz_pid = pca_mesh.nodes[24].cids[8]

    x_pids_ant = [pca_mesh.nodes[i].cids[0] for i in [8, 16]]
    x_pids_pos = [pca_mesh.nodes[i].cids[0] for i in [11, 13, 19, 31]]
    y_pids_right = [pca_mesh.nodes[i].cids[4] for i in [18, 26]]
    y_pids_left = [pca_mesh.nodes[i].cids[4] for i in [22, 30]]

    meshes = {'lungs': pca_mesh}
    data = {
        'lungs': {'data': lung_pts}
    }
    dofs = [
        {'mesh': 'lungs', 'nodes': 'all', 'fix': 'all'},
        {'mesh': 'lungs', 'nodes': ['dx'], 'var': [0, 1, 2]}
    ]
    elems1 = [0, 1, 2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 13, 14]
    elems2 = [8, 15, 16, 17, 18, 19, 20, 21, 22, 23]
    fits = [
        {'type': 'update_pca', 'mesh': ['lungs'], 'translation_node': 'dx', 'group': 'pca', 'weight': 5},
        {'type': 'closest_data', 'mesh': ['lungs'], 'data': 'lungs', 'elements': elems1, 'xi': Xi, 'weight': 20},
        {'type': 'closest_data', 'mesh': ['lungs'], 'data': 'lungs', 'elements': elems2, 'xi': Xi, 'weight':1, 'limit': 50},
        {'type': 'fix_params', 'mesh': 'lungs', 'pids': [minz_pid], 'data': z_base, 'weight': 1000},
        {'type': 'fix_params', 'mesh': 'lungs', 'pids': x_pids_ant, 'data': xx[0], 'weight': 10},
        # {'type': 'fix_params', 'mesh': 'lungs', 'pids': x_pids_pos, 'data': xx[1], 'weight': 10},
        {'type': 'fix_params', 'mesh': 'lungs', 'pids': y_pids_right, 'data': yy[1], 'weight': 10},
        {'type': 'fix_params', 'mesh': 'lungs', 'pids': y_pids_left, 'data': yy[0], 'weight': 10},
    ]

    meshes = automesh.fit.fit_mesh(meshes, data, fits, dofs=dofs, ftol=1e-4, xtol=1e-4, maxiter=1, dt=10, output=True)

    dofs.append({'mesh': 'lungs', 'nodes': ['weights'], 'var': range(1, num_modes + 1)})
    meshes = automesh.fit.fit_mesh(meshes, data, fits, dofs=dofs, ftol=1e-4, xtol=1e-4, maxiter=1000, dt=10, output=True)

    return meshes['lungs']


def collapse_lungs_pca_mesh(pca_mesh):
    new_mesh = morphic.Mesh()
    for nid in range(32):
        new_mesh.add_stdnode(pca_mesh.nodes[nid].id, pca_mesh.nodes[nid].values)
    for eid in range(24):
        new_mesh.add_element(pca_mesh.elements[eid].id, pca_mesh.elements[eid].basis, pca_mesh.elements[eid].node_ids)
    new_mesh.generate()
    return new_mesh


def get_offset(mesh0, mesh1):
    x0 = [mesh1.nodes[nid].values[:, 0] for nid in [14, 65]]
    x = np.mean(x0, 0)
    x[1] = mesh0.nodes[0].values[1, 0]
    x[2] = mesh0.nodes[24].values[2, 0]
    return x


def load_lungs_ribcage_plsr_data(path_formats, include_subjects, skin_nodes='all'):
    if skin_nodes == 'all':
        skin_nodes = [nid for nid in range(74) if nid not in [50, 52]]
    xnids = range(32)
    ynids = range(32)
    X, Y, included_subjects = [], [], []
    for sid in include_subjects:
        paths = [path_format % sid for path_format in path_formats]
        all_paths_exist = True
        for path in paths:
            if not os.path.exists(path):
                print('Mesh does not exist: %s' % path)
                all_paths_exist = False
        if all_paths_exist:
            included_subjects.append(sid)
            x = []
            x0 = None
            mesh0 = morphic.Mesh(paths[0])
            mesh1 = morphic.Mesh(paths[1])
            mesh2 = morphic.Mesh(paths[2])
            if x0 is None:
                x0 = get_offset(mesh0, mesh1)
            for nid in xnids:
                xn = np.array(mesh0.nodes[nid].values)
                xn[:, 0] -= x0
                x.extend(xn.flatten().tolist())
            for nid in skin_nodes:
                xn = np.array(mesh1.nodes[nid].values)
                xn[:, 0] -= x0
                x.extend(xn.flatten().tolist())
            for nid in skin_nodes:
                xn = np.array(mesh2.nodes[nid].values)
                xn[:, 0] -= x0
                x.extend(xn.flatten().tolist())
            X.append(x)

            y = []
            ribcage_mesh = morphic.Mesh(paths[-1])
            for nid in ynids:
                yn = np.array(ribcage_mesh.nodes[nid].values)
                yn[:, 0] = yn[:, 0] - x0
                y.extend(yn.flatten().tolist())
            Y.append(y)
    # print np.array(X)
    return np.array(X), np.array(Y), included_subjects


def predict_lungs_to_ribcage(lungs_mesh, left_skin, right_skin, X, Y, included_subjects=None, exclude_subject=None,
                             skin_nodes='all', modes=6):

    # TODO: implement exclude subject

    # sternum_nodes = [21, 22, 23, 28, 29, 30, 35, 36, 37, 42, 43, 44]
    if skin_nodes == 'all':
        skin_nodes = [nid for nid in range(74) if nid not in [50, 52]]
    # skin_nids = []
    # skin_nodes = sternum_nodes
    xnids = range(32)
    ynids = range(32)

    # Load input data using left and right mesh
    x_input = []
    x0 = get_offset(lungs_mesh, left_skin)
    for nid in xnids:
        xn = np.array(lungs_mesh.nodes[nid].values)
        xn[:, 0] -= x0
        x_input.extend(xn.flatten().tolist())
    for nid in skin_nodes:
        xn = np.array(left_skin.nodes[nid].values)
        xn[:, 0] -= x0
        x_input.extend(xn.flatten().tolist())
    for nid in skin_nodes:
        xn = np.array(right_skin.nodes[nid].values)
        xn[:, 0] -= x0
        x_input.extend(xn.flatten().tolist())
    x_input = np.array(x_input)

    # TODO. chinchien
    x_input = x_input.reshape(1, -1)
    # end TODO

    plsr = PLSRegression(copy=True, n_components=modes, scale=False)
    plsr.fit(X, Y)
    y_output = plsr.predict(x_input)[0]

    ribcage_mesh = morphic.Mesh()
    idx = 0
    for nid in ynids:
        ribcage_mesh.add_stdnode(nid, y_output[idx:idx + 12].reshape((3, 4)))
        ribcage_mesh.nodes[nid].values[:, 0] += x0
        idx += 12

    for elem in lungs_mesh.elements:
        ribcage_mesh.add_element(elem.id, ['H3', 'H3'], elem.node_ids)

    ribcage_mesh.generate()

    return ribcage_mesh


def load_ribcage_plsr_data(path_formats, include_subjects):
    xnids = [nid for nid in range(73) if nid not in [50, 52]]
    ynids = range(32)
    X, Y, included_subjects = [], [], []
    for sid in include_subjects:
        paths = [path_format % sid for path_format in path_formats]
        all_paths_exist = True
        for path in paths:
            if not os.path.exists(path):
                print('Mesh does not exist: %s' % path)
                all_paths_exist = False
        if all_paths_exist:
            included_subjects.append(sid)
            x = []
            x0 = None
            for path in paths[:2]:
                mesh = morphic.Mesh(path)
                if x0 is None:
                    x0 = 0.5 * (mesh.nodes[14].values[:, 0] + mesh.nodes[65].values[:, 0])
                for nid in xnids:
                    xn = np.array(mesh.nodes[nid].values)
                    xn[:, 0] -= x0
                    x.extend(xn.flatten().tolist())
            X.append(x)
            y = []
            ribcage_mesh = morphic.Mesh(paths[2])
            for nid in ynids:
                yn = np.array(ribcage_mesh.nodes[nid].values)
                yn[:, 0] -= x0
                y.extend(yn.flatten().tolist())
            Y.append(y)
    return np.array(X), np.array(Y), included_subjects


def predict_ribcage(left_mesh, right_mesh, X, Y, modes=6):

    xnids = [nid for nid in range(73) if nid not in [50, 52]]
    ynids = range(32)

    # Load input data using left and right mesh
    x_input = []
    x0 = 0.5 * (left_mesh.nodes[14].values[:, 0] + left_mesh.nodes[65].values[:, 0])
    for nid in xnids:
        xn = np.array(left_mesh.nodes[nid].values)
        xn[:, 0] -= x0
        x_input.extend(xn.flatten().tolist())
    for nid in xnids:
        xn = np.array(right_mesh.nodes[nid].values)
        xn[:, 0] -= x0
        x_input.extend(xn.flatten().tolist())

    x_input = np.array([x_input])

    plsr = PLSRegression(copy=True, n_components=modes, scale=False)
    plsr.fit(X, Y)
    y_output = plsr.predict(x_input)[0]

    ribcage_mesh = morphic.Mesh()
    idx = 0
    for nid in ynids:
        ribcage_mesh.add_stdnode(nid, y_output[idx:idx + 12].reshape((3, 4)))
        ribcage_mesh.nodes[nid].values[:, 0] += x0
        idx += 12

    elements = [
        [0, 1, 8, 9], [1, 2, 9, 10], [2, 3, 10, 11], [3, 4, 11, 12],
        [4, 5, 12, 13], [5, 6, 13, 14], [6, 7, 14, 15], [7, 0, 15, 8],
        [8, 9, 16, 17], [9, 10, 17, 18], [10, 11, 18, 19], [11, 12, 19, 20],
        [12, 13, 20, 21], [13, 14, 21, 22], [14, 15, 22, 23], [15, 8, 23, 16],
        [16, 17, 24, 25], [17, 18, 25, 26], [18, 19, 26, 27], [19, 20, 27, 28],
        [20, 21, 28, 29], [21, 22, 29, 30], [22, 23, 30, 31], [23, 16, 31, 24]]
    for eid, elnds in enumerate(elements):
        ribcage_mesh.add_element(eid, ['H3', 'H3'], elnds)

    ribcage_mesh.generate()

    return ribcage_mesh


def run(process):
    actions = ['fit_pca', 'fit_pca2', 'fit_left', 'fit_right', 'join_skin', 'fit_lungs', 'predict_ribcage', 'create_prone_mesh']
    print('Actions: ', actions)
    process.set_param('actions', actions)

    subject_id = None
    if process.parent is not None and process.parent.has_metadata():
        # extract_process_metadata(process)
        extract_metadata(process)
        metadata = process.metadata
        if 'subject' in metadata.keys() and 'id' in metadata['subject'].keys() and metadata['subject']['id'][:2] == 'VL':
            subject_id = int(metadata['subject']['id'][2:])
    else:
        subject_id = process.params.get('subject_id')
    print('Subject id:', subject_id)

    # TODO. chinchien.
    # extras_dir = os.path.join(process.project.root_dir, 'extras')
    extras_dir = process.metadata.get("project").get("extras_dir")

    print('Loading segmentations')
    if process.parent is None:
        cloud_path = os.path.join(process.params.get('source_dir'), 'CL%05d' % subject_id)
    else:
        cloud_path = process.parent.workspace('generate_point_cloud', False).path()

    mesh_wksp = process.workspace('mesh', True)
    mesh_path = mesh_wksp.path()

    # TODO. chinchien. copy files
    copy_files(cloud_path, mesh_path, strings=["nipple"])

    generate_mesh(cloud_path, mesh_path, extras_dir, subject_id, actions=actions)

    update_metadata(process)
    process.completed()

def copy_files(source_dir, dest_dir, strings=list()):
    """
    Copy files if the filenames contain one of the strings in the given list

    :param source_dir: path to the source directory
    :type source_dir: string
    :param dest_dir: path to the destination directory
    :type dest_dir: string
    :param strings: a list of strings
    :type strings: list
    :return:
    :rtype:
    """
    files = os.listdir(source_dir)
    for file in files:
        for string in strings:
            if string in file.lower():
                input_file = os.path.join(source_dir, file)
                output_file = os.path.join(dest_dir, file)
                copyfile(input_file, output_file)
                continue

def generate_mesh(cloud_path, mesh_path, extras_dir, subject_id, actions=None):
    if not actions:
        print("Action not found!")
        return

    print('Actions: ', actions)
    print('Subject id:', subject_id)

    # Lungs missing: 20
    subjects = [i for i in range(20, 81) if i not in [20, 22, 26, 32, 42, 43, 44, 64, 73, 78]]
    if subject_id in subjects:
        subjects.remove(subject_id)  # Leave-one-out

    print('Loading segmentations')
    lungs_data = morphic.Data(os.path.join(cloud_path, 'lungs_pts.data'))
    skin_data = morphic.Data(os.path.join(cloud_path, 'skin_pts.data'))
    nipple_data = morphic.Data(os.path.join(cloud_path, 'nipple_points.data'))
    lungs_data_values = lungs_data.values
    skin_data_values = skin_data.values
    nipple_data_values = nipple_data.values

    if actions is None or 'fit_pca' in actions:
        """ Generate and fit PCA meshes of the lungs, left skin and right skin """
        print('PCA fit of lungs, left skin and right skin')

        data = {
            'skin': {'data': skin_data_values},
            'lungs': {'data': lungs_data_values},
            'nipples': {'data': nipple_data_values},
        }

        # Generate PCA Meshes
        bad_skin_subject_ids = [26, 32, 38, 42, 43, 44, 53, 54, 56, 61, 64, 65, 70, 71, 73, 78, 79, 82, 86, 87, 90,
                                95, 109, 111, 113]
        bad_lung_ids = [20, 21, 22, 26, 57, 61, 64, 70, 75]

        path_formats = {'left': os.path.join(extras_dir, 'meshes', 'skin_left', 'gen1', 'VL%05d_prone.mesh'),
                        'right': os.path.join(extras_dir, 'meshes', 'skin_right', 'gen1', 'VL%05d_prone.mesh'),
                        'lungs': os.path.join(extras_dir, 'meshes', 'lungs', 'gen1', 'VL%05d_lungs_prone.mesh')}

        for sid in range(20, 81):
            path = path_formats['lungs'] % sid
            if os.path.exists(path):
                print(path)
                mesh = morphic.Mesh(path)
                if 'std' not in mesh.nodes[0].groups():
                    print('Adding group std to %d' % sid)
                    for node in mesh.nodes:
                        node.add_to_group('std')
                    mesh.save(path)
                else:
                    break

        # Extract paths and origins for combined PCA
        origins = {}
        pca_paths = {}
        for sid in range(23, 81):
            paths = []
            if sid != subject_id and sid not in bad_skin_subject_ids and sid not in bad_lung_ids:
                path = os.path.join(extras_dir, 'meshes', 'skin_left', 'gen1', 'VL%05d_prone.mesh' % sid)
                if os.path.exists(path):
                    mesh = morphic.Mesh(path)
                    origins[sid] = mesh.nodes[0].values[:, 0]
                    for side in ['left', 'right', 'lungs']:
                        paths.append(path_formats[side] % sid)
                    pca_paths[sid] = paths

        pca_meshes = automesh.generate_pca_meshes_v2(pca_paths, origins, groups='std', modes=24)

        meshes = {'left': pca_meshes[0].mesh, 'right': pca_meshes[1].mesh, 'lungs': pca_meshes[2].mesh}

        # Fit skin and lungs PCA meshes
        meshes = init_pca_mesh(meshes, nipple_data_values)
        for nmodes in [7]:
            print('Fitted PCA meshes for %d modes' % nmodes)
            meshes = pca_fit_skin_lungs(meshes, data, num_modes=nmodes)
            for side in ['left', 'right', 'lungs']:
                meshes[side].save('%s/skin_%s_prone_%dmode_pca.mesh' % (mesh_path, side, nmodes))
            for side in ['left', 'right']:
                mesh = collapse_skin_pca_mesh(meshes[side])
                mesh.save('%s/skin_%s_prone_%dmode.mesh' % (mesh_path, side, nmodes))
            mesh = collapse_pca_mesh(meshes['lungs'], range(32), range(24))
            mesh.save('%s/lungs_prone_%dmode.mesh' % (mesh_path, nmodes))

    if actions is None or 'fit_pca2' in actions:

        data = {
            'skin': {'data': skin_data_values},
            'lungs': {'data': lungs_data_values},
            'nipples': {'data': nipple_data_values},
        }

        meshes = {}
        for side in ['left', 'right', 'lungs']:
            meshes[side] = morphic.Mesh('%s/skin_%s_prone_%dmode_pca.mesh' % (mesh_path, side, 7))

        nmodes = 15
        print('Fitted PCA meshes anterior surface for %d modes' % nmodes)
        meshes = pca_fit_skin_stage2(meshes, data, num_modes=nmodes)
        for side in ['left', 'right']:
            meshes[side].save('%s/skin_%s_prone_stage2b_pca.mesh' % (mesh_path, side))
            mesh = collapse_skin_pca_mesh(meshes[side])
            mesh.save('%s/skin_%s_prone_stage2b.mesh' % (mesh_path, side))

    smooth_mode = 7
    if actions is None or 'fit_left' in actions:
        pca_mesh = morphic.Mesh(os.path.join(mesh_path, 'skin_left_prone_stage2b_pca.mesh'))
        pca_mesh.nodes['weights'].values[smooth_mode:] *= 0
        pca_mesh.update_pca_nodes(True)
        pca_mesh.translate('dx', groups=['std', 'pca'])
        left_mesh = collapse_skin_pca_mesh(pca_mesh)

        pca_mesh = morphic.Mesh(os.path.join(mesh_path, 'skin_right_prone_stage2b_pca.mesh'))
        pca_mesh.nodes['weights'].values[smooth_mode:] *= 0
        pca_mesh.update_pca_nodes(True)
        pca_mesh.translate('dx', groups=['std', 'pca'])

        zmin = np.min([left_mesh.nodes[42].values[2, 0], pca_mesh.nodes[42].values[2, 0]])

        for nid in [42, 43, 44, 45, 46, 47, 48, 53, 70, 71, 72, 73]:
            left_mesh.nodes[nid].values[2, 0] = zmin

        # Filter skin data using the bounds of the mesh.
        Xs = np.array(skin_data_values)
        ii = Xs[:, 2] < left_mesh.nodes[0].values[2, 0]
        Xs = Xs[ii, :]
        ii = Xs[:, 1] < left_mesh.nodes[0].values[1, 0]
        Xs = Xs[ii, :]

        left_mesh = fit_skin_mesh(left_mesh, Xs)
        left_mesh.save(os.path.join(mesh_path, 'skin_left_prone_fit1.mesh'))
        # left_mesh = fit_skin_mesh(left_mesh, Xs, stage=2)
        # left_mesh.save(os.path.join(mesh_path, 'skin_left_prone_fit2.mesh'))

    if actions is None or 'fit_right' in actions:
        pca_mesh = morphic.Mesh(os.path.join(mesh_path, 'skin_right_prone_stage2b_pca.mesh'))
        pca_mesh.nodes['weights'].values[smooth_mode:] *= 0
        pca_mesh.update_pca_nodes(True)
        pca_mesh.translate('dx', groups=['std', 'pca'])
        right_mesh = collapse_skin_pca_mesh(pca_mesh)

        left_mesh = morphic.Mesh(os.path.join(mesh_path, 'skin_left_prone_fit1.mesh'))
        for nid in [42, 43, 44, 45, 46, 47, 48, 53, 70, 71, 72, 73]:
            right_mesh.nodes[nid].values[2, 0] = left_mesh.nodes[nid].values[2, 0]

        # Filter skin data using the bounds of the mesh.
        Xs = np.array(skin_data_values)
        ii = Xs[:, 2] < right_mesh.nodes[0].values[2, 0]
        Xs = Xs[ii, :]
        ii = Xs[:, 1] > right_mesh.nodes[0].values[1, 0]
        Xs = Xs[ii, :]

        # Fit mesh
        right_mesh = fit_skin_mesh(right_mesh, Xs)
        right_mesh.save(os.path.join(mesh_path, 'skin_right_prone_fit1.mesh'))
        # right_mesh = fit_skin_mesh(right_mesh, Xs, stage=2)
        # right_mesh.save(os.path.join(mesh_path, 'skin_right_prone_fit2.mesh'))

    if actions is None or 'join_skin' in actions:
        print('Joining skin meshes')
        left_mesh = morphic.Mesh(os.path.join(mesh_path, 'skin_left_prone_fit1.mesh'))
        right_mesh = morphic.Mesh(os.path.join(mesh_path, 'skin_right_prone_fit1.mesh'))
        left_mesh, right_mesh = fit_skin_seam('anterior', left_mesh, right_mesh, skin_data_values)
        left_mesh, right_mesh = fit_skin_seam('posterior', left_mesh, right_mesh, skin_data_values)
        left_mesh.save(os.path.join(mesh_path, 'skin_left_prone.mesh'))
        right_mesh.save(os.path.join(mesh_path, 'skin_right_prone.mesh'))

    bad_lung_ids = [20, 21, 22, 26, 57, 61, 64, 70, 75]
    # if actions is None or 'fit_lungs' in actions:
    #     print 'Fitting lungs'
    #     lungs_path = os.path.join(extras_dir, 'meshes', 'lungs', 'gen1', 'VL%05d_lungs_prone.mesh')
    #     lungs_paths = [lungs_path % sid for sid in range(20, 81)
    #                    if sid not in bad_lung_ids and sid != subject_id]
    #
    #     left_mesh = morphic.Mesh(os.path.join(mesh_path, 'skin_left_prone.mesh'))
    #     z_base = left_mesh.nodes[42].values[2, 0]
    #
    #     lungs_pca_mesh = automesh.generate_pca_mesh(lungs_paths, origin_node=0, modes=24)
    #     lungs_pca_mesh = pca_fit_lungs(lungs_pca_mesh, lungs_data, z_base, num_modes=6)
    #     lungs_pca_mesh.save(os.path.join(mesh_path, 'lungs_prone_pca.mesh'))
    #     lungs_mesh = collapse_lungs_pca_mesh(lungs_pca_mesh)
    #     lungs_mesh.save(os.path.join(mesh_path, 'lungs_prone.mesh'))

    if actions is None or 'predict_ribcage' in actions:
        print('Predicting Ribcage')
        path_formats = [
            os.path.join(extras_dir, 'meshes', 'lungs', 'gen1', 'VL%05d_lungs_prone.mesh'),
            os.path.join(extras_dir, 'meshes', 'skin_left', 'gen1', 'VL%05d_prone.mesh'),
            os.path.join(extras_dir, 'meshes', 'skin_right', 'gen1', 'VL%05d_prone.mesh'),
            os.path.join(extras_dir, 'meshes', 'ribcage', 'gen3', 'VL%05d_ribcage_prone.mesh'),
        ]
        included_subject_ids = [sid for sid in range(23, 81)
                                if sid not in bad_lung_ids and sid != subject_id]

        X, Y, included_subjects = load_lungs_ribcage_plsr_data(path_formats, included_subject_ids, skin_nodes='all')

        lungs_mesh = morphic.Mesh(os.path.join(mesh_path, 'lungs_prone_7mode.mesh'))
        left_skin = morphic.Mesh(os.path.join(mesh_path, 'skin_left_prone.mesh'))
        right_skin = morphic.Mesh(os.path.join(mesh_path, 'skin_right_prone.mesh'))
        ribcage_mesh = predict_lungs_to_ribcage(lungs_mesh, left_skin, right_skin, X, Y, skin_nodes='all')
        ribcage_mesh.save(os.path.join(mesh_path, 'ribcage_prone.mesh'))

    # TODO. chinchien. create torso mesh
    if actions is None or 'create_prone_mesh' in actions:
        print('Creating prone mesh')
        create_prone_mesh(mesh_path, subject_id)

def create_prone_mesh(mesh_path, subject_id):
    volunteer_id = subject_id
    save_path = mesh_path

    p = {
        'debug' : False,
        'offscreen': True,
        'mesh_dir': mesh_path,
        'results_dir': save_path,
        'volunteer_id': volunteer_id,
        'offset' : 0,
        'breast_stiffnesses' : scipy.array([0.3,  0.2925,  0.285]),
        'boundary_stiffnesses' : scipy.array([5., 100.,100.,2.]),
        'force_full_mechanics_solve' : True,
        'field_export_name' : 'field'}
    params = automesh.Params(p)
    print('Volunteer id: ', params.volunteer_id)
    if params.offscreen:
        fig = None
        viewer = None
    else:
        from morphic import viewer
    fig = bmw.add_fig(viewer, label='mesh') # returns empty array if offscreen

    # Load fitted chest wall surface (cwm)
    cwm_fname = os.path.join(mesh_path, 'ribcage_prone.mesh')
    if os.path.exists(cwm_fname):
        cwm = morphic.Mesh(cwm_fname)
        cwm.label = 'cwm'
    else:
        message = 'ribcage mesh not found'
        print(message)

    # Load rhs and lhs fitted breast surface (bm)
    bm_rhs_fname = os.path.join(mesh_path, 'skin_right_prone.mesh')
    if os.path.exists(bm_rhs_fname):
        bm_rhs = morphic.Mesh(bm_rhs_fname)
        bm_rhs.label = 'bm_rhs'
    else:
        message = 'rhs skin mesh not found'
        print(message)

    bm_lhs_fname = os.path.join(mesh_path, 'skin_left_prone.mesh')
    if os.path.exists(bm_lhs_fname):
        bm_lhs = morphic.Mesh(bm_lhs_fname)
        bm_lhs.label = 'bm_lhs'
    else:
        message = 'lhs skin mesh not found'
        print(message)

    if params.debug:
        bmw.visualise_mesh(cwm, fig, visualise=False, face_colours=(1,0,0))
        bmw.visualise_mesh(bm_rhs, fig, visualise=False, face_colours=(1,1,0), opacity=0.75)
        bmw.visualise_mesh(bm_lhs, fig, visualise=False, face_colours=(1,1,0), opacity=0.75)

    # Add missing elements to the shoulder region of the breast surface mesh
    bmw.add_shoulder_elements(bm_rhs,'rhs', adjacent_nodes=[[6,54],[13,58]], armpit_nodes=[20,49,62])
    bmw.add_shoulder_elements(bm_lhs,'lhs', adjacent_nodes=[[6,54],[13,58]], armpit_nodes=[20,49,62])

    if params.debug:
        bmw.visualise_mesh(cwm, fig, visualise=False, face_colours=(1,0,0), nodes='all', node_size=1, node_text=True, element_ids=True)
        bmw.visualise_mesh(bm_rhs, fig, visualise=False, face_colours=(1,1,0), opacity=0.75, nodes='all', node_size=1, node_text=True, element_ids=True)
        bmw.visualise_mesh(bm_lhs, fig, visualise=False, face_colours=(1,1,0), opacity=0.75, nodes='all', node_size=1, node_text=True, element_ids=True)

    # Create new breast surface mesh
    Xe = [[0,1,2,3,4,5,54,55,42,43,44],
        [6,7,8,9,10,11,56,57,45,46,47],
        [12, 13, 14, 15, 16, 17, 36, 37, 48, 49, 50],
        [18, 19, 20, 21, 22, 23, 38, 37, 48, 49, 50],
        [24, 25, 26, 27, 28, 29, 39, 40, 51, 52, 53],
        [30, 31, 32, 33, 34, 35, 41, 40, 51, 52, 53]]
    hanging_e = [ None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,
        None,  None,  None,  None,  None,  None,  None,  None,  None,  None,  None,
        None,  None,  None,  None,  None,  None,  None,  [[0.,1.],[0.0, 0.4]],  [[0.,1.],[0.0, 0.4]],  [[0.,1.],[0.0, 0.4]],  [[0.,1.],[0.0, 0.4]],
        None,  None,  None,  None,  None,  None,  None,  [[0.,1.],[0.4, 1.0]],  [[0.,1.],[0.4, 1.0]],  [[0.,1.],[0.4, 1.0]],  [[0.,1.],[0.4, 1.0]],
        None,  None,  None,  None,  None,  None,  None,  [[0.,1.],[0., 0.50]],  [[0.,1.],[0., 0.50]],  [[0.,1.],[0., 0.50]],  [[0.,1.],[0., 0.50]],
        None,  None,  None,  None,  None,  None,  None,  [[0.,1.],[0.50, 1.]],  [[0.,1.],[0.50, 1.]],  [[0.,1.],[0.50, 1.]],  [[0.,1.],[0.50, 1.]]]

    new_bm_rhs, _ = bmw.create_surface_mesh(fig, 'new_bm_rhs', bm_rhs, Xe, hanging_e, params.offset, visualise=False)
    new_bm_lhs, _ = bmw.create_surface_mesh(fig, 'new_bm_lhs', bm_lhs, Xe, hanging_e, params.offset, visualise=False)

    if params.debug:
        #import ipdb; ipdb.set_trace()
        bmw.visualise_mesh(cwm, fig, visualise=False, face_colours=(1,0,0), nodes='all', node_size=1, node_text=True, element_ids=True)
        bmw.visualise_mesh(new_bm_rhs, fig, visualise=False, face_colours=(1,1,0), opacity=0.75, nodes='all', node_size=1, node_text=True, element_ids=True)
        bmw.visualise_mesh(new_bm_lhs, fig, visualise=False, face_colours=(1,1,0), opacity=0.75, nodes='all', node_size=1, node_text=True, element_ids=True)

    # Create new chestwall surface mesh
    Xe_rhs = scipy.array([[0, 1, 2, 3],
                          [ 8,  9, 10, 11],
                          [16, 17, 18, 19]])
    new_cwm_rhs = bmw.reposition_nodes(fig, cwm, new_bm_rhs, params.offset, side='rhs', xi1_Xe=Xe_rhs, elem_shape=scipy.array(Xe).shape[::-1], debug=False)

    Xe_lhs = scipy.array(Xe_rhs)
    temp =  scipy.array([0,8,16])
    for row in range(Xe_lhs.shape[0]):
        Xe_lhs[row,:] = 7-scipy.array(Xe_rhs[0])+temp[row]
    new_cwm_lhs = bmw.reposition_nodes(fig, cwm, new_bm_lhs, params.offset, side='lhs', xi1_Xe=Xe_lhs, elem_shape=scipy.array(Xe).shape[::-1], debug=False)

    if params.debug:
        bmw.visualise_mesh(new_cwm_rhs, fig, visualise=False, face_colours=(1,1,0))
        bmw.visualise_mesh(new_cwm_lhs, fig, visualise=False, face_colours=(1,1,0))

    # Create new volume mesh
    mesh3D_rhs = bmw.create_volume_mesh(
        new_bm_rhs, new_cwm_rhs, 'rhs', params.offset, fig, [], skin=False,
        skin_thickness=1.45,smoothing=1)
    mesh3D_rhs.label = 'mesh3D_rhs'

    mesh3D_lhs = bmw.create_volume_mesh(
        new_bm_lhs, new_cwm_lhs, 'lhs', params.offset, fig, [], skin=False,
        skin_thickness=1.45,smoothing=1)
    mesh3D_lhs.label = 'mesh3D_lhs'

    bmw.generate_boundary_groups(mesh3D_rhs, fig, side='rhs', visualise_points=False, visualise_nodes=False, export_groups=True, export_folder=params.results_dir)
    bmw.generate_boundary_groups(mesh3D_lhs, fig, side='lhs', visualise_points=False, visualise_nodes=False, export_groups=True, export_folder=params.results_dir)

    if params.debug:
        bmw.visualise_mesh(mesh3D_rhs, fig, visualise=False, face_colours=(0,1,0),pt_size=1, opacity=0.25, line_opacity=0.75)
        bmw.visualise_mesh(mesh3D_lhs, fig, visualise=False, face_colours=(0,1,0),pt_size=1, opacity=0.25, line_opacity=0.75)

    # Load sternum/spine node groups
    # TODO use dictionaries to store dof groups and add to metadata
    hdf5_main_grp = h5py.File('{0}/dof_groups_{1}.h5'.format(params.results_dir,'rhs'), 'r')
    rhs_sternum_nodes = hdf5_main_grp['/nodes/sternum'][()].T
    rhs_spine_nodes = hdf5_main_grp['/nodes/spine'][()].T
    hdf5_main_grp = h5py.File('{0}/dof_groups_{1}.h5'.format(params.results_dir,'lhs'), 'r')
    lhs_sternum_nodes = hdf5_main_grp['/nodes/sternum'][()].T
    lhs_spine_nodes = hdf5_main_grp['/nodes/spine'][()].T
    lhs_Xn_offset = 10000
    lhs_Xe_offset = len(mesh3D_rhs.get_element_cids())
    torso_mesh = bmw.join_lhs_rhs_meshes(mesh3D_lhs, mesh3D_rhs, fig, 'torso_mesh', scipy.hstack([rhs_sternum_nodes, rhs_spine_nodes]), scipy.hstack([lhs_sternum_nodes, lhs_spine_nodes]), lhs_Xn_offset=lhs_Xn_offset, lhs_Xe_offset=lhs_Xe_offset)
    if params.debug:
        bmw.visualise_mesh(torso_mesh, fig, visualise=False, face_colours=(0,1,1),pt_size=1, opacity=0.75, line_opacity = 0.75, text=False)
    bmw.generate_boundary_groups(torso_mesh, fig, side='both', visualise_points=False, visualise_nodes=False, export_groups=True, export_folder=params.results_dir, lhs_Xn_offset=lhs_Xn_offset, lhs_Xe_offset=lhs_Xe_offset, debug=False)
    h5_dof_groups = h5py.File('{0}/dof_groups_{1}.h5'.format(params.results_dir, 'both'), 'r')
    stiffer_shoulder_nodes = h5_dof_groups['/nodes/stiffer_shoulder'][()].T
    fixed_shoulder_nodes = h5_dof_groups['/nodes/fixed_shoulder'][()].T
    stiffer_back_nodes = h5_dof_groups['/nodes/stiffer_back'][()].T
    transitional_nodes = h5_dof_groups['/nodes/transitional'][()].T
    bmw.plot_points(fig, 'stiffer_shoulder_nodes', torso_mesh.get_nodes(stiffer_shoulder_nodes.tolist()), stiffer_shoulder_nodes, visualise=False, colours=(0,0,1), point_size=10, text_size=5)
    bmw.plot_points(fig, 'fixed_shoulder_nodes', torso_mesh.get_nodes(fixed_shoulder_nodes.tolist()), fixed_shoulder_nodes, visualise=False, colours=(1,0,0), point_size=10, text_size=5)
    bmw.plot_points(fig, 'stiffer_back_nodes', torso_mesh.get_nodes(stiffer_back_nodes.tolist()), stiffer_back_nodes, visualise=False, colours=(0,1,0), point_size=10, text_size=5)
    bmw.plot_points(fig, 'transitional_nodes', torso_mesh.get_nodes(transitional_nodes.tolist()), transitional_nodes, visualise=False, colours=(1,1,0), point_size=10, text_size=5)

    print('Mesh construction complete.')

    mesh_quality = bmw.check_mesh_quality(torso_mesh)

    # Save mesh quality jacobian to Morphic data
    jacobian_filepath = os.path.join(save_path, 'prone_jacobian.data')
    jacobian_data = morphic.Data()
    jacobian_data.values = mesh_quality['jacobians']
    jacobian_data.save(jacobian_filepath)
    torso_mesh.metadata['prone_mesh'] = {
        'setup': p,
        'mesh_generation_parameters': [],
        'jacobian_file': jacobian_filepath}
    # Only Jacobian stored in Morphic data, remaining mesh quality data
    # stored in generic hdf5 dataset
    # TODO. chinchien. check the line below. for now, commented it
    # bmw.export_mesh_quality_data(mesh_quality, os.path.join(save_path, 'prone_mesh_quality.h5'))

    # TODO. below is Prasad's new code for:
    # export of the torso mesh in obj
    # generation of skin and outer rib points

    # Transform morphic mesh node coordinates.
    # Imaging metadata for VL00001.
    # image_origin = [-219.5572052001953, -164.0460968017578, -63.32743453979492]
    # image_spacing = [1.0044642686843872, 1.0044642686843872, 0.8999999761581421]
    # image_size = [448, 448, 208]
    image_origin = [-180.70217917081, -152.88135524873, -83.468521118164]
    image_spacing = [0.9375, 0.9375, 3]
    image_size = [384, 384, 56]

    for node in torso_mesh.nodes:
        node.values[:] = transformPointToImageSpace(node.values, image_origin, image_spacing, image_size)

    meshio_mesh = mesh_tools.morphic_to_meshio(
        torso_mesh, triangulate=True, res=8, exterior_only=True)

    meshio_mesh.write(os.path.join(save_path, 'prone.vtk'))
    meshio_mesh.write(os.path.join(save_path, 'prone.obj'))

    def export_points(points, output_file):
        data = {
            'Datapoints': points.tolist()
        }
        with open(output_file + ".json", 'w') as outfile:
            json.dump(data, outfile, indent=4)
        # save cloud to txt
        np.savetxt(output_file + ".txt", points, delimiter=',')

    skin_mesh_surface_points, _, _ = mesh_tools.generate_points_morphic_face(
        torso_mesh, "xi3", 1, num_points=[10, 10], element_ids=[], dim=3)

    export_points(
        skin_mesh_surface_points,
        os.path.join(save_path, 'skin_mesh_surface_points'))

    outer_rib_mesh_surface_points, _, _ = mesh_tools.generate_points_morphic_face(
        torso_mesh, "xi3", 0, num_points=[10, 10], element_ids=[], dim=3)

    export_points(
        outer_rib_mesh_surface_points,
        os.path.join(save_path, 'outer_rib_mesh_surface_points'))
    # END TODO


    # torso_mesh = set_metadata(torso_mesh, process)
    torso_mesh.save(os.path.join(save_path, 'prone.mesh'))
    morphic.Mesh(os.path.join(save_path, 'prone.mesh')).export(os.path.join(mesh_path, 'prone.json'))

    message = 'Num bad guass points in prone mesh: {0}'.format(
        mesh_quality['num_bad_gauss_points'])
    print(message)

def extract_process_metadata(process):
    parent = process.parent
    if not parent.has_metadata():
        return

    process.clear_metadata()
    for key in parent.metadata.keys():
        process.set_metadata(key, parent.metadata[key])

    pipeline = process.parent.metadata['bpm_pipeline']
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
    process.set_metadata('bpm_pipeline', pipeline)


def set_metadata(mesh, process):
    m = process.metadata
    for key in m.keys():
        mesh.metadata[key] = m[key]
    return mesh


if __name__ == "__main__":
    # import workflow_manager
    # run(workflow_manager.get_project_process())

    # # usage example
    # # subject_id = 28
    # subject_id = "1.3.6.1.4.1.14519.5.2.1.160280964313719412347933524460119440797"
    # cloud_path = "/home/clin864/eresearch/sandbox/chinchien/workflow_Duke-Breast-Cancer-MRI/results/1.3.6.1.4.1.14519.5.2.1.160280964313719412347933524460119440797/cloud"
    # mesh_path = "/home/clin864/eresearch/sandbox/chinchien/workflow_Duke-Breast-Cancer-MRI/results/1.3.6.1.4.1.14519.5.2.1.160280964313719412347933524460119440797/mesh"
    #
    # extras_dir = "/home/clin864/opt/automated-workflows/services/modelling/resources/extras"
    # actions = ['fit_pca', 'fit_pca2', 'fit_left', 'fit_right', 'join_skin', 'fit_lungs', 'predict_ribcage',
    #            'create_prone_mesh']
    # generate_mesh(cloud_path, mesh_path, extras_dir, subject_id, actions=actions)

    subject_id = 1
    cloud_path = "/home/clin864/eresearch/sandbox/clin864/workflow_Duke-Breast-Cancer-MRI/results/Breast_MRI_014/0000/prone/model"
    mesh_path = "/home/clin864/eresearch/sandbox/clin864/workflow_Duke-Breast-Cancer-MRI/results/Breast_MRI_014/0000/prone/model"

    extras_dir = "/home/clin864/opt/automated-workflows/services/modelling/resources/extras"
    actions = ['fit_pca', 'fit_pca2', 'fit_left', 'fit_right', 'join_skin', 'fit_lungs', 'predict_ribcage',
               'create_prone_mesh']
    generate_mesh(cloud_path, mesh_path, extras_dir, subject_id, actions=actions)
