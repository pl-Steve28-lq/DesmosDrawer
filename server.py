import json
from flask import Flask
from flask_cors import CORS

from PIL import Image
from numpy import array, zeros, uint32
from potrace import Bitmap

app = Flask(__name__)
CORS(app)

def imageToArray(filename):
  img = Image.open(filename)
  w, h = img.size
  data = array(img.getdata()).reshape(h, w, 3)
  bindata = zeros((h, w), uint32)
  for i, row in enumerate(data):
    for j, byte in enumerate(row):
      bindata[h-i-1, j] = 1 if sum(byte) < 127*3 else 0
  return bindata

def imageToSVG(path):
  data = imageToArray(path)
  bmp = Bitmap(data)
  path = bmp.trace()
  return path

Bezier = lambda t0, t1: f'{t0:.3f}(1-t)+{t1:.3f}t'
UBezier = lambda t0, t1: f'({t0})(1-t)+({t1})t'

def imageToBezier(path):
  latex = ''
  latex += '['

  svg = imageToSVG(path)

  for curve in svg.curves:
    segments = curve.segments
    start = curve.start_point
    for segment in segments:
      x0, y0 = start
      if segment.is_corner:
        x1, y1 = segment.c
        x2, y2 = segment.end_point
        
        X1, Y1 = Bezier(x0, x1), Bezier(y0, y1)
        X2, Y2 = Bezier(x1, x2), Bezier(y1, y2)
        latex += f'"({X1},{Y1})","({X2},{Y2})",'
      else:
        x1, y1 = segment.c1
        x2, y2 = segment.c2
        x3, y3 = segment.end_point
        
        X = UBezier(
            UBezier(Bezier(x0, x1), Bezier(x1, x2)),
            UBezier(Bezier(x1, x2), Bezier(x2, x3))
        )
        Y = UBezier(
            UBezier(Bezier(y0, y1), Bezier(y1, y2)),
            UBezier(Bezier(y1, y2), Bezier(y2, y3))
        )
        
        latex += f'"({X},{Y})",'
      start = segment.end_point

  latex = latex[:-1]
  latex += ']'
  return latex

curve = imageToBezier('wak.jpg')

@app.route('/')
def index():
  return curve

import sys
app.run(host='0.0.0.0', port=int(sys.argv[1]))
