import cv2
import numpy as np
from PIL import Image, ImageChops
from ocr import preprocessing, resizing
from skimage.color import rgb2lab, deltaE_cie76
from colormap.colors import hex2rgb, rgb2hsv, hsv2rgb


def differentiate_colors(c1, c2, diff):
    """
    :param c1: color in hex string format
    :param c2: same
    :param diff: arbitrary treshold for similarity value
    :return: new c1 & c2 values, differentiated if they were too similar
    """

    r1, g1, b1 = hex2rgb(c1, normalise=False)
    lab1 = rgb2lab([[[r1, g1, b1]]])
    r2, g2, b2 = hex2rgb(c2, normalise=False)
    lab2 = rgb2lab([[[r2, g2, b2]]])
    cdiff = (deltaE_cie76(lab1, lab2) * 1e5)[0][0]

    if cdiff < diff:
        h1, s1, v1 = rgb2hsv(r1, g1, b1, normalised=False)
        h2, s2, v2 = rgb2hsv(r2, g2, b2, normalised=False)

        if v1 <= v2 < .5:
            v2 = 1.5 * v2 if 1.5 * v2 <= 1 else 1
        else:
            v2 = .75 * v2

        r1, g1, b1 = hsv2rgb(h1, s1, v1, normalised=True)
        r2, g2, b2 = hsv2rgb(h2, s2, v2, normalised=True)
        c1, c2 = (rgb2hex([int(r1*255), int(g1*255), int(b1*255)]), rgb2hex([int(r2*255), int(g2*255), int(b2*255)]))

    return c1, c2


def liken_colors(c1, c2, diff):
    """
    :param c1: color attribute of a text element (either text_color or [button_color, text_color] in hex string format
    :param c2: same
    :param diff: arbitrary treshold for similarity value
    :return: new c1 & c2 values, both the same if they were similar enough
    """

    c1t, c2t = (c1[1], c2[1]) if len(c1) == 2 else (c1, c2)

    r1, g1, b1 = hex2rgb(c1t, normalise=False)
    lab1 = rgb2lab([[[r1, g1, b1]]])
    r2, g2, b2 = hex2rgb(c2t, normalise=False)
    lab2 = rgb2lab([[[r2, g2, b2]]])
    cdiff = (deltaE_cie76(lab1, lab2) * 1e5)[0][0]

    if cdiff < diff:
        c2t = c1t

    new_colors = ([c1[0], c1t], [c2[0], c2t]) if len(c1) == 2 else (c1t, c2t)

    return new_colors


def remove_image_borders(image):
    """
    find if an image has border (from approximate object detections result) by looking at first pixel color, and if so
    remove them
    :param image: any
    :return: same image without borders (if it had any)
    """

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    bg = Image.new(pil_image.mode, pil_image.size, pil_image.getpixel((0, 0)))
    diff = ImageChops.difference(pil_image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    bbox = diff.getbbox()
    if bbox:
        pil_image = pil_image.crop(bbox)

    cv2_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    return cv2_image


def find_text_nb_of_lines(text_image):
    """
    :param text_image: any BGR image of text (aligned = not rotated)
    :return: number of lines found in text_image
    """

    binary = 255 - preprocessing(text_image)

    hist = cv2.reduce(binary, 1, cv2.REDUCE_AVG).reshape(-1)

    h = text_image.shape[0]

    lines = []
    for y in range(h - 1):
        try:
            if hist[y + 1] <= 2 < hist[y]:
                lines.append(y)
        except IndexError:
            pass

    return len(lines) if len(lines) > 0 else 1


def find_text_color(cropped_text):
    """
    compute text color by converting image to binary (OTSU treshold), take first black pixel (= first
    and find its color value in the original text image
    :param cropped_text: numpy image of a text element already cropped
    :return: text color in hex string format
    """
    height = cropped_text.shape[0]
    binary = preprocessing(cropped_text)
    binary = resizing(binary, height)

    black_pixels = np.argwhere(binary == 0)

    try:
        bgr = cropped_text[black_pixels[1][0]][black_pixels[1][1]]
    except IndexError:
        bgr = cropped_text[black_pixels[0][0]][black_pixels[0][1]]

    return bgr2hex(bgr)


def find_background_color(image):
    pil_image = Image.fromarray(image)
    background_color = pil_image.getpixel((0, 0))
    return background_color


def bgr2hex(bgr):
    """
    :param bgr: bgr color in the form of an array [.., .., ..]
    :return: hex color in string format
    """
    return '#%02x%02x%02x' % (bgr[2], bgr[1], bgr[0])


def rgb2hex(rgb):
    """
    :param rgb: rgb color in the form of an array [.., .., ..]
    :return: hex color in string format
    """
    return '#%02x%02x%02x' % (rgb[0], rgb[1], rgb[2])

