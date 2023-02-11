import os.path
import shutil
from collections import defaultdict

import numpy as np
import cv2
from PIL import Image
from tacv.fileUtils import get_all_files, get_file_name

from pdf_extractor.utils.ocr_utils import VietOCR
from pdf_extractor.utils.utils import pdf_2_image, is_possible_NO_box, is_possible_signer_box, is_possible_date_box, \
    is_possible_date_text, is_possible_NO_text, is_possible_signer_text

NO = "no"
SIGNER = "signer"
DATE = "date"


class PDFExtractor:
    def __init__(self, temp_dir="/tmp/pdf_extractor"):
        """
        :param temp_dir: where the extraction process works
        """
        self.temp_dir = temp_dir

    def detect_text_lines(self, image: np.ndarray, target_shape):
        """
        :param image:
        :param target_shape: ratio of text boxes wanted, recommend is 20:1
        :return: list of bounding boxes possibly containing text lines. The boxes are in (xmin,ymin,xmax,ymax) format
        """
        # Load image, grayscale, Gaussian blur, Otsu's threshold
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (7, 7), 0)
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

        # Create rectangular structuring element and dilate
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, target_shape)
        dilate = cv2.dilate(thresh, kernel, iterations=4)

        # Find contours and draw rectangle
        cnts = cv2.findContours(dilate, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = cnts[0] if len(cnts) == 2 else cnts[1]

        boxes = []

        for c in cnts:
            x, y, w, h = cv2.boundingRect(c)
            boxes.append([x, y, x + w, y + h])
        return boxes

    def _extract_a_page(self, image: np.ndarray, target_shape, confidence_score):
        # detect all text boxes
        text_boxes = self.detect_text_lines(image, target_shape)
        text_boxes = sorted(text_boxes, key=lambda x: x[-1])  # sort by ymax

        # results
        results = {NO: [], SIGNER: [], DATE: []}
        # remove trash boxes, select only possible-interested boxes (NO, date, signer)
        for idx, box in enumerate(text_boxes):
            xmin, ymin, xmax, ymax = box
            cv2.rectangle(image, (xmin, ymin), (xmax, ymax), (36, 255, 12), 2)
            key = ""
            if is_possible_NO_box(image.shape, xmin, ymin, xmax, ymax):
                key = NO
            if is_possible_date_box(image.shape, xmin, ymin, xmax, ymax):
                key = DATE
            if is_possible_signer_box(image.shape, xmin, ymin, xmax, ymax):
                if idx + 7 >= len(text_boxes):
                    # signer only appears in bottom most text boxes, assume within 7 bottom most ones.
                    key = SIGNER
            if key == "":
                continue

            tbox = image[ymin:ymax, xmin:xmax]
            tbox = Image.fromarray(tbox)
            text, prob = VietOCR.get_text(tbox, return_prob=True)

            if prob < confidence_score:
                continue
            if len(text) <= 0:
                continue
            if not PDFExtractor.is_possible_text(key, text):
                continue

            results[key].append(text)
        return results

    @staticmethod
    def is_possible_text(key, text):
        if key == NO:
            return is_possible_NO_text(text)
        if key == DATE:
            return is_possible_date_text(text)
        if key == SIGNER:
            return is_possible_signer_text(text)
        return False

    def extract(self, pdf_path: str, target_shape=(20, 1), confidence_threshold=0.7):
        """
        :param pdf_path: path to a pdf file
        :return:
        """
        # just to be sure no trash files in the directory
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
        os.makedirs(self.temp_dir)

        # convert pdf pages to images, save the image in a temporal directory
        pdf_2_image(pdf_path, save_dir=self.temp_dir)

        # get list of image paths from the directory
        image_paths = get_all_files(self.temp_dir)
        image_paths.sort()
        all_page_results = []
        # for each image
        for idx, image_path in enumerate(image_paths):
            image = cv2.imread(image_path)
            page_result = self._extract_a_page(image, target_shape, confidence_threshold)
            all_page_results.append(page_result)

            # save image for debugging
            image_name = get_file_name(image_path) + "_visual.jpg"
            save_path = os.path.join(self.temp_dir, image_name)
            cv2.imwrite(save_path, image)

        final_res = self.gather_all_page_results(all_page_results)
        return dict(final_res)

    def gather_all_page_results(self, page_result: list):
        final_res = defaultdict(list)
        for page_id, res in enumerate(page_result):
            if page_id != 0:  # pages which are other than 0 do not have date, and NO info
                res[NO] = []
                res[DATE] = []
            final_res[NO].extend(res[NO])
            final_res[DATE].extend(res[DATE])
            final_res[SIGNER].extend(res[SIGNER])
        return final_res
