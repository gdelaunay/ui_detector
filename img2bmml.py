import os
from abc import ABC, abstractmethod
import urllib.parse


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
        self.width = width
        self.height = height

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
            var += item.strarray()

        var += ["</controls>\n</mockup>"]

        return var

    def write_bmml(self, path):
        """
        Write bmml in file
        :param path:
        :param filename:
        :return: SVG Filename
        """

        self.name = self.name + ".bmml"
        file = open(os.path.join(path, self.name), 'w', encoding='UTF-8')
        file.writelines(self.strarray())
        file.close()
        return self.name


class Text(GraphicElementBmml):
    def __init__(self, id, x, y, text, width, height):
        super().__init__(id, x, y, width, height)
        self.text = text

    def redact_bmml(self):
        bmml_element = [
            '<control controlID="{}" controlTypeID="com.balsamiq.mockups::SubTitle" x="{}" y="{}" w="-1" h="-1" measuredW="{}" measuredH="{}" zOrder="{}" locked="false" isInGroup="-1">\n'.format(
                self.id, self.x, self.y, self.width, self.height, self.id
        )]

        text = text_treatment_4_balsamiq(self.text)

        bmml_element += ['<controlProperties>\n']
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
            '<control controlID="{}" controlTypeID="com.balsamiq.mockups::Button" x="{}" y="{}" w="-1" h="-1" measuredW="{}" measuredH="{}" zOrder="{}" locked="false" isInGroup="-1">\n'.format(
                self.id, self.x, self.y, self.width, self.height, self.id
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
            '<control controlID="{}" controlTypeID="com.balsamiq.mockups::Image" x="{}" y="{}" w="-1" h="-1" measuredW="{}" measuredH="{}" zOrder="{}" locked="false" isInGroup="-1">\n'.format(
                self.id, self.x, self.y, self.width, self.height, self.id
            )]
        bmml_element += ['<controlProperties>\n']
        bmml_element += ['<src>./assets/{}</src>\n'.format(
            self.path
        )]
