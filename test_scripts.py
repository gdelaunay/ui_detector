from mockup import Mockup
import elements
import cv2
from matplotlib import pyplot as plt
from base64 import b64encode

import numpy as np

from ocr import preprocessing
from image_utils import resizing
from PIL import Image
from prediction import detection
from elements import TextElement
from skimage.color import rgb2lab, deltaE_cie76
from colormap.colors import hex2rgb, rgb2hsv
import image_utils as iu

import numpy as np

import matplotlib
matplotlib.use('TkAgg')
IMAGE_PATH = "testing_data/docker.png"


image = cv2.imread(IMAGE_PATH)
original_image = image.copy()
detection_results = detection(image)

mockup = Mockup("sw", original_image, detection_results)
mockup.translate_raw_results()
mockup.align_text_elements()
mockup.create_xml_page()
mockup.generate_pencil_file()
