from base64 import b64encode
from abc import ABC, abstractmethod


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


class Image(Element):

    def __init__(self, coordinates, image=None, b64=None):
        super().__init__(coordinates)
        self.image = image
        self.b64 = b64

    def redact_xml(self):

        generated_id = "id"
        width = self.xmax - self.xmin
        height = self.ymax - self.ymin

        self.xml_element = \
            ' <g xmlns="http://www.w3.org/2000/svg" p:type="Shape" p:def="Evolus.Common:Bitmap" id="' + generated_id + \
            '" transform="matrix(1,0,0,1,' + self.xmin + ',' + self.ymin + ')"> \n ' \
            ' <p:metadata> \n ' \
            ' <p:property name="box"><![CDATA[' + width + ',' + height + ']]></p:property> \n ' + \
            ' <p:property name="imageData"><![CDATA[' + width + ',' + height + ',' + self.b64 + ']]></p:property> \n ' \
            ' </p:metadata> \n ' \
            ' </g>'

    def extract_image(self, original_image):

        cropped_image = original_image[self.ymin:self.ymax, self.xmin:self.xmax]

        # TODO : Remove borders from cropped_image, compute new coordinates

        self.image = cropped_image

    def set_base64(self):
        self.b64 = b64encode(self.image)


class Icon(Element):

    def __init__(self, coordinates, ptype=None):
        super().__init__(coordinates)
        self.ptype = ptype

    def redact_xml(self):
        pass

