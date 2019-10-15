from mockup import Mockup
import elements
import cv2
from matplotlib import pyplot as plt
from base64 import b64encode
import numpy as np
import ocr
from PIL import Image
from prediction import detection
from elements import TextElement
from skimage.color import rgb2lab, deltaE_cie76
from colormap.colors import hex2rgb, rgb2hsv
from image_utils import find_text_nb_of_lines


IMAGE_PATH = "testing_data/image017.jpg"


image = cv2.imread(IMAGE_PATH)

original_image = image.copy()
detection_results = detection(image)

mockup = Mockup("xero", original_image, detection_results)
mockup.translate_raw_results()
# mockup.align_text_elements()
# mockup.create_svg("C:/projet/ui_detector_git/output")
mockup.create_bmml("./export_balsamiq")
# mockup.create_xml_page()
# mockup.generate_pencil_file()
