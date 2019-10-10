from elements import TextElement, ImageElement, Icon
from image_utils import liken_colors, get_main_color
from zipfile import ZipFile
from shortuuid import ShortUUID
from constants import text_types, icon_types
import img2svg
import collections
from PIL import Image
import numpy as np
import cv2
import os


class Mockup:

    def __init__(self, title, original_image, detection_results, elements=None, xml_page=None):
        self.title = title
        self.original_image = original_image
        self.background_image = original_image.copy()
        self.boxes, self.classes, self.scores = detection_results
        self.elements = elements if elements else []
        self.xml_page = xml_page if xml_page else ""
        self.generated_id = ShortUUID().random(length=8)
        self.current_id_svg = 0

    def translate_raw_results(self):
        """
        Translate TersonFlow predictions to Elements according to type (text, button, etc)
        """

        classes = ["text", "text_input", "image", "rectangle_button", "oval_button", "search", "login", "lock", "chat",
                   "phone", "checkbox", "home", "help", "down_arrow", "right_arrow", "menu", "plus", "mail", "settings"]

        for i, box in enumerate(self.boxes):

            self.current_id_svg += 1

            box_class = classes[int(self.classes[i] - 1)]

            if box_class in text_types:
                element = TextElement(box, box_class)
                element.compute_text_properties(self.original_image)
                if (element.text_value.strip() == "") & (element.ptype == "text"):
                    continue

            if box_class in icon_types:
                element = Icon(box, box_class)

            if box_class is "image" or box_class is "checkbox":
                element = ImageElement(box)
                element.extract_image(self.original_image)
                element.set_base64()

            self.extract_from_background(element)

            # Only for SVG export
            element.svg_id = element.ptype + str(self.current_id_svg)

            self.elements.append(element)

        self.elements.sort(key=lambda x: x.xmax)

    def create_svg(self, path):
        """
        Create the SVG with all SVG sequence (all elements)
        :param path: Path to write SVG
        :return: String : SVG Filename
        """

        height, width = self.original_image.shape[:2]

        svg = img2svg.Scene(self.current_id_svg, self.title, height, width)

        background_element = ImageElement([0, 0, height, width], self.background_image)
        background_element.set_base64()

        svg.add(img2svg.Image((0, 0), background_element.b64, "background" + str(self.current_id_svg), height, width))

        for element in self.elements:
            element.create_svg_item()
            svg.add(element.svg_item)

        return svg.write_svg(path)

    def create_xml_page(self):
        """
        Create XML page for pencil with all xml elements
        :return:
        """

        height, width = self.original_image.shape[:2]

        xml_header = ' <p:Page xmlns:p="http://www.evolus.vn/Namespace/Pencil"> \n ' \
                     ' <p:Properties> \n ' \
                     ' <p:Property name="id">' + self.generated_id + '</p:Property> \n ' \
                     ' <p:Property name="name">' + self.title + '</p:Property> \n ' \
                     ' <p:Property name="width">' + str(width) + '</p:Property> \n ' \
                     ' <p:Property name="height">' + str(height) + '</p:Property> \n ' \
                     ' <p:Property name="pageFileName">page_' + self.generated_id + '.xml</p:Property> \n ' \
                     ' </p:Properties> \n '

        background_element = ImageElement([0, 0, height, width], self.background_image)
        background_element.set_base64()
        background_element.redact_xml(backgroung=True)

        xml_content = ' <p:Content> \n '
        xml_content += background_element.xml_element

        for element in self.elements:
            if isinstance(element, ImageElement):
                element.redact_xml()
                xml_content += element.xml_element

        for element in self.elements:
            if not isinstance(element, ImageElement):
                element.redact_xml()
                xml_content += element.xml_element

        xml_content += ' </p:Content> \n '

        self.xml_page = xml_header + xml_content + ' </p:Page> '

    def generate_pencil_file(self):
        """
        Put in shape XML to be Pencil compatible and compact it with resources in Zip
        """

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
        """
        Align elements en y axis according to distance between each others
        """

        for el in (x for x in self.elements if isinstance(x, TextElement)):

            for next_el in (x for x in self.elements if isinstance(x, TextElement)):

                if el.ptype == next_el.ptype:

                    h = (el.ymax - el.ymin) * .25

                    if (abs(next_el.xmin - el.xmax) < 150) & \
                            (.7 * int(el.text_size) < int(next_el.text_size) < 1.3 * int(el.text_size)) & \
                            (el.ymin - h < next_el.ymin < el.ymin + h):

                        next_el.text_size = el.text_size
                        next_el.ymin = el.ymin
                        next_el.ymax = el.ymax
                        el.color, next_el.color = liken_colors(el.color, next_el.color, .35)

                    if el.xmin - h < next_el.xmin < el.xmin + h:

                        next_el.xmin = el.xmin

                        if .9 * int(el.text_size) < int(next_el.text_size) < 1.1 * int(el.text_size):
                            next_el.text_size = el.text_size

    def extract_from_background(self, element):
        """
        Fill old position element in the background with most reveling color
        :param element: Boxe prediction of Tensorfolw (coord)
        """

        w, h = ((element.xmax - element.xmin), (element.ymax - element.ymin))

        pil_image = Image.fromarray(self.background_image)
        corner_tl = pil_image.getpixel((element.xmin, element.ymin))
        corner_tr = pil_image.getpixel((element.xmin + w, element.ymin))
        corner_bl = pil_image.getpixel((element.xmin, element.ymin + h))
        corner_br = pil_image.getpixel((element.xmin + w, element.ymin + h))

        lst_corners = [corner_br, corner_bl, corner_tr, corner_tl]
        approx_color = [item for item, count in collections.Counter(lst_corners).items() if count > 1]

        filling_color = approx_color[0] if approx_color else corner_tl

        if isinstance(element, ImageElement):
            pt1 = (element.xmin, element.ymin)
            pt2 = (element.xmax, element.ymax)
        else:
            dx = 0.05
            dy = 0.1
            xmin = int(element.xmin - dx * w) if (element.xmin - dx * w) > 0 else 0
            ymin = int(element.ymin - dy * h) if (element.ymin - dy * h) > 0 else 0
            pt1 = (xmin, ymin)
            pt2 = (int(element.xmax + dx * w), int(element.ymax + dy * h))

        cv2.rectangle(self.background_image, pt1, pt2, filling_color, cv2.FILLED)



