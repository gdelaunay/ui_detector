import os
from abc import ABC, abstractmethod
import urllib.parse
from zipfile import ZipFile
from os import walk


# Utils methods
# --------------------------------
def text_treatment_4_balsamiq(text):
    """
    Convert text to url's style text for balsamiq
    :return: string
    """

    return urllib.parse.quote(text)
# --------------------------------


class ElementBmml(ABC):
    """
        Minimum intelligence for bmml sequence
    """

    def __init__(self, id):
        self.id = id

    @abstractmethod
    def redact_bmml(self):
        """ Translate the Element object into bmml format """
        pass


class GraphicElementBmml(ElementBmml, ABC):
    """
        Minimum intelligence for graphic bmml sequence
    """

    def __init__(self, id, x, y, width, height):
        super().__init__(id)
        self.x = x
        self.y = y
        self.width = int(width)
        self.height = int(height)

    @abstractmethod
    def redact_bmml(self):
        """ Translate the Element object into bmml format """
        pass


class Sketch(ElementBmml):
    """
    Main scene for Balsamiq export
    """

    def __init__(self, id, name, width, height):
        super().__init__(id)
        self.name = name
        self.width = width
        self.height = height
        self.items = []

    def add(self, item):
        """
        Add bmml sequence to scene
        :param item:
        """

        self.items.append(item)

    def redact_bmml(self):
        """
        Create bmml structure and complete it with items in skecth
        :return:
        """
        var = ['<mockup version="1.0" skin="sketch" fontFace="Balsamiq Sans" measuredW="{0}" measuredH="{1}" mockupW="{0}" mockupH="{1}">\n'.format(
            self.width, self.height
        )]

        var += ['<controls>\n']

        for item in self.items:
            var += item.redact_bmml()

        var += ["</controls>\n</mockup>"]

        return var

    def write_bmml(self, path):
        """
        Write bmml in file
        :param path:
        :param filename:
        :return: SVG Filename
        """

        file = open(os.path.join('./', self.name + ".bmml"), 'w', encoding='UTF-8')
        file.writelines(self.redact_bmml())
        file.close()

        files_lst = []

        for file in os.listdir("./"):
            if file.endswith(".png") or file.endswith(".bmml"):
                files_lst.append(file)

        with ZipFile(path + '/' + self.name + '.zip', 'w') as archive:
            for file in files_lst:
                if file.endswith('.png'):
                    archive.write(file, 'assets/' + file)
                else:
                    archive.write(file)

        for file in files_lst:
            os.remove(file)

        return self.name + ".zip"


class Text(GraphicElementBmml):
    def __init__(self, id, x, y, text, width, height, text_size):
        super().__init__(id, x, y, width, height)
        self.text = text
        self.text_size = text_size

    def redact_bmml(self):
        bmml_element = [
            '<control controlID="{0}" controlTypeID="com.balsamiq.mockups::SubTitle" x="{1}" y="{2}" w="{3}" h="{4}" measuredW="{3}" measuredH="{4}" zOrder="{0}" locked="false" isInGroup="-1">\n'.format(
                self.id, self.x, self.y, self.width, self.height
        )]

        text = text_treatment_4_balsamiq(self.text)

        bmml_element += ['<controlProperties>\n']
        bmml_element += ['<size>{}</size>'.format(
            self.text_size
        )]
        bmml_element += ['<text>{}</text>'.format(
            text
        )]

        bmml_element += ['</controlProperties>\n</control>\n']

        return bmml_element


class Button(GraphicElementBmml):
    def __init__(self, id, x, y, text, width, height):
        super().__init__(id, x, y, width, height)
        self.text = text

    def redact_bmml(self):
        bmml_element = [
            '<control controlID="{0}" controlTypeID="com.balsamiq.mockups::Button" x="{0}" y="{1}" w="{3}" h="{4}" measuredW="{3}" measuredH="{4}" zOrder="{0}" locked="false" isInGroup="-1">\n'.format(
                self.id, self.x, self.y, self.width, self.height
            )]

        text = text_treatment_4_balsamiq(self.text)

        bmml_element += ['<controlProperties>\n']
        bmml_element += ['<text>{}</text>\n'.format(
            text
        )]
        bmml_element += ['</controlProperties>\n']
        bmml_element += ['</control>\n']

        return bmml_element


class Image(GraphicElementBmml):
    def __init__(self, id, x, y, width, height, path_to_img):
        super().__init__(id, x, y, width, height)
        self.path = path_to_img

    def redact_bmml(self):
        bmml_element = [
            '<control controlID="{0}" controlTypeID="com.balsamiq.mockups::Image" x="{1}" y="{2}" w="{3}" h="{4}" measuredW="{3}" measuredH="{4}" zOrder="{0}" locked="false" isInGroup="-1">\n'.format(
                self.id, self.x, self.y, self.width, self.height
            )]
        bmml_element += ['<controlProperties>\n']
        bmml_element += ['<src>./assets/{}</src>\n'.format(
            self.path.split('/')[-1]
        )]

        bmml_element += ['</controlProperties>\n</control>\n']

        return bmml_element
