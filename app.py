from flask import Flask, jsonify, request, render_template

from PIL import Image
import os
import base64
import io
import numpy as np
import torch
import random

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
    b64_start_index = blob.decode().find('base64') + len('base64,')
    b64data = blob[b64_start_index:]
    base64_decoded = base64.b64decode(b64data)
    image = Image.open(io.BytesIO(base64_decoded))
    image_np = np.array(image).astype(np.int) # note: could be RGB (3D np array) or Greyscale (2D array) depending on image format
    latex = ['\\[e^{-i\\pi} + 1 = 0\\]', '\\[\\frac{1}{2}\\]', '\\[h(x)\\cdot \\exp(\\eta^T t(x) - a(\\eta))\\]']
    # TODO: latex = call_model(image_np)
    return latex[random.randint(0, 2)]