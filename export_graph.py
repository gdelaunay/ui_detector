import tensorflow as tf
from google.protobuf import text_format
from object_detection import exporter
from object_detection.protos import pipeline_pb2

PIPELINE_CONFIG_PATH = "training/faster_rcnn_resnet50_coco.config"
CHECKPOINT_PATH = "training/model.ckpt-483"
OUTPUT_DIR = "trained_graphs/ui_detection_graph_483.pb"


def main(_):
    pipeline_config = pipeline_pb2.TrainEvalPipelineConfig()
    with tf.gfile.GFile(PIPELINE_CONFIG_PATH, 'r') as f:
        text_format.Merge(f.read(), pipeline_config)

    input_shape = None
    exporter.export_inference_graph(
        'image_tensor', pipeline_config, CHECKPOINT_PATH,
        OUTPUT_DIR, input_shape=input_shape,
        write_inference_graph=False)


if __name__ == '__main__':
    tf.app.run()
