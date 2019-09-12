#! venv/ python3
# coding: utf-8

import cv2
import image_utils as iu
from base64 import b64encode
from abc import ABC, abstractmethod
from PIL import Image
from shortuuid import ShortUUID
from constants import icon_types, b64_icons, text_types, t_firsts_tags, t_properties
from ocr import ocr, padding


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
        stroke_style = "2" if len(self.color[0]) == 2 else "0"

        if self.ptype is "text":
            property_value = self.text_value
            text_color = border_color = self.color
        else:
            property_value = size
            text_color = self.color[1]
            if len(self.color[0]) == 2:
                border_color = self.color[0][1]
                self.color = self.color[0][0]
            else:
                border_color = text_color
                self.color = self.color[0]

        self.xml_element = \
            first_tag + generated_id + '" transform="matrix(1,0,0,1,' + first_point + ')"> \n <p:metadata> \n ' + \
            properties_tag[0] + property_value + ']]></p:property> \n' \
            '<p:property name="fillColor"><![CDATA[' + self.color + ']]></p:property> \n' \
            '<p:property name="textColor"><![CDATA[' + text_color + ']]></p:property> \n' \
            '<p:property name="textContent"><![CDATA[' + self.text_value + ']]></p:property> \n' \
            '<p:property name="textFont"><![CDATA[Arial|normal|normal|' + self.text_size + 'px|none]]></p:property> \n'\
            '<p:property name="strokeStyle"><![CDATA[' + stroke_style + '|]]></p:property> \n' \
            '<p:property name="strokeColor"><![CDATA[' + border_color + ']]></p:property> \n' \
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
            padding_color = iu.find_background_color(cropped_text)
            cropped_text = iu.remove_image_borders(cropped_text)
            cropped_text = padding(cropped_text, int(cropped_text.shape[0]/5), padding_color)

            text_height = 0.8 * cropped_text.shape[0]
            self.color = iu.find_text_color(cropped_text)
        else:
            background_bgr = iu.find_background_color(cropped_text)
            background_hex = iu.bgr2hex(background_bgr)

            x = int(cropped_text.shape[0] / 4)
            cropped_text = cropped_text[x:- x, x:- x]
            text_height = 0.6 * cropped_text.shape[0]

            pil_image = Image.fromarray(cropped_text)
            button_bgr = pil_image.getpixel((0, int(cropped_text.shape[0]/2)))
            button_hex = iu.bgr2hex(button_bgr)
            background_hex, button_hex = iu.liken_colors(background_hex, button_hex, .15)

            text_color = iu.find_text_color(cropped_text)
            button_hex, text_color = iu.differentiate_colors(button_hex, text_color, .1)

            if button_hex == background_hex:
                border_color = text_color
                button_color = [button_hex, border_color]
            else:
                button_color = button_hex

            self.color = [button_color, text_color]

        nb_of_lines = iu.find_text_nb_of_lines(cropped_text)

        self.text_size = str(int(text_height / nb_of_lines))

        self.text_value = ocr(cropped_text)


class ImageElement(Element):

    def __init__(self, coordinates, image=None, b64=None):
        super().__init__(coordinates)
        self.image = image
        self.b64 = b64

    def redact_xml(self, **background):

        generated_id, first_point, size = get_element_properties(self)

        self.xml_element = \
            ' <g xmlns="http://www.w3.org/2000/svg" p:type="Shape" p:def="Evolus.Common:Bitmap" id="' + generated_id + \
            '" transform="matrix(1,0,0,1,' + first_point

        if background:
            self.xml_element += ')" ' + 'p:locked="true"> \n '
        else:
            self.xml_element += ')"> \n '

        self.xml_element += ' <p:metadata> \n ' \
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

        borderless_image = iu.remove_image_borders(cropped_image)

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


