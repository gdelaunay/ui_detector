#! venv/ python3
# coding: utf-8

import pytesseract
import cv2


def ocr(text_image):

    processed = preprocessing(text_image)

    pytesseract.pytesseract.tesseract_cmd = 'D:/delaunay/env/Tesseract-OCR/tesseract'

    # Define config parameters.
    # '-l eng'  for using the English language
    # '--oem 1' for using LSTM OCR Engine (NN) / 0 for legacy engine
    config = '-l eng+fra --oem 1 --psm 3'

    # Run tesseract OCR on image
    text = pytesseract.image_to_string(processed, config=config)

    return text


def preprocessing(text_image):

    gray = cv2.cvtColor(text_image, cv2.COLOR_BGR2GRAY)

    # converting to binary image
    _, binary = cv2.threshold(gray, 120, 255, cv2.THRESH_OTSU)

    # optimal character height for Tesseract ?
    resized = resizing(binary, 60)

    return resized


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
