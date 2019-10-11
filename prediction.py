import numpy as np
import os
import tensorflow as tf
import cv2

from object_detection.utils import label_map_util
from object_detection.utils import visualization_utils as vis_util

IMAGE_PATH = "testing_data/test3.jpg"
MODEL_NAME = 'ui_detection_graph_3363.pb'

# Number of different classes to detect
NUM_CLASSES = 19

# Minimum confidence score under wich we don't show/save predictions
MIN_SCORE_TRESH = .4


def detection(image):

    # Path to frozen detection graph. This is the actual model that is used for the object detection.
    path_to_ckpt = 'trained_graphs\\' + MODEL_NAME + '\\frozen_inference_graph.pb'
    # Path to labelmap = List of the strings that is used to add correct label for each box.
    path_to_labels = os.path.join('dataset\\annotations', 'label_map.pbtxt')

    # Load a (frozen) Tensorflow model into memory.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(path_to_ckpt, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')

    # Loading label map
    label_map = label_map_util.load_labelmap(path_to_labels)
    categories = label_map_util.convert_label_map_to_categories(
        label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)

    # Detection
    with detection_graph.as_default():
        with tf.Session(graph=detection_graph) as sess:

            # Expand dimensions since the model expects images to have shape: [1, None, None, 3]
            image_np_expanded = np.expand_dims(image, axis=0)

            # Extracting tensors (tensorflow variables)
            image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
            boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
            scores = detection_graph.get_tensor_by_name('detection_scores:0')
            classes = detection_graph.get_tensor_by_name('detection_classes:0')
            num_detections = detection_graph.get_tensor_by_name(
                'num_detections:0')

            # Run variable through tf.session with our detection graph = actual detection
            (boxes, scores, classes, num_detections) = sess.run(
                [boxes, scores, classes, num_detections],
                feed_dict={image_tensor: image_np_expanded})

            selected_boxes, selected_classes, selected_scores = delete_overlapping_boxes(sess,
                                                                                         np.squeeze(boxes),
                                                                                         np.squeeze(classes),
                                                                                         np.squeeze(scores))
            # np.squeeze(boxes), np.squeeze(classes), np.squeeze(scores)
            # delete_overlapping_boxes(sess, np.squeeze(boxes), np.squeeze(classes), np.squeeze(scores))
            # delete_overlapping_boxes_by_class(sess, boxes, classes, scores)

            # Visualization of the results
            vis_util.visualize_boxes_and_labels_on_image_array(
                image,
                selected_boxes,
                selected_classes.astype(np.int32),
                selected_scores,
                category_index,
                use_normalized_coordinates=True,
                line_thickness=5,
                min_score_thresh=MIN_SCORE_TRESH,
                max_boxes_to_draw=1000)

            # display_output(image)
            cv2.imwrite("output/" + MODEL_NAME + ".jpg", image)
            normalized_boxes = get_pixelwise_boxes_coordinates(image, selected_boxes)

    return normalized_boxes, selected_classes, selected_scores


def display_output(image):
    """ Display an image (keeping proportions), press any key to exit """

    h, w = image.shape[:2]
    nh = int(1200 / w * h)

    cv2.imshow('object detection', cv2.resize(image, (1200, nh)))
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def delete_overlapping_boxes_by_class(sess, boxes, classes, scores):
    """ params: tf.session, raw object detection result and index of a class we want to select
        returns: new arrays of boxes, classes and scores with boxes of the same class overlapping removed """

    new_boxes, new_classes, new_scores = [], [], []

    for i in range(1, NUM_CLASSES + 1):
        selected_boxes, selected_classes, selected_scores = class_selection(sess, boxes, classes, scores, i)
        if selected_boxes.shape[0] > 1:
            selected_boxes, selected_classes, selected_scores = delete_overlapping_boxes(sess, selected_boxes,
                                                                                         selected_classes,
                                                                                         selected_scores)
        for b in selected_boxes:
            new_boxes.append(b)
        new_classes = np.hstack((new_classes, selected_classes))
        new_scores = np.hstack((new_scores, selected_scores))

    return np.array(new_boxes), new_classes, new_scores


def delete_overlapping_boxes(sess, boxes, classes, scores):
    """ params: tf.session and "squeezed" object detection result
        returns: new arrays of boxes, classes and scores with boxes overlapping (depending on treshold) removed """

    max_output_size = 1000
    overlapping_treshold = .1

    selected_indices = tf.image.non_max_suppression(
        boxes,
        scores,
        max_output_size,
        iou_threshold=overlapping_treshold,
        score_threshold=MIN_SCORE_TRESH,
        name=None
    )

    selected_indices = sess.run(selected_indices)
    selected_boxes = np.array(sess.run(tf.gather(np.squeeze(boxes), selected_indices)))
    selected_classes = np.array(sess.run(tf.gather(classes, selected_indices)))
    selected_scores = np.array(sess.run(tf.gather(np.squeeze(scores), selected_indices)))

    return selected_boxes, selected_classes, selected_scores


def class_selection(sess, boxes, classes, scores, class_index):
    """ params: tf.session, raw object detection result and index of a class we want to select
        returns: new arrays of boxes, classes and scores with only the results corresponding to the class we chose """

    classes = np.squeeze(classes)
    new_classes = []
    indices = []

    for i, item in enumerate(classes):
        if item == class_index:
            new_classes.append(item.astype(np.int32))
            indices.append(i)

    new_boxes = tf.gather(np.squeeze(boxes), np.array(indices).astype(np.int64))
    new_scores = tf.gather(np.squeeze(scores), np.array(indices).astype(np.int64))
    new_boxes, new_scores = sess.run([new_boxes, new_scores])

    return np.array(new_boxes), np.array(new_classes), np.array(new_scores)


def get_pixelwise_boxes_coordinates(image, boxes):
    """ params: original image and already processed (through overlapping removal = already squeezed) boxes and scores
        returns: an array of boxes, each box being an array containing their pixelwise (detection output coordinates are
                normalized) position and score """

    # Getting image dimensions (box coordinates are normalized, we have to multiply them by the image size)
    im_height, im_width = image.shape[:2]

    boxes_coordinates = []
    for i, box in enumerate(boxes):
        box[0] = box[0] * im_height
        box[1] = box[1] * im_width
        box[2] = box[2] * im_height
        box[3] = box[3] * im_width
        boxes_coordinates.append(box)

    return np.array(boxes_coordinates)
