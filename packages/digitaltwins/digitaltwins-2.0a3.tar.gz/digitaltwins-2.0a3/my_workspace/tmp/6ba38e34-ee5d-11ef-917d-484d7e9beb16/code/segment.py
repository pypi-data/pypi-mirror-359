'''
Created on 7/04/2020
​
@author: gonzalo, Chinchien
'''

import tensorflow as tf
import numpy as np
import time
import math
import nibabel
import os
import json

import breast_metadata
import morphic

script_id = 'segment'
run_program = 'python3'
run_script = 'segment.py'
depends_on = ['dicom_to_nifti']


class UNet(object):
    '''
    U-Net model for axial image inputs.
    '''

    def __init__(self, patch):
        '''
        Constructor
        '''
        self.patch = patch

    def create_graph(self):
        inputs = self.patch
        conv1 = tf.compat.v1.layers.Conv2D(64, 3, activation=tf.compat.v1.nn.relu, padding='same')(inputs)
        conv1 = tf.compat.v1.layers.Conv2D(64, 3, activation=tf.compat.v1.nn.relu, padding='same')(conv1)
        pool1 = tf.compat.v1.layers.MaxPooling2D(2, 2)(conv1)

        conv2 = tf.compat.v1.layers.Conv2D(128, 3, activation=tf.compat.v1.nn.relu, padding='same')(pool1)
        conv2 = tf.compat.v1.layers.Conv2D(128, 3, activation=tf.compat.v1.nn.relu, padding='same')(conv2)
        pool2 = tf.compat.v1.layers.MaxPooling2D(2, 2)(conv2)

        conv3 = tf.compat.v1.layers.Conv2D(256, 3, activation=tf.compat.v1.nn.relu, padding='same')(pool2)
        conv3 = tf.compat.v1.layers.Conv2D(256, 3, activation=tf.compat.v1.nn.relu, padding='same')(conv3)
        pool3 = tf.compat.v1.layers.MaxPooling2D(2, 2)(conv3)

        conv4 = tf.compat.v1.layers.Conv2D(512, 3, activation=tf.compat.v1.nn.relu, padding='same')(pool3)
        conv4 = tf.compat.v1.layers.Conv2D(512, 3, activation=tf.compat.v1.nn.relu, padding='same')(conv4)
        drop4 = tf.compat.v1.layers.Dropout(0.5)(conv4)
        pool4 = tf.compat.v1.layers.MaxPooling2D(2, 2)(drop4)

        conv5 = tf.compat.v1.layers.Conv2D(1024, 3, activation=tf.compat.v1.nn.relu, padding='same')(pool4)
        conv5 = tf.compat.v1.layers.Conv2D(1024, 3, activation=tf.compat.v1.nn.relu, padding='same')(conv5)
        drop5 = tf.compat.v1.layers.Dropout(0.5)(conv5)

        up6 = tf.compat.v1.layers.Conv2DTranspose(512, 2, (2, 2), activation=tf.compat.v1.nn.relu, padding='same')(
            drop5)
        merge6 = tf.compat.v1.concat([drop4, up6], axis=3)
        conv6 = tf.compat.v1.layers.Conv2D(512, 3, activation=tf.compat.v1.nn.relu, padding='same')(merge6)
        conv6 = tf.compat.v1.layers.Conv2D(512, 3, activation=tf.compat.v1.nn.relu, padding='same')(conv6)

        up7 = tf.compat.v1.layers.Conv2DTranspose(256, 2, (2, 2), activation=tf.compat.v1.nn.relu, padding='same')(
            conv6)
        merge7 = tf.compat.v1.concat([conv3, up7], axis=3)
        conv7 = tf.compat.v1.layers.Conv2D(256, 3, activation=tf.compat.v1.nn.relu, padding='same')(merge7)
        conv7 = tf.compat.v1.layers.Conv2D(256, 3, activation=tf.compat.v1.nn.relu, padding='same')(conv7)

        up8 = tf.compat.v1.layers.Conv2DTranspose(128, 2, (2, 2), activation=tf.compat.v1.nn.relu, padding='same')(
            conv7)
        merge8 = tf.compat.v1.concat([conv2, up8], axis=3)
        conv8 = tf.compat.v1.layers.Conv2D(128, 3, activation=tf.compat.v1.nn.relu, padding='same')(merge8)
        conv8 = tf.compat.v1.layers.Conv2D(128, 3, activation=tf.compat.v1.nn.relu, padding='same')(conv8)

        up9 = tf.compat.v1.layers.Conv2DTranspose(64, 2, (2, 2), activation=tf.compat.v1.nn.relu, padding='same')(conv8)
        merge9 = tf.compat.v1.concat([conv1, up9], axis=3)
        conv9 = tf.compat.v1.layers.Conv2D(64, 3, activation=tf.compat.v1.nn.relu, padding='same')(merge9)
        conv9 = tf.compat.v1.layers.Conv2D(64, 3, activation=tf.compat.v1.nn.relu, padding='same')(conv9)
        conv9 = tf.compat.v1.layers.Conv2D(2, 3, activation=tf.compat.v1.nn.relu, padding='same')(conv9)

        #         logits = tf.layers.Conv2D(1, 1, activation = tf.sigmoid, padding = 'same')(conv9)

        return conv9


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


def extract_nipples(skin_image, output_file):
    im = breast_metadata.readNIFTIImage(skin_image)
    data = im.values
    spacing = im.spacing

    mid_point = int(np.round(im.shape[1] / 2))
    # Divide the image into two
    iml = np.zeros(data.shape)
    imr = np.zeros(data.shape)
    iml[:, 0:mid_point, :] = data[:, 0:mid_point, :]
    imr[:, mid_point:-1, :] = data[:, mid_point:-1, :]
    # Detect the points which are the furthest towards the front to detect the
    # nipples
    l = np.where(np.round(iml) == 1)
    r = np.where(np.round(imr) == 1)
    tp = np.zeros([3, 3])
    # Extract left nipple position
    tp[0, 0] = l[0][np.argmin(l[0])]
    tp[0, 1] = l[1][np.argmin(l[0])]
    tp[0, 2] = l[2][np.argmin(l[0])]
    # Extract right nipple position
    tp[1, 0] = r[0][np.argmin(r[0])]
    tp[1, 1] = r[1][np.argmin(r[0])]
    tp[1, 2] = r[2][np.argmin(r[0])]
    # Extract the skin point between the nipples
    tp[2, 1] = np.round((tp[0, 1] + tp[1, 1]) / 2)
    tp[2, 2] = np.round((tp[0, 2] + tp[1, 2]) / 2)
    tp[2, 0] = np.min(np.where(data[:, np.uint16(tp[2, 1]), np.uint16(tp[2, 2])]))
    tp[:, 0] = np.float32(tp[:, 0]) * spacing[0]
    tp[:, 1] = np.float32(tp[:, 1]) * spacing[1]
    tp[:, 2] = np.float32(tp[:, 2]) * spacing[2]

    output_data = {
        "nodes": {
            "right_nipple": list(tp[1]),
            "left_nipple": list(tp[0])
        },
        "elements": {}
    }

    with open(output_file + '.json', 'w') as outfile:
        json.dump(output_data, outfile, indent=4)

    data = morphic.Data()
    data.values = tp
    data.save(output_file + '.data')


def load_Nifti(path, filename):
    """
    Loads a volumetric Nifti file. It returns a volume with the file's data and its metadata.
    """
    proxy_data = nibabel.load(path + filename)
    proxy_data.affine[0:3, -1] = 0
    data = proxy_data.get_fdata()

    return data, proxy_data


def get_uncertainty(y_pred):
    entropy = tf.reduce_sum(- y_pred * tf.math.log(tf.clip_by_value(y_pred, 1e-6, 1.0)), axis=-1)
    return entropy


def get_batch(study, idx_batch, batch_size):
    offset = idx_batch * batch_size
    upper_limit = min(offset + batch_size, study.shape[2])
    image_batch = study[:, :, offset:upper_limit]
    image_batch = np.transpose(image_batch, (2, 0, 1))

    return image_batch.reshape(image_batch.shape + (1,))


def set_batch(study_prediction, predictions_batch, idx_batch, batch_size):
    offset = idx_batch * batch_size
    upper_limit = min(offset + batch_size, study_prediction.shape[2])
    predictions_batch = np.transpose(predictions_batch, (1, 2, 0))

    study_prediction[:, :, offset:upper_limit] = predictions_batch


def save_prediction(prediction, meta, output_file):
    meta.affine[0:3, -1] = 0
    save_data = nibabel.Nifti1Image(np.transpose(prediction, (1, 0, 2)), meta.affine)
    if (not os.path.exists(os.path.dirname(output_file))):
        os.mkdir(os.path.dirname(output_file))

    nibabel.save(save_data, output_file)


def predict_nii_with_model(input_file, output_file, UNet_model_path):
    batch_size = 4

    model = tf.keras.models.load_model(UNet_model_path)

    data, meta = load_Nifti("", input_file)

    #    Adjust dimensions to be a multiple of a certain factor
    prediction = np.zeros((data.shape[0], data.shape[1], data.shape[2]))
    #    Normalise study [0.0,1.0] range.
    prediction = data[:prediction.shape[0], :prediction.shape[1], :] / np.amax(data)

    study_processing_time_start = time.time()
    for idx_batch in range(0, int(math.ceil(data.shape[2] / batch_size))):
        image_batch = get_batch(prediction, idx_batch, batch_size)

        prob_predictions = model(image_batch)
        #             uncertainty = get_uncertainty(image_batch)
        predictions_batch = tf.math.argmax(prob_predictions, axis=-1)

        set_batch(prediction, predictions_batch, idx_batch, batch_size)

    elapsed = time.time() - study_processing_time_start
    print("Study {} processed in {}".format(input_file, elapsed))

    #    Adjust dimensions to be original size
    prediction = prediction[:data.shape[0], :data.shape[1], :data.shape[2]]

    save_prediction(prediction, meta, output_file)


def predict_nii_with_model_tf1(input_file, output_file, model_checkpoint):
    batch_size = 4

    with tf.compat.v1.Graph().as_default(), tf.compat.v1.Session() as sess:
        # load data
        data, meta = load_Nifti("", input_file)

        data = np.transpose(data, (1, 0, 2))
        data = data / np.amax(data)

        data_batch = np.zeros((batch_size, data.shape[0], data.shape[1], 1))
        prediction = np.zeros((data.shape[0], data.shape[1], data.shape[2]))

        # Create image tensor placeholder
        image_tf = tf.compat.v1.placeholder(tf.compat.v1.float32, [None, data.shape[0], data.shape[1], 1])
        # Get model architecture (nodes/operations/labels)
        model = UNet(image_tf)
        logits = model.create_graph()
        labels = tf.argmax(logits, axis=3)
        # Restore meta graph (model variables)
        saver = tf.compat.v1.train.Saver()
        saver.restore(sess, model_checkpoint)
        print("Model restored")

        # Multi-slice prediction
        not_finished = True
        frame = 0
        while (not_finished):
            prev_frame = frame

            for sample in range(0, batch_size):

                data_batch[sample, 0:data.shape[0], 0:data.shape[1], 0] = data[:, :, frame]
                frame = frame + 1
                if frame == data.shape[2]:
                    data_batch = data_batch[0:sample + 1, :, :, :]
                    not_finished = False
                    break

            prediction_batch = sess.run(labels, feed_dict={image_tf: data_batch})

            prediction[:, :, prev_frame:frame] = np.transpose(prediction_batch, (1, 2, 0))
            print("Frame {}/{}".format(frame, data.shape[2]))

        save_prediction(prediction, meta, output_file)


def run(process):
    extract_metadata(process)

    source_workspace = process.parent.get_workspace('dicom_to_nifti')
    dest_workspace = process.get_workspace('segment', True)
    source_path = source_workspace.path()
    dest_path = dest_workspace.path()

    files = os.listdir(source_path)
    filename = files[0]
    input_file = os.path.join(source_path, filename)

    # Segment lungs with TF1 model
    filename_lungs = "lungs.nii.gz"
    output_file = os.path.join(dest_path, filename_lungs)
    model_path = process.metadata.get("project").get("lung_model")
    predict_nii_with_model_tf1(input_file=input_file,
                               output_file=output_file,
                               model_checkpoint=model_path)

    # Segment skin with TF1 model
    filename_skin = "skin.nii.gz"
    output_file = os.path.join(dest_path, filename_skin)
    model_path = process.metadata.get("project").get("skin_model")
    predict_nii_with_model_tf1(input_file=input_file,
                               output_file=output_file,
                               model_checkpoint=model_path)

    # Extract the nipple
    filename_nipples = "nipple_points"
    output_file = os.path.join(dest_path, filename_nipples)
    skin_image = os.path.join(dest_path, filename_skin)
    extract_nipples(skin_image, output_file)

    update_metadata(process)
    process.completed()


if __name__ == "__main__":
    import workflow_manager
    run(workflow_manager.get_project_process())

    # Example of usage

    # TF1 models

    # VL Prone

    # # Skin t1
    # model_checkpoint = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/body/imagewise/UNet/test_training_t1_batch16/best_accuracy-8"
    # # Skin t2
    # model_checkpoint = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/body/imagewise/UNet/test_training_t2_batch16/best_accuracy-26"
    #
    # predict_nii_with_model_tf1(
    #     input_file="/home/clin864/hpc/data/breast/VL01/00035/VL00035_t1.nii.gz",
    #     output_file="/home/clin864/hpc/data/breast/VL01/00035/segmentations/t1_prone/body.nii.gz",
    #     model_checkpoint=model_checkpoint)
    #
    # # # Lungs t1
    # model_checkpoint = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/lung/imagewise/UNet/test_training_T1_batch16/best_accuracy-5"
    # # # Lungs t2
    # # model_checkpoint = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/lung/imagewise/UNet/test_training_T2_batch16/best_accuracy-6"
    #
    # predict_nii_with_model_tf1(
    #     input_file="/home/clin864/hpc/data/breast/VL01/00035/VL00035_t1.nii.gz",
    #     output_file="/home/clin864/hpc/data/breast/VL01/00035/segmentations/t1_prone/lungs.nii.gz",
    #     model_checkpoint=model_checkpoint)
    #
    # # Nipples extraction
    # skin_image = "/home/clin864/hpc/data/breast/VL01/00035/segmentations/t1_prone/body.nii.gz"
    # output_file = "/home/clin864/hpc/data/breast/VL01/00035/segmentations/t1_prone/nipple_points_new"
    # extract_nipples(skin_image, output_file)

    # # todo. Duke dataset
    # input_dir = "/home/clin864/eresearch/sandbox/chinchien/workflow_Duke-Breast-Cancer-MRI/results/1.3.6.1.4.1.14519.5.2.1.160280964313719412347933524460119440797"
    # output_dir = "/home/clin864/eresearch/sandbox/chinchien/workflow_Duke-Breast-Cancer-MRI/results/1.3.6.1.4.1.14519.5.2.1.160280964313719412347933524460119440797/segment"
    # image = os.path.join(input_dir, "1.3.6.1.4.1.14519.5.2.1.160280964313719412347933524460119440797.nii.gz")
    # skin = os.path.join(output_dir, "body.nii.gz")
    # lung = os.path.join(output_dir, "lung.nii.gz")
    # nipple = os.path.join(output_dir, "nipple_points")
    # # T1
    # # Skin
    # model_checkpoint = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/body/imagewise/UNet/test_training_t1_batch16/best_accuracy-8"
    # predict_nii_with_model_tf1(
    #     input_file=image,
    #     output_file=skin,
    #     model_checkpoint=model_checkpoint)
    # # Lung
    # model_checkpoint = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/lung/imagewise/UNet/test_training_T1_batch16/best_accuracy-5"
    # predict_nii_with_model_tf1(
    #     input_file=image,
    #     output_file=lung,
    #     model_checkpoint=model_checkpoint)
    #
    # # Nipples extraction
    # extract_nipples(skin, nipple)

