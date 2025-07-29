import os

import tensorflow as tf
import numpy as np
import time
import math
import nibabel
import os
import json

from airflow import DAG
from airflow.operators.python import PythonOperator

import shutil
import pandas as pd
from xlrd import XLRDError

from sparc_me import Dataset, Subject, Sample

import breast_metadata
import morphic


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


def load_Nifti(path, filename):
    """
    Loads a volumetric Nifti file. It returns a volume with the file's data and its metadata.
    """
    proxy_data = nibabel.load(path + filename)
    # proxy_data.affine[0:3, -1] = 0
    data = proxy_data.get_fdata()

    return data, proxy_data


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


def save_prediction(prediction, meta, output_file):
    # meta.affine[0:3, -1] = 0
    save_data = nibabel.Nifti1Image(np.transpose(prediction, (1, 0, 2)), meta.affine, meta.header)
    if (not os.path.exists(os.path.dirname(output_file))):
        os.mkdir(os.path.dirname(output_file))

    nibabel.save(save_data, output_file)


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


def get_sample_metadata(metadata_file):
    try:
        metadata = pd.read_excel(metadata_file)
    except XLRDError:
        metadata = pd.read_excel(metadata_file, engine='openpyxl')

    return metadata


def exec(**kwargs):
    try:
        sample_uuid = kwargs['dag_run'].conf.get('sample_uuid', kwargs['params'].get('sample_uuid'))
    except:
        sample_uuid = kwargs["sample_uuid"]

    try:
        # Pull variables from previous step using XCom
        nifti_file = kwargs["ti"].xcom_pull(key='nifti_file', task_ids="create_nifti")
        # nifti_file = kwargs["ti"].xcom_pull(key='nifti_file', task_ids="create_nifti_" + sample_uuid)
    except:
        nifti_file = kwargs["nifti_file"]

    try:
        workspace = kwargs['dag_run'].conf.get('workspace', kwargs['params'].get('workspace'))
        workspace_seg = os.path.join(workspace, "seg")
    except:
        workspace_seg = kwargs['workspace']
    os.makedirs(workspace_seg, exist_ok=True)

    try:
        body_model = kwargs['dag_run'].conf.get('body_model', kwargs['params'].get('body_model'))
    except:
        body_model = kwargs["body_model"]
    try:
        lung_model = kwargs['dag_run'].conf.get('lung_model', kwargs['params'].get('lung_model'))
    except:
        lung_model = kwargs["lung_model"]

    body_file = os.path.join(workspace_seg, "body.nii.gz")
    lungs_file = os.path.join(workspace_seg, "lungs.nii.gz")
    nipples_file = os.path.join(workspace_seg, "nipple_points")

    predict_nii_with_model_tf1(
        input_file=nifti_file,
        output_file=body_file,
        model_checkpoint=body_model)
    predict_nii_with_model_tf1(
        input_file=nifti_file,
        output_file=lungs_file,
        model_checkpoint=lung_model)
    # extract_nipples(body_file, nipples_file)


def get_task(dag: DAG):
    # sample_uuid = dag.params.get("sample_uuid")
    # task_id = "segment_" + str(sample_uuid)
    task_id = "segment"
    return PythonOperator(
        task_id=task_id,
        python_callable=exec,
        provide_context=True,
        dag=dag
    )


if __name__ == '__main__':
    sample_uuid = "sam-001001"
    nifti_file = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/airflow/single_input/out/sam-001001/nifti/sam-001001.nii.gz"
    workspace = "/home/clin864/opt/digitaltwins-api/my_workspace/ep4/airflow/single_input/out/sam-001001/seg"

    body_model = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/body/imagewise/UNet/test_training_t1_batch16/best_accuracy-8"
    lung_model = "/home/clin864/eresearch/Vault/Segmentations/models/resources/volunteers/lung/imagewise/UNet/test_training_T1_batch16/best_accuracy-5"

    exec(sample_uuid=sample_uuid, nifti_file=nifti_file, workspace=workspace, body_model=body_model, lung_model=lung_model)
