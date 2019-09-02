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

    def ocr_text_value(self, image):
        pass



