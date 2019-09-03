

class Mockup:

    def __init__(self, original_image, detection_results, elements=None, xml_page=None, generated_id=None):
        self.original_image = original_image
        self.boxes, self.classes, self.scores = detection_results
        self.elements = elements
        self.xml_page = xml_page
        self.generated_id = generated_id

    def translate_raw_results(self):

        pass

    def create_xml_page(self):

        height, width = self.original_image.shape[1::-1]
        page_title = 'Page Title'

        xml_header = ' <p:Page xmlns:p="http://www.evolus.vn/Namespace/Pencil"> \n ' \
                     ' <p:Properties> \n ' \
                     ' <p:Property name="id">' + self.generated_id + '</p:Property> \n ' \
                     ' <p:Property name="name">' + page_title + '</p:Property> \n ' \
                     ' <p:Property name="width">' + width + '</p:Property> \n ' \
                     ' <p:Property name="height">' + height + '</p:Property> \n ' \
                     ' <p:Property name="pageFileName">page_' + self.generated_id + '.xml</p:Property> \n ' \
                     ' </p:Properties> \n '

        xml_content = ' <p:Content> \n '
        for element in self.elements:
            xml_content += element.xml_element
        xml_content += ' </p:Content> \n '

        self.xml_page = xml_header + xml_content + ' </p:Page> '

    def generate_pencil_file(self):

        pass
