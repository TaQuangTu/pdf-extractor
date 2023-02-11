import argparse
import os
import uuid

import torch
from flask import Flask, jsonify, request

from pdf_extractor.extractor import PDFExtractor


def make_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--ip", default="0.0.0.0", help="Ip of running host")
    parser.add_argument("-p", "--port", default=4444, help="Port of host")
    return parser


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
args = make_parser().parse_args()

pdf_extractor = PDFExtractor()


@app.route('/')
def hello():
    return "Send POST request to '/predict' endpoint with an image to get predictions"


@app.route('/heath', methods=['GET'])
def health():
    return jsonify(True)


@app.route('/extract', methods=['POST'])
@torch.no_grad()
def extract():
    file = request.files['file']
    tmp_file = uuid.uuid4().__str__().replace("-", "") + ".pdf"
    file.save(tmp_file)
    ratio, threshold = (20,1), 0.7
    if "threshold" in request.form:
        threshold = float(request.form["threshold"])
    if "ratio" in request.form:
        w,h = request.form["ratio"].split(",")[:2]
        ratio = (int(w),int(h))
    result = pdf_extractor.extract(tmp_file, ratio, threshold)
    os.remove(tmp_file)
    return jsonify(result)


if __name__ == '__main__':
    app.run(host=args.ip, port=args.port)
