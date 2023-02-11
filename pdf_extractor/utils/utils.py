import os.path
import re
from pdf2image import convert_from_path


def is_possible_signer_text(text):
    length_check = len(text) > 5
    not_contain_digit = len(re.findall('\d+', text)) == 0
    return length_check and not_contain_digit


def is_possible_NO_text(text):
    length_check = len(text) >= 5
    return length_check


def is_possible_date_text(text):
    length_check = len(text) > 20
    contain_digit = len(re.findall('\d+?', text)) >= 4
    return length_check and contain_digit


def is_possible_signer_box(image_shape, xmin, ymin, xmax, ymax):
    """
    :param xmin:
    :param ymin:
    :param xmax:
    :param ymax:
    :param image_shape: H x W x C
    :return:
    """
    w = xmax - xmin
    h = ymax - ymin

    size_check = w / h > 2
    x_check = xmax > image_shape[1] * 3 / 4
    length_check = image_shape[1] / 3 > w
    return size_check and x_check and length_check


def is_possible_NO_box(image_shape, xmin, ymin, xmax, ymax):
    """
    :param xmin:
    :param ymin:
    :param xmax:
    :param ymax:
    :param image_shape: H x W x C
    :return:
    """
    w = xmax - xmin
    h = ymax - ymin

    size_check = w / h > 2
    x_check = xmin < image_shape[1] / 5
    y_check = ymin < image_shape[0] / 7
    length_check = image_shape[1] / 3 > w
    return size_check and x_check and y_check and length_check


def is_possible_date_box(image_shape, xmin, ymin, xmax, ymax):
    """
    :param xmin:
    :param ymin:
    :param xmax:
    :param ymax:
    :param image_shape: H x W x C
    :return:
    """
    w = xmax - xmin
    h = ymax - ymin

    size_check = w / h > 2
    x_check = xmax > image_shape[1] * 3 / 4
    y_check = ymin < image_shape[0] / 6
    length_check = image_shape[1] / 2 > w
    return size_check and x_check and y_check and length_check


def pdf_2_image(pdf_path, save_dir=None):
    """return image and save to image_path"""

    # Store Pdf with convert_from_path function
    images = convert_from_path(pdf_path)

    if save_dir is not None:
        for i in range(len(images)):
            # Save pages as images in the pdf
            images[i].save(os.path.join(save_dir, 'page' + str(i) + '.jpg'), 'JPEG')
