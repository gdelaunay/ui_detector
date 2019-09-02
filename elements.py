from abc import ABC, abstractmethod


class Element(ABC):

    def __init__(self, coordinates):
        self.ymin = coordinates[0]
        self.xmin = coordinates[1]
        self.ymax = coordinates[2]
        self.xmax = coordinates[3]

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

    def __init__(self, coordinates, image=None, base64=None):
        super().__init__(coordinates)
        self.image = image
        self.base64 = base64

    def redact_xml(self):
        pass

    def extract_image(self, original_image):
        pass

    def set_base64(self):
        pass


class Icon(Element):

    def __init__(self, coordinates, ptype=None):
        super().__init__(coordinates)
        self.ptype = ptype

    def redact_xml(self):
        pass

