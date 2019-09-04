from base64 import b64encode
from abc import ABC, abstractmethod
from PIL import Image, ImageChops
from shortuuid import ShortUUID
from constants import icon_types, b64_icons
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
        pass

    def compute_text_size(self):
        pass

    def ocr_text_value(self, original_image):
        pass


class ImageElement(Element):

    def __init__(self, coordinates, image=None, b64=None):
        super().__init__(coordinates)
        self.image = image
        self.b64 = b64

    def redact_xml(self):

        generated_id = ShortUUID().random(length=12)
        first_point = str(int(self.xmin)) + "," + str(int(self.ymin))
        width = int(self.xmax - self.xmin)
        height = int(self.ymax - self.ymin)
        size = str(width) + "," + str(height)

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

    def __init__(self, coordinates, ptype=None):
        super().__init__(coordinates)
        self.ptype = ptype

    def redact_xml(self):

        generated_id = ShortUUID().random(length=12)
        first_point = str(int(self.xmin)) + "," + str(int(self.ymin))
        width = int(self.xmax - self.xmin)
        height = int(self.ymax - self.ymin)
        size = str(width) + "," + str(height)

        base64 = b64_icons[icon_types.index(self.ptype)]

        self.xml_element = \
            ' <g xmlns="http://www.w3.org/2000/svg" p:type="Shape" p:def="Evolus.Common:Bitmap" id="' + generated_id + \
            '" transform="matrix(1,0,0,1,' + first_point + ')"> \n ' \
            ' <p:metadata> \n ' \
            ' <p:property name="box"><![CDATA[' + size + ']]></p:property> \n ' + \
            ' <p:property name="imageData"><![CDATA[' + size + ',' + base64 + ']]></p:property> \n ' \
            ' </p:metadata> \n ' \
            ' </g> \n '


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

