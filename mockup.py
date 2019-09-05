from zipfile import ZipFile
from shortuuid import ShortUUID
from elements import TextElement, ImageElement, Icon
from constants import text_types, icon_types
import os


class Mockup:

    def __init__(self, title, original_image, detection_results, elements=None, xml_page=None):
        self.title = title
        self.original_image = original_image
        self.boxes, self.classes, self.scores = detection_results
        self.elements = elements if elements else []
        self.xml_page = xml_page if xml_page else ""
        self.generated_id = ShortUUID().random(length=8)

    def translate_raw_results(self):

        classes = ["text", "text_input", "image", "rectangle_button", "oval_button", "search", "login", "lock", "chat",
                   "phone", "checkbox", "home", "help", "down_arrow", "right_arrow", "menu", "plus", "mail", "settings"]

        for i, box in enumerate(self.boxes):

            box_class = classes[self.classes[i] - 1]

            if box_class in text_types:
                element = TextElement(box, box_class)
                element.compute_text_size_and_value(self.original_image)
            if box_class in icon_types:
                element = Icon(box, box_class)
            else:
                element = ImageElement(box)
                element.extract_image(self.original_image)
                element.set_base64()

            element.redact_xml()

            self.elements.append(element)

    def create_xml_page(self):

        height, width = self.original_image.shape[1::-1]

        xml_header = ' <p:Page xmlns:p="http://www.evolus.vn/Namespace/Pencil"> \n ' \
                     ' <p:Properties> \n ' \
                     ' <p:Property name="id">' + self.generated_id + '</p:Property> \n ' \
                     ' <p:Property name="name">' + self.title + '</p:Property> \n ' \
                     ' <p:Property name="width">' + str(width) + '</p:Property> \n ' \
                     ' <p:Property name="height">' + str(height) + '</p:Property> \n ' \
                     ' <p:Property name="pageFileName">page_' + self.generated_id + '.xml</p:Property> \n ' \
                     ' </p:Properties> \n '

        xml_content = ' <p:Content> \n '
        for element in self.elements:
            xml_content += element.xml_element
        xml_content += ' </p:Content> \n '

        self.xml_page = xml_header + xml_content + ' </p:Page> '

    def generate_pencil_file(self):

        path = "output/"
        page_file = open("page_" + self.generated_id + ".xml", "w+")
        page_file.write(self.xml_page)
        page_file.close()

        content_file_xml = \
            ' <Document xmlns="http://www.evolus.vn/Namespace/Pencil"> \n ' \
            ' <Properties> \n <Property name="activeId">' + self.generated_id + '</Property> \n </Properties> \n ' \
            ' <Pages> \n <Page href="page_' + self.generated_id + '.xml"/> \n </Pages> \n' \
            ' </Document> \n'
        content_file = open("content.xml", "w+")
        content_file.write(content_file_xml)
        content_file.close()

        filename = self.title.strip()

        with ZipFile(path + filename + '.epz', 'w') as pencil_archive:
            pencil_archive.write('content.xml')
            pencil_archive.write('page_' + self.generated_id + '.xml')

        os.rename("content.xml", path + "content.xml")
        os.rename("page_" + self.generated_id + ".xml", path + "page_" + self.generated_id + ".xml")