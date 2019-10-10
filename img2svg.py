import os
display_prog = "display"


class Scene:
    """
    Scene regroup all SVG sequence
    """
    def __init__(self, id, name="svg", height=400, width=400):
        self.name = name
        self.items = []
        self.height = height
        self.width = width
        self.id = id
        return

    def add(self, item):
        """
        Add SVG sequence to scene
        :param item:
        """
        self.items.append(item)

    def strarray(self):
        """
        Create svg-xml and complete it with items in scene
        :return:
        """
        var = ["<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>\n",
               "<svg  xmlns:dc=\"http://purl.org/dc/elements/1.1/\" \
                   xmlns:cc=\"http://creativecommons.org/ns#\" \
                   xmlns:rdf=\"http://www.w3.org/1999/02/22-rdf-syntax-ns#\" \
                   xmlns:svg=\"http://www.w3.org/2000/svg\" \
                   xmlns=\"http://www.w3.org/2000/svg\" \
                   xmlns:xlink=\"http://www.w3.org/1999/xlink\" \
                   xmlns:sodipodi=\"http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd\" \
                   xmlns:inkscape=\"http://www.inkscape.org/namespaces/inkscape\" \
                   viewBox=\"0 0 %d %d\" height=\"%d\" width=\"%d\" id=\"%s\" >\n"
               % (self.height, self.width, self.height, self.width, self.id),
               ]

        for item in self.items:
            var += item.strarray()

        var += ["</svg>\n"]

        return var

    def write_svg(self, path, filename=None):
        """
        Write SVG in file
        :param path:
        :param filename:
        :return: SVG Filename
        """
        if filename:
            self.svgname = filename
        else:
            self.svgname = self.name + ".svg"
        file = open(os.path.join(path, self.svgname), 'w', encoding='UTF-8')
        file.writelines(self.strarray())
        file.close()
        return self.svgname

    def display(self, prog=display_prog):
        """
        Display SVG in chosen programme
        :param prog:
        :return:
        """
        os.system("%s %s" % (prog, self.svgname))
        return


class Line:
    def __init__(self,start,end,color,width, id):
        self.start = start
        self.end = end
        self.color = color
        self.width = width
        self.id = id
        return

    def strarray(self):
        return ["  <line id=\"%s\" x1=\"%d\" y1=\"%d\" x2=\"%d\" y2=\"%d\" style=\"stroke:%s;stroke-width:%d\"/>\n" %\
                (self.id, self.start[0], self.start[1], self.end[0], self.end[1], colorstr(self.color), self.width)]


class Image:
    def __init__(self, origin, b64, id, height=100, width=100):
        self.origin = origin
        self.b64 = b64
        self.height = height
        self.width = width
        self.id = id

    def strarray(self):
        return ['  <image id="{}" x="{}" y="{}" height="{}" width="{}" xlink:href="{}" /> \n'.format(
            self.id,
            self.origin[0],
            self.origin[1],
            self.height,
            self.width,
            self.b64
        )]


class Circle:
    def __init__(self,center,radius,fill_color,line_color,line_width, id):
        self.center = center
        self.radius = radius
        self.fill_color = fill_color
        self.line_color = line_color
        self.line_width = line_width
        self.id = id
        return

    def strarray(self):
        return ["  <circle id=\"%s\" cx=\"%d\" cy=\"%d\" r=\"%d\"\n" %\
                (self.id, self.center[0], self.center[1], self.radius),
                "    style=\"fill:%s;stroke:%s;stroke-width:%d\"  />\n" % (colorstr(self.fill_color),colorstr(self.line_color),self.line_width)]


class Ellipse:
    def __init__(self,center,radius_x,radius_y,fill_color,line_color,line_width, id):
        self.center = center
        self.radiusx = radius_x
        self.radiusy = radius_y
        self.fill_color = fill_color
        self.line_color = line_color
        self.line_width = line_width
        self.id = id

    def strarray(self):
        return ["  <ellipse id=\"%s\" cx=\"%d\" cy=\"%d\" rx=\"%d\" ry=\"%d\"\n" %\
                (self.id, self.center[0],self.center[1],self.radius_x,self.radius_y),
                "    style=\"fill:%s;stroke:%s;stroke-width:%d\"/>\n" % (colorstr(self.fill_color),colorstr(self.line_color),self.line_width)]


class Polygon:
    def __init__(self,points,fill_color,line_color,line_width, id):
        self.points = points
        self.fill_color = fill_color
        self.line_color = line_color
        self.line_width = line_width
        self.id = id

    def strarray(self):
        polygon="<polygon points=\""
        for point in self.points:
            polygon+=" %d,%d" % (point[0],point[1])
        return [polygon,\
               "\" \n id=\"%s\" style=\"fill:%s;stroke:%s;stroke-width:%d\"/>\n" %\
               (self.id, colorstr(self.fill_color),colorstr(self.line_color),self.line_width)]


class ButtonRectangle:
    def __init__(self, rectangle, text, id):
        self.rectangle = rectangle
        self.text = text
        self.id = "buttonRect" + id

    def strarray(self):

        rect_str = ""
        text_str = ""

        for elem in self.rectangle.strarray():
            rect_str += elem
        for elem in self.text.strarray():
            text_str += elem

        return ['  <g> id="{}" \n '.format(self.id),
                rect_str,
                text_str,
                ' </g> \n '
                ]


class Rectangle:
    def __init__(self,origin,height,width,fill_color,line_color,line_width, id):
        self.origin = origin
        self.height = height
        self.width = width
        self.fill_color = fill_color
        self.line_color = line_color
        self.line_width = line_width
        self.id = id
        return

    def strarray(self):
        return ["  <rect id=\"%s\" x=\"%d\" y=\"%d\" height=\"%d\"\n" %\
                (self.id, self.origin[0],self.origin[1],self.height),
                "    width=\"%d\" style=\"fill:%s;stroke:%s;stroke-width:%d\" />\n" %\
                (self.width,colorstr(self.fill_color),colorstr(self.line_color),self.line_width)]


class Tspan:
    def __init__(self, x, dy, text, id):
        self.x = x
        self.dy = dy
        self.text = text
        self.id = id

    def strarray(self):
        return '<tspan id="{}" x="{}" dy="{}">{}</tspan>\n'.format(
            self.id, self.x, self.dy, self.text
        )


class Text:
    def __init__(self,origin,text,size,color, id, option=''):
        self.origin = origin
        self.text = text
        self.size = size
        self.color = color
        self.option = option
        self.lst_tspan = []
        self.id = id
        return

    def add_tspan(self, tspan):
        self.lst_tspan.append(tspan)

    def strarray(self):
        if len(self.lst_tspan) > 0:
            text = [' <text id="{}" x="{}" y="{}" style="font-size:{}px;fill:{};stroke:none;" {} >\n '.format(
                str(self.id), str(self.origin[0]), str(self.origin[1]), self.size, colorstr(self.color), self.option
            )]
            for tspan in self.lst_tspan:
                text.append(tspan.strarray())
            text.append("  </text>\n")

            return text

        return ["  <text id=\"%s\" x=\"%s\" y=\"%s\" style=\"font-size:%spx;fill:%s;stroke:none;\" %s >\n" %\
                (self.id, str(self.origin[0]),str(self.origin[1]),self.size,colorstr(self.color), self.option),
                "   %s\n" % self.text,
                "  </text>\n"]


def colorstr(hexa):
    return hexa
    # if isinstance(rgb, str):
    #     rgb = rgb.lstrip('#')
    #     if not rgb:
    #         return 255, 255, 255
    #     return tuple(int(rgb[i:i + 2], 16) for i in (0, 2, 4))
    #
    # else:
    #     print(rgb)
    #     return "#%x%x%x" % (rgb[0]//16,rgb[1]//16,rgb[2]//16)

