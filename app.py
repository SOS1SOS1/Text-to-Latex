from flask import Flask, jsonify, request, render_template

from PIL import Image
import os
import base64
import io
import numpy as np
import torch
import sys
import json
import pdf2image

app = Flask(__name__)

def dir_last_updated(folder):
    return str(max(os.path.getmtime(os.path.join(root_path, f))
                   for root_path, dirs, files in os.walk(folder)
                   for f in files))

@app.route("/")
def hello_world():
    return render_template('index.html', last_updated=dir_last_updated('./static'))

@app.route('/test', methods=['POST'])
def testfn():
    message = {'latex': queryModel(request.data)}
    return jsonify(message)  # serialize and use JSON headers

def queryModel(blob):
    raw_data = json.loads(blob.decode())

    image = None;
    b64_start_index = raw_data['data'].find('base64') + len('base64,')
    b64data = raw_data['data'][b64_start_index:]
    if "pdf" in raw_data['filetype']:
        images = pdf2image.convert_from_bytes(base64.b64decode(b64data))
        image = images[0]
    else:
        base64_decoded = base64.b64decode(b64data)
        image = Image.open(io.BytesIO(base64_decoded))
    image_np = np.array(image).astype(np.int) # note: could be RGB (3D np array) or Greyscale (2D array) depending on image format
    latex = '\\[e^{-i\\pi} + 1 = 0\\]'
    # TODO: latex = call_model(image_np)
    return latex
