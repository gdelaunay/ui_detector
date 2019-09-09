from zipfile import ZipFile
from shortuuid import ShortUUID
from elements import TextElement, ImageElement, Icon
from constants import text_types, icon_types
from skimage.color import rgb2lab, deltaE_cie76
from colormap.colors import hex2rgb
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

            box_class = classes[int(self.classes[i] - 1)]

            if box_class in text_types:
                element = TextElement(box, box_class)
                element.compute_text_properties(self.original_image)
                if element.text_value.strip() == "":
                    continue

            if box_class in icon_types:
                element = Icon(box, box_class)

            if box_class is "image" or box_class is "checkbox":
                element = ImageElement(box)
                element.extract_image(self.original_image)
                element.set_base64()

            self.elements.append(element)

    def create_xml_page(self):

        height, width = self.original_image.shape[:2]

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
            element.redact_xml()
            xml_content += element.xml_element
        xml_content += ' </p:Content> \n '

        self.xml_page = xml_header + xml_content + ' </p:Page> '

    def generate_pencil_file(self):

        path = "output/mockup_" + self.title + "_" + self.generated_id + "/"
        os.makedirs(path)

        page_file = open("page_" + self.generated_id + ".xml", "wb")
        page_file.write(self.xml_page.encode("utf-8"))
        page_file.close()

        content_file_xml = \
            ' <Document xmlns="http://www.evolus.vn/Namespace/Pencil"> \n ' \
            ' <Properties> \n <Property name="activeId">' + self.generated_id + '</Property> \n </Properties> \n ' \
            ' <Pages> \n <Page href="page_' + self.generated_id + '.xml"/> \n </Pages> \n' \
            ' </Document> \n'
        content_file = open("content.xml", "wt")
        content_file.write(content_file_xml)
        content_file.close()

        filename = self.title.strip()

        with ZipFile(path + filename + '.epz', 'w') as pencil_archive:
            pencil_archive.write('content.xml')
            pencil_archive.write('page_' + self.generated_id + '.xml')

        os.rename("content.xml", path + "content.xml")
        os.rename("page_" + self.generated_id + ".xml", path + "page_" + self.generated_id + ".xml")

    def align_text_elements(self):

        for el in (x for x in self.elements if isinstance(x, TextElement)):
            for next_el in (x for x in self.elements if isinstance(x, TextElement)):
                if el.ptype == next_el.ptype:
                    h = (el.ymax - el.ymin) * .5

                    if el.ymin - h < next_el.ymin < el.ymin + h:
                        next_el.ymin = el.ymin

                        if (next_el.xmin - el.xmax < 100) & \
                                (.5 * int(el.text_size) < int(next_el.text_size) < 2 * int(el.text_size)):
                            next_el.text_size = el.text_size

                        el.color, next_el.color = compare_colors(el.color, next_el.color)

                    if el.xmin - h < next_el.xmin < el.xmin + h:
                        next_el.xmin = el.xmin


def compare_colors(c1, c2):

    c1s, c2s = (c1[1], c2[1]) if len(c1) == 2 else (c1, c2)

    r1, g1, b1 = hex2rgb(c1s, normalise=False)
    lab1 = rgb2lab([[[r1, g1, b1]]])
    r2, g2, b2 = hex2rgb(c2s, normalise=False)
    lab2 = rgb2lab([[[r2, g2, b2]]])
    diff = (deltaE_cie76(lab1, lab2) * 1e5)[0][0]

    return (c1, c1) if diff < .5 else (c1, c2)
