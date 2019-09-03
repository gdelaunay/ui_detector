

class Mockup:

    def __init__(self, original_image, detection_results, elements=None, xml_page=None):
        self.original_image = original_image
        self.boxes, self.classes, self.scores = detection_results
        self.elements = elements
        self.xml_page = xml_page

    def translate_raw_results(self):

        pass

    def create_xml_page(self):

        pass

    def generate_pencil_file(self):

        pass
