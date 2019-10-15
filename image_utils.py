import cv2
import numpy as np
from PIL import Image, ImageChops
from ocr import preprocessing, resizing
from skimage.color import rgb2lab, deltaE_cie76
from colormap.colors import hex2rgb, rgb2hsv, hsv2rgb

import matplotlib
matplotlib.use('TkAgg')


def get_main_color(image):
    """
    Get most reveling color in image
    :param image:
    :return: Color Bgr Tuple
    """
    a2D = image.reshape(-1, image.shape[-1])
    col_range = (256, 256, 256)  # generically : a2D.max(0)+1
    a1D = np.ravel_multi_index(a2D.T, col_range)

    return np.unravel_index(np.bincount(a1D).argmax(), col_range)


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


def similar_colors(c1, c2, diff):

    lab1 = rgb2lab([[[c1[2], c1[1], c1[0]]]])
    lab2 = rgb2lab([[[c2[2], c2[1], c2[0]]]])
    cdiff = (deltaE_cie76(lab1, lab2) * 1e5)[0][0]

    if cdiff < diff:
        return True
    else:
        return False


def detect_border(image):
    """
     find if an image has border (from approximate object detections result) by looking at first pixel color
    :param image:
    :return: box border, array Image
    """

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb_image)
    bg = Image.new(pil_image.mode, pil_image.size, pil_image.getpixel((0, 0)))
    diff = ImageChops.difference(pil_image, bg)
    diff = ImageChops.add(diff, diff, 2.0, -100)
    return diff.getbbox(), pil_image


def remove_image_borders(image):
    """
    Remove image border
    :param image: any
    :return: same image without borders (if it had any)
    """

    bbox, pil_image = detect_border(image)

    if bbox:
        pil_image = pil_image.crop(bbox)

    cv2_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    return cv2_image


def find_text_nb_of_lines(text):
    """
    Return number of lines in text
    :param text:
    :return: Int
    """
    nb_of_lines = text.count('\n') + text.count('\r') + 1

    return nb_of_lines


def find_text_color(cropped_text):
    """
    find second most present color in the image = text color ?
    :param cropped_text: numpy image of a text element already cropped
    :return: text color in hex string format
    """

    binary = preprocessing(cropped_text)
    black_pixels = np.argwhere(binary == 0)
    pixels = []

    if len(black_pixels) > 1:
        for pixel in black_pixels:
            pixels.append(cropped_text[pixel[0]][pixel[1]])
    else:
        pixels.append(cropped_text[black_pixels[0][1]][black_pixels[0][1]])

    b, g, r = get_xmost_occuring_color(pixels, 1)

    bgr = [b, g, r]

    return bgr2hex(bgr)


def find_text_position(text_image):
    """
    :param text_image: any BGR image of text (aligned = not rotated)
    :return: upper, lower tuple : y axis value of start of first text line and bottom of last
    """

    h, w = text_image.shape[:2]
    binary = 255 - preprocessing(text_image)

    hist = cv2.reduce(binary, 1, cv2.REDUCE_AVG).reshape(-1)

    count = np.bincount(hist)
    th = np.argmax(count)

    uppers = [y for y in range(len(hist) - 1) if hist[y] <= th < hist[y + 1]]
    lowers = [y for y in range(len(hist) - 1) if hist[y] > th >= hist[y + 1]]
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

    have_border, _ = detect_border(text_image)

    if have_border and lefters and righters:
        xmin = lefters[1] if 1 in lefters else lefters[0]
        xmax = righters[-2] if -2 in righters else righters[-1]
    else:
        xmin = lefters[0] if lefters else 0
        xmax = righters[-1] if righters else int(w * 0.6)

    return ymin, ymax, xmin, xmax


def find_button_properties(button_image):
    """
    Get Coord of text in button, main color and border color
    :param button_image:
    :return: Information on button
    """

    height, width = button_image.shape[:2]
    ymin, ymax, xmin, xmax = find_text_position(button_image)
    text_height = 1.1 * (ymax - ymin)
    text_width = 1.1 * (xmax - xmin)

    x = int(height / 10)
    ymin = ymin - x if ymin - x > 0 else 0
    ymax = ymax + x if ymax + x < height else height
    xmin = x
    xmax = width - x

    lst_dim_text = [ymin, ymax, xmin, xmax]
    """
    button_image = button_image[ymin:ymax, xmin:xmax]
    x = int(xmax/2)
    bgr1 = (button_image[0][x]).astype(np.int32)
    bgr2 = button_image[0][x-1].astype(np.int32)
    bgr3 = button_image[1][x+1].astype(np.int32)

    bgr_mean = ((bgr1 + bgr2 + bgr3) / 3).astype(int)

    button_hex = bgr2hex(bgr_mean)
    """
    text_color = find_text_color(button_image)

    return button_image, text_width, text_color, text_height, lst_dim_text


def crop_button(button_image, background_color, coords):

    class Break(Exception):
        pass

    button_color = get_xmost_occuring_color(button_image, 1)

    if similar_colors(button_color, background_color, .2):
        button_color = get_xmost_occuring_color(button_image, 2)

    h, w = button_image.shape[:2]
    binary = 255 - preprocessing(button_image)

    yhist = cv2.reduce(binary, 1, cv2.REDUCE_AVG).reshape(-1)
    xhist = cv2.reduce(binary, 0, cv2.REDUCE_AVG).reshape(-1)

    th = 15

    ylimits = [y for y in range(len(yhist) - 1) if ((yhist[y] < yhist[y + 1] - th) | (yhist[y] > yhist[y + 1] + th))]

    xlimits = [x for x in range(len(xhist) - 1) if ((xhist[x] < xhist[x + 1] - th) | (xhist[x] > xhist[x + 1] + th))]

    th = .3

    try:
        ymin = 0
        if similar_colors(get_xmost_occuring_color(button_image[:1, :], 1), button_color, th):
            raise Break
        for y in ylimits:
            if similar_colors(get_xmost_occuring_color(button_image[y + 1:y + 2, :], 1), button_color, th):
                ymin = y + 1
                raise Break
    except Break:
        pass

    ylimits.reverse()

    try:
        ymax = h
        if similar_colors(get_xmost_occuring_color(button_image[-2:-1, :], 1), button_color, th):
            raise Break
        for y in ylimits:
            if similar_colors(get_xmost_occuring_color(button_image[y - 2:y - 1, :], 1), button_color, th):
                ymax = y
                raise Break
    except Break:
        pass

    try:
        xmin = 0
        if similar_colors(get_xmost_occuring_color(button_image[:, :1], 1), button_color, th):
            raise Break
        for x in xlimits:
            if similar_colors(get_xmost_occuring_color(button_image[:, x + 1:x + 2], 1), button_color, th):
                xmin = x + 1
                raise Break
    except Break:
        pass

    xlimits.reverse()

    try:
        xmax = w
        if similar_colors(get_xmost_occuring_color(button_image[:, -2:-1], 1), button_color, th):
            raise Break
        for x in xlimits:
            if similar_colors(get_xmost_occuring_color(button_image[:, x - 2:x - 1], 1), button_color, th):
                xmax = x
                raise Break
    except Break:
        pass

    cropped = button_image[ymin:ymax, xmin:xmax]

    abs_ymin, abs_ymax, abs_xmin, abs_xmax = coords

    abs_ymin += ymin
    abs_ymax -= (h - ymax)
    abs_xmin += xmin
    abs_xmax -= (w - xmax)

    return cropped, bgr2hex(button_color), abs_ymin, abs_ymax, abs_xmin, abs_xmax


def find_background_color(image):
    """
    Return background color
    :param image: Bgr color tuple
    :return:
    """
    pil_image = Image.fromarray(image)
    background_color = pil_image.getpixel((0, 0))
    return background_color


def get_xmost_occuring_color(image, x):
    """
    :param image : image (np.array or list of pixels)
    :return: xmost occurring color in image (in bgr)
    """

    if isinstance(image, list):
        image = np.array(image)
        pairs, counts = np.unique(image, axis=0, return_counts=True)
        count_sort_index = np.argsort(-counts)
        bgr = pairs[count_sort_index[0]]
    else:
        height, width = image.shape[:2]
        image = Image.fromarray(image)
        image = image.resize((width, height), resample=0)
        pixels = image.getcolors(width * height)
        sorted_pixels = sorted(pixels, key=lambda t: t[0])
        bgr = sorted_pixels[-x][1]

    return bgr


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
