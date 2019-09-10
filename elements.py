#! venv/ python3
# coding: utf-8

import cv2
import numpy as np
from base64 import b64encode
from abc import ABC, abstractmethod
from PIL import Image, ImageChops
from shortuuid import ShortUUID
from constants import icon_types, b64_icons, text_types, t_firsts_tags, t_properties
from ocr import ocr, padding, preprocessing


class Element(ABC):

    def __init__(self, coordinates, xml_element=None):
        self.ymin = int(coordinates[0])
        self.xmin = int(coordinates[1])
        self.ymax = int(coordinates[2])
        self.xmax = int(coordinates[3])
        self.xml_element = xml_element

    @abstractmethod
    def redact_xml(self):
        """ translate the Element object into xml pencil format """
        pass


class TextElement(Element):

    def __init__(self, coordinates, ptype, text_size=None, text_value=None, color=None):
        super().__init__(coordinates)
        self.ptype = ptype
        self.text_size = text_size
        self.text_value = text_value
        self.color = color

    def redact_xml(self):

        generated_id, first_point, size = get_element_properties(self)

        type_index = text_types.index(self.ptype)
        first_tag = t_firsts_tags[type_index]
        properties_tag = t_properties[type_index]

        if self.ptype is "text":
            property_value = self.text_value
            text_color = self.color
        else:
            property_value = size
            text_color = self.color[1]
            self.color = self.color[0]

        stroke_style = "1" if self.ptype is "text_input" else "0"

        self.xml_element = \
            first_tag + generated_id + '" transform="matrix(1,0,0,1,' + first_point + ')"> \n <p:metadata> \n ' + \
            properties_tag[0] + property_value + ']]></p:property> \n' \
            '<p:property name="fillColor"><![CDATA[' + self.color + ']]></p:property> \n' \
            '<p:property name="textColor"><![CDATA[' + text_color + ']]></p:property> \n' \
            '<p:property name="textContent"><![CDATA[' + self.text_value + ']]></p:property> \n' \
            '<p:property name="textFont"><![CDATA[Arial|normal|normal|' + self.text_size + 'px|none]]></p:property> \n'\
            '<p:property name="strokeStyle"><![CDATA[' + stroke_style + '|]]></p:property> \n' \
            '</p:metadata> \n <text p:name="text"></text> \n </g> \n'

    def compute_text_properties(self, original_image):
        """
        crop the element from the original image, remove its border, calculate its size according to its type, OCR
        its value, find text color and button color
        :param original_image: original screenshot of the web UI
        :set: text_size in pixels and text_value in string format
        """

        cropped_text = original_image[self.ymin:self.ymax, self.xmin:self.xmax]

        if self.ptype is "text":
            pil_image = Image.fromarray(cropped_text)
            padding_color = pil_image.getpixel((0, 0))
            cropped_text = remove_image_borders(cropped_text)
            cropped_text = padding(cropped_text, int(cropped_text.shape[0]/5), padding_color)
            text_height = 0.8 * cropped_text.shape[0]
            self.color = find_text_color(cropped_text)
        else:
            x = int(cropped_text.shape[0]/4)
            cropped_text = cropped_text[x:-x, x:-x]
            text_height = 0.55 * cropped_text.shape[0]
            pil_image = Image.fromarray(cropped_text)
            bgr = pil_image.getpixel((8, int(cropped_text.shape[0]/2)))
            button_color = bgr_to_hex(bgr)
            text_color = find_text_color(cropped_text)
            self.color = [button_color, text_color]

        nb_of_lines = find_text_nb_of_lines(cropped_text)

        self.text_size = str(int(text_height / nb_of_lines))

        self.text_value = ocr(cropped_text)


class ImageElement(Element):

    def __init__(self, coordinates, image=None, b64=None):
        super().__init__(coordinates)
        self.image = image
        self.b64 = b64

    def redact_xml(self):

        generated_id, first_point, size = get_element_properties(self)

        self.xml_element = \
            ' <g xmlns="http://www.w3.org/2000/svg" p:type="Shape" p:def="Evolus.Common:Bitmap" id="' + generated_id + \
            '" transform="matrix(1,0,0,1,' + first_point + ')"> \n ' \
            ' <p:metadata> \n ' \
            ' <p:property name="box"><![CDATA[' + size + ']]></p:property> \n ' + \
            ' <p:property name="imageData"><![CDATA[' + size + ',' + self.b64 + ']]></p:property> \n ' \
            ' </p:metadata> \n ' \
            ' </g> \n '

    def extract_image(self, original_image):
        """
        :param original_image: original screenshot of the web UI
        :set: image element cropped from the original image
        """

        cropped_image = original_image[self.ymin:self.ymax, self.xmin:self.xmax]

        borderless_image = remove_image_borders(cropped_image)

        self.image = borderless_image

    def set_base64(self):
        """
        convert an numpy array image to a base64 string
        :set: b64 string image
        """
        _, encoded_image = cv2.imencode('.png', self.image)
        self.b64 = "data:image/png;base64," + b64encode(encoded_image).decode('ascii')


class Icon(Element):

    def __init__(self, coordinates, ptype):
        super().__init__(coordinates)
        self.ptype = ptype

    def redact_xml(self):

        generated_id, first_point, size = get_element_properties(self)

        base64 = b64_icons[icon_types.index(self.ptype)]

        self.xml_element = \
            ' <g xmlns="http://www.w3.org/2000/svg" p:type="Shape" p:def="Evolus.Common:Bitmap" id="' + generated_id + \
            '" transform="matrix(1,0,0,1,' + first_point + ')"> \n ' \
            ' <p:metadata> \n ' \
            ' <p:property name="box"><![CDATA[' + size + ']]></p:property> \n ' + \
            ' <p:property name="imageData"><![CDATA[' + size + ',' + base64 + ']]></p:property> \n ' \
            ' </p:metadata> \n ' \
            ' </g> \n '


def get_element_properties(element):
    """
    compute an element's properties needed to write it in xml file
    :param element: any Element object
    :return: its uuid, first (xmin, ymin) point, and its size "width, height" in string format
    """

    generated_id = ShortUUID().random(length=12)
    first_point = str(int(element.xmin)) + "," + str(int(element.ymin))
    width = int(element.xmax - element.xmin)
    height = int(element.ymax - element.ymin)
    size = str(width) + "," + str(height)

    return generated_id, first_point, size


def remove_image_borders(image):
    """
    find if an image has border (from approximate object detections result) by looking at first pixel color, and if so
    remove them
    :param image: any
    :return: same image without borders (if it had any)
    """

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    bg = Image.new(pil_image.mode, pil_image.size, pil_image.getpixel((0, 0)))
    diff = ImageChops.difference(pil_image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        pil_image = pil_image.crop(bbox)

    cv2_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    return cv2_image


def find_text_nb_of_lines(text_image):
    """
    :param text_image: any BGR image of text (aligned = not rotated)
    :return: number of lines found in text_image
    """

    binary = 255 - preprocessing(text_image)

    hist = cv2.reduce(binary, 1, cv2.REDUCE_AVG).reshape(-1)

    h = text_image.shape[0]

    lines = [y for y in range(h - 1) if hist[y + 1] <= 2 < hist[y]]

    return len(lines) if len(lines) > 0 else 1


def find_text_color(cropped_text):
    """
    compute text color by converting image to binary (OTSU treshold), take first black pixel (= first
    and find its color value in the original text image
    :param cropped_text: numpy image of a text element already cropped
    :return: text color in hex string format
    """

    binary = preprocessing(cropped_text)
    black_pixels = np.argwhere(binary == 0)

    try:
        bgr = cropped_text[black_pixels[1][0]][black_pixels[1][1]]
    except IndexError:
        bgr = cropped_text[black_pixels[0][0]][black_pixels[0][1]]

    return bgr_to_hex(bgr)


def bgr_to_hex(bgr):
    """
    :param bgr: bgr color in the form of an array [.., .., ..]
    :return: hex color in string format
    """
    return '#%02x%02x%02x' % (bgr[2], bgr[1], bgr[0])