import cv2
import numpy as np
from PIL import Image, ImageChops
from ocr import preprocessing, resizing
from skimage.color import rgb2lab, deltaE_cie76
from colormap.colors import hex2rgb, rgb2hsv, hsv2rgb

import matplotlib
matplotlib.use('TkAgg')


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


def find_text_nb_of_lines(text):

    nb_of_lines = text.count('\n') + text.count('\r') + 1

    return nb_of_lines


def find_text_color(cropped_text):
    """
    find second most present color in the image = text color ?
    :param cropped_text: numpy image of a text element already cropped
    :return: text color in hex string format
    """

    pixels = np.float32(cropped_text.reshape(-1, 3))

    _, labels, palette = cv2.kmeans(pixels, 20, None, (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1), 10,
                                    cv2.KMEANS_RANDOM_CENTERS)
    _, counts = np.unique(labels, return_counts=True)
    indices = np.argsort(counts)[::-1]

    bgr = palette[indices[1]].astype(np.int)

    return bgr2hex(bgr)


def find_button_text_position(text_image):
    """
    :param text_image: any BGR image of text (aligned = not rotated)
    :return: upper, lower tuple : y axis value of start of first text line and bottom of last
    """

    h, w = text_image.shape[:2]
    x = int(h/8)
    text_image = text_image[x:-x, x:-x]
    binary = 255 - preprocessing(text_image)
    binary = resizing(binary, h)

    hist = cv2.reduce(binary, 1, cv2.REDUCE_AVG).reshape(-1)

    th = 50
    uppers = [y for y in range(h - 1) if hist[y] <= th < hist[y + 1]]
    lowers = [y for y in range(h - 1) if hist[y] > th >= hist[y + 1]]

    try:
        if len(uppers) > 3:
            ymin = uppers[1]
            ymax = lowers[-2] if lowers[-2] - ymin > 5 else lowers[-1]
        else:
            ymin = uppers[0]
            ymax = lowers[-1]
    except IndexError:
        ymin = 0
        ymax = int(0.6 * h)

    hist = cv2.reduce(binary, 0, cv2.REDUCE_AVG).reshape(-1)

    count = np.bincount(hist)

    th = np.argmax(count)
    lefters = [x for x in range(len(hist) - 1) if hist[x] <= th < hist[x + 1]]
    righters = [x for x in range(len(hist) - 1) if hist[x] > th >= hist[x + 1]]

    # if no border :
    # xmin = lefters[0]
    # xmax = righters[-1]

    # if border :
    # xmin = lefters[1]
    # xmax = righters[-2]

    return ymin, ymax


def find_button_properties(button_image):

    height, width = button_image.shape[:2]

    upper, lower = find_button_text_position(button_image)
    text_height = 1.5 * (lower - upper)

    x = int(height / 10)
    ymin = upper - x if upper - x > 0 else 0
    ymax = lower + x if lower + x < height else height
    xmin = x
    xmax = width - x

    button_image = button_image[ymin:ymax, xmin:xmax]

    x = int(xmax/2)
    bgr1 = (button_image[0][x]).astype(np.int32)
    bgr2 = button_image[0][x-1].astype(np.int32)
    bgr3 = button_image[1][x+1].astype(np.int32)

    bgr_mean = ((bgr1 + bgr2 + bgr3) / 3).astype(int)

    button_hex = bgr2hex(bgr_mean)

    text_color = find_text_color(button_image)

    return button_image, button_hex, text_color, text_height


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

