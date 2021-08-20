from flask import Flask
from flask_cors import CORS

from numpy import median as med
import potrace as p
import cv2

app = Flask(__name__)
CORS(app)

def get_contours(filename, nudge = .33):
  image = cv2.imread(filename)
  gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
  median = max(10, min(245, med(gray)))
  lower = int(max(0, (1 - nudge) * median))
  upper = int(min(255, (1 + nudge) * median))
  filtered = cv2.bilateralFilter(gray, 5, 50, 50)
  edged = cv2.Canny(filtered, lower, upper, L2gradient = False)
  
  return edged[::-1]

def get_trace(data):
  for i in range(len(data)):
    data[i][data[i] > 1] = 1
  bmp = p.Bitmap(data)
  path = bmp.trace(2, p.TURNPOLICY_MINORITY, 1.0, 1, .5)
  return path

Bezier = lambda t0, t1: f'{t0:.3f}(1-t)+{t1:.3f}t'
UBezier = lambda t0, t1: f'({t0})(1-t)+({t1})t'

def imageToBezier(path):
  latex = ''
  latex += '['

  svg = get_trace(get_contours(path))

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

curve = imageToBezier('h.jpg')

@app.route('/')
def index():
  return curve

import sys
app.run(host='0.0.0.0', port=int(sys.argv[1]))
