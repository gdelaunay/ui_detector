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
import numpy as np
from img2svg import Rectangle, Text, Image, ButtonRectangle, Scene, Tspan
import img2bmml

PATH_BALSAMIQ = './'


class Element(ABC):

    def __init__(self, coordinates, xml_element=None):
        self.ymin = int(coordinates[0])
        self.xmin = int(coordinates[1])
        self.ymax = int(coordinates[2])
        self.xmax = int(coordinates[3])

        self.xml_element = xml_element

        self.svg_item = None
        self.svg_id = None

        self.bmml_id = None
        self.bmml_item = None

    @abstractmethod
    def redact_xml(self):
        """ Translate the Element object into xml pencil format """
        pass

    @abstractmethod
    def create_svg_item(self):
        """
        Translate the Element object into sequence of SVG
        :return: SVG sequence
        """
        pass

    @abstractmethod
    def create_bmml_item(self):
        """
        Translate the Element object into sequence of bmml
        :return: bmml sequence
        """
        pass


class TextElement(Element):

    def __init__(self, coordinates, ptype, text_size=None, text_value=None, color=None, svg_item=None):
        super().__init__(coordinates)
        self.ptype = ptype
        self.text_size = text_size
        self.text_value = text_value
        self.color = color
        self.svg_item = svg_item
        self.text_dim = None
        self.button_dim = None

    def create_bmml_item(self):

        if self.ptype is "text":
            self.bmml_element = img2bmml.Text(self.bmml_id, self.xmin, self.ymin,
                                 self.text_value, self.xmax - self.xmin, self.ymax - self.ymin, self.text_size)

        else:
            self.bmml_element = img2bmml.Button(self.bmml_id, self.xmin, self.ymin, self.text_value, self.xmax - self.xmin,
                                                self.ymax - self.ymax)

        return self.bmml_element

    def create_svg_item(self):

        # SVG line break need Tspan Tag
        lst_tspan = self.text_value.split('\n')

        if self.ptype is "text":

            # If multi-lines
            if len(lst_tspan) > 1:

                text = Text((self.xmin, self.ymin), '', self.text_size, self.color, self.svg_id)

                id = 0

                for tspan in lst_tspan:
                    id += 1
                    text.add_tspan(Tspan(self.xmin, "1.2em", tspan, 'tspan' + self.svg_id + str(id)))

                self.svg_item = text

            else:
                self.svg_item = Text((self.xmin + self.text_dim[0], self.ymin), self.text_value,
                                     self.text_size, self.color, self.svg_id)

        # Button, etc
        else:

            if len(self.color[0]) == 2:
                border_color = self.color[0][1]
                color = self.color[0][0]
            else:
                border_color = self.color[1]
                color = self.color[0]

            width, height = get_width_height(self)

            shape = Rectangle((self.xmin, self.ymin), height, width, color, border_color, 1, "rect" + self.svg_id)

            text = Text((self.xmin + width / 2, self.ymin + height / 2), self.text_value, self.text_size,
                        border_color, "text" + self.svg_id, 'dominant-baseline="middle" text-anchor="middle"')

            self.svg_item = ButtonRectangle(shape, text, self.svg_id)

    def redact_xml(self):

        generated_id, first_point, size = get_element_properties(self)

        type_index = text_types.index(self.ptype)
        first_tag = t_firsts_tags[type_index]
        properties_tag = t_properties[type_index]
        stroke_style = "2" if len(self.color[0]) == 2 else "0"

        if self.ptype is "text":
            property_value = self.text_value
            color = text_color = border_color = self.color
        else:
            property_value = size
            text_color = self.color[1]
            if len(self.color[0]) == 2:
                border_color = self.color[0][1]
                color = self.color[0][0]
            else:
                border_color = text_color
                color = self.color[0]

        self.xml_element = \
            first_tag + generated_id + '" transform="matrix(1,0,0,1,' + first_point + ')"> \n <p:metadata> \n ' + \
            properties_tag[0] + property_value + ']]></p:property> \n' \
            '<p:property name="fillColor"><![CDATA[' + color + ']]></p:property> \n' \
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
            borderless = iu.remove_image_borders(cropped_text)
            text_height = borderless.shape[0]
            text_width = borderless.shape[1]

            self.color = iu.find_text_color(cropped_text)

            bbox, _ = iu.detect_border(cropped_text)

            if bbox:
                self.text_dim = (bbox[0], bbox[1], bbox[2], bbox[3])
            else:
                self.text_dim = (self.xmin, self.ymin, text_width, text_height)
        else:
            background_bgr = iu.find_background_color(cropped_text)
            background_hex = iu.bgr2hex(background_bgr)

            cropped_button, button_hex, self.ymin, self.ymax, self.xmin, self.xmax = iu.crop_button(cropped_text,
                                                                                                    background_bgr,
                                                                                                    (self.ymin,
                                                                                                     self.ymax,
                                                                                                     self.xmin,
                                                                                                     self.xmax))

            cropped_text, text_width, text_color, text_height, dim_text = iu.find_button_properties(cropped_button)

            button_hex, background_hex = iu.liken_colors(button_hex, background_hex, .15)

            self.text_dim = dim_text

            if button_hex == background_hex:
                border_color = text_color
                button_color = [button_hex, border_color]
            else:
                button_color = button_hex

            self.color = [button_color, text_color]

        self.text_value = ocr(cropped_text)

        nb_of_lines = iu.find_text_nb_of_lines(self.text_value)

        text_height = 0.75 * text_height if nb_of_lines > 1 else text_height

        self.button_dim = (self.xmax - self.xmin, self.ymax - self.ymax)
        self.text_size = str(int(text_height / nb_of_lines))


class ImageElement(Element):

    def __init__(self, coordinates, image=None, b64=None, svg_item=None):
        super().__init__(coordinates)
        self.image = image
        self.b64 = b64
        self.svg_item = svg_item
        self.ptype = 'Image'

    def create_bmml_item(self):
        width, height = get_width_height(self)
        image_name = str(self.bmml_id) + '.png'
        self.store_image(PATH_BALSAMIQ, image_name)
        self.bmml_element = img2bmml.Image(self.bmml_id, self.xmin, self.ymin, width, height, PATH_BALSAMIQ + image_name)

        return self.bmml_element

    def create_svg_item(self):

        width, height = get_width_height(self)

        self.svg_item = Image((self.xmin, self.ymin), self.b64, self.svg_id, height, width)

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

        border, _ = iu.detect_border(cropped_image)

        # self.xmin = self.xmin + border[0]
        # self.ymin = self.ymin + border[1]
        # self.xmax = self.xmin + border[2]
        # self.ymax = self.ymin + border[3]

        self.image = borderless_image

    def set_base64(self):
        """
        convert an numpy array image to a base64 string
        :set: b64 string image
        """
        _, encoded_image = cv2.imencode('.png', self.image)
        self.b64 = "data:image/png;base64," + b64encode(encoded_image).decode('ascii')

    def store_image(self, path, filename):
        """
        Store image on hard drive
        :param path:
        """

        cv2.imwrite(filename, self.image)


class Icon(Element):

    def __init__(self, coordinates, ptype, svg_item=None):
        super().__init__(coordinates)
        self.ptype = ptype
        self.svg_item = svg_item

    def create_svg_item(self):

        width, height = get_width_height(self)
        self.svg_item = Image((self.xmin, self.ymin), b64_icons[icon_types.index(self.ptype)], self.svg_id, height, width)

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


def get_width_height(element):
    """
    Get width and height of element in image
    :param element:
    :return:
    """
    width = int(element.xmax - element.xmin)
    height = int(element.ymax - element.ymin)
    return width, height


def get_element_properties(element):
    """
    Compute an element's properties needed to write it in xml file
    :param element: any Element object
    :return: its uuid, first (xmin, ymin) point, and its size "width, height" in string format
    """

    generated_id = ShortUUID().random(length=12)
    first_point = str(int(element.xmin)) + "," + str(int(element.ymin))
    width, height = get_width_height(element)
    size = str(width) + "," + str(height)

    return generated_id, first_point, size


