#! venv/ python3
# coding: utf-8

import pytesseract
import cv2
import numpy as np


def ocr(text_image):

    processed = preprocessing(text_image)

    resized = resizing(processed, 120)

    pytesseract.pytesseract.tesseract_cmd = 'D:\\delaunay\\env\\Tesseract-OCR\\tesseract'

    # Define config parameters.
    # '-l eng'  for using the English language
    # '--oem 1' for using LSTM OCR Engine (NN) / 0 for legacy engine
    config = '-l eng+fra --oem 1 --psm 3'

    # Run tesseract OCR on image
    text = pytesseract.image_to_string(resized, config=config)

    return text


def preprocessing(text_image):

    gray = cv2.cvtColor(text_image, cv2.COLOR_BGR2GRAY)

    # converting to binary image
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU)

    count_white = np.sum(binary > 0)
    count_black = np.sum(binary == 0)
    if count_black > count_white:
        binary = 255 - binary

    return binary


# resizing to a fixed height (keeping proportions) for OCR efficiency and preprocessing consistency
def resizing(image, x):

    # x = desired height

    im_height, im_width = image.shape

    resized = cv2.resize(image, (int(x*(im_width/im_height)), x))

    return resized


# padding in case text detection graph cropped it to close to the text
def padding(image, padding_size, padding_color):

    x = padding_size

    padded = cv2.copyMakeBorder(image, x, x, x, x, cv2.BORDER_CONSTANT, value=padding_color)

    return padded


def find_main_color(image):
    im2d = image.reshape(-1, image.shape[-1])
    col_range = (256, 256, 256)  # generically : a2D.max(0)+1
    im1d = np.ravel_multi_index(im2d.T, col_range)
    b, g, r = np.unravel_index(np.bincount(im1d).argmax(), col_range)
    return [b, g, r]
