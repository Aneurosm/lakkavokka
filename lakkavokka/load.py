################################################################################
# Copyright (c) 2021 Miroff
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
################################################################################

import sys
import requests
from os.path import join, exists
from PIL import Image
import numpy as np


def loadFromDisk(zoom, x, y, base_path):
    tile_file = base_path \
                .replace('{zoom}', str(zoom)) \
                .replace('{x}', str(x)) \
                .replace('{y}', str(y))

    if not exists(tile_file):
        return None

    pil_img = Image.open(tile_file)
    return np.array(pil_img)


def downloadTile(zoom, x, y, base_url):
    tile_url = base_url \
                .replace('{zoom}', str(zoom)) \
                .replace('{x}', str(x)) \
                .replace('{y}', str(y))

    response = requests.get(tile_url, stream=True)

    pil_img = Image.open(response.raw)
    return np.array(pil_img)
