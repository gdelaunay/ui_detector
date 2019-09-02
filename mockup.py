

class Mockup:

    def __init__(self, original_image, detection_results, elements=None):
        self.original_image = original_image
        self.boxes, self.classes, self.scores = detection_results
        self.elements = elements

    def translate(self):

        pass

    def create_xml(self):

        pass

