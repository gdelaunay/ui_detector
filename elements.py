from base64 import b64encode
from abc import ABC, abstractmethod
from PIL import Image, ImageChops
from shortuuid import ShortUUID
from constants import icon_types, b64_icons, text_types, t_firsts_tags, t_properties
import cv2
import numpy


class Element(ABC):

    def __init__(self, coordinates, xml_element=None):
        self.ymin = coordinates[0]
        self.xmin = coordinates[1]
        self.ymax = coordinates[2]
        self.xmax = coordinates[3]
        self.xml_element = xml_element

    @abstractmethod
    def redact_xml(self):
        pass


class TextElement(Element):

    def __init__(self, coordinates, ptype, text_size=None, text_value=None):
        super().__init__(coordinates)
        self.ptype = ptype
        self.text_size = text_size
        self.text_value = text_value

    def redact_xml(self):

        generated_id, first_point, size = get_element_properties(self)

        first_tag = t_firsts_tags[text_types.index(self.ptype)]
        properties_tag = t_properties[text_types.index(self.ptype)]
        property_value = self.text_value if self.ptype is "text" else size

        self.xml_element = \
            first_tag + generated_id + '" transform="matrix(1,0,0,1,' + first_point + ')"> \n <p:metadata> \n ' + \
            properties_tag + property_value + ']]></p:property> \n' \
            '<p:property name="textContent"><![CDATA[' + self.text_value + ']]></p:property> \n' \
            '<p:property name="textFont"><![CDATA[Arial|normal|normal|' + self.text_size + 'px|none]]></p:property> \n'\
            '</p:metadata> \n <text p:name="text"></text> \n </g> \n'

    def compute_text_size(self, original_image):

        cropped_text = original_image[self.ymin:self.ymax, self.xmin:self.xmax]
        borderless_text = remove_image_borders(cropped_text)

        height = borderless_text.shape[0]

        if self.ptype is not "text":
            height *= .45

        self.text_size = str(int(4.1 * height))

    def ocr_text_value(self, original_image):
        pass


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

        cropped_image = original_image[self.ymin:self.ymax, self.xmin:self.xmax]

        borderless_image = remove_image_borders(cropped_image)

        self.image = borderless_image

    def set_base64(self):
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

    generated_id = ShortUUID().random(length=12)
    first_point = str(int(element.xmin)) + "," + str(int(element.ymin))
    width = int(element.xmax - element.xmin)
    height = int(element.ymax - element.ymin)
    size = str(width) + "," + str(height)

    return generated_id, first_point, size


def remove_image_borders(image):

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    bg = Image.new(pil_image.mode, pil_image.size, pil_image.getpixel((0, 0)))
    diff = ImageChops.difference(pil_image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        pil_image = pil_image.crop(bbox)

    cv2_image = cv2.cvtColor(numpy.array(pil_image), cv2.COLOR_RGB2BGR)

    return cv2_image

