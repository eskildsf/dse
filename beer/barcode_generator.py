from __future__ import division
import math
import re
import barcode.codex

def renderBarcode(x, y, width, height, text):
    result = ''
    bar = barcode.codex.Code39(text, add_checksum=False)
    ascii = bar.to_ascii()

    unitWidth = width / len(ascii)

    result += '<g transform="translate(%s, %s)" fill="#000">' % (x, y)
    x = 0
    for run in re.split('( +)', ascii):
        runWidth = unitWidth*len(run)
        if run[0] == 'X':
            result += '<rect x="%s" y="0" width="%s" height="%s" />' % (x, runWidth, height)

        x += runWidth

    result += '</g>\n'
    return result

def renderText(x, y, lineHeight, style, text):
    xml = []
    xml.append('<text x="%s" y="%s" xml:space="preserve" style="%s">' % (x, y, style))
    for line in text.split('\n'):
        xml.append('<tspan x="%s" y="%s" sodipodi:role="line">%s</tspan>' % (x, y, line))
        y += lineHeight
    xml.append('</text>')
    return ''.join(xml)

class TableAxis:
    def __init__(self, size, count, margin):
        self.size = size
        self.count = count
        self.margin = margin
        self.cellSize = (size - (count + 1) * margin) / count

    def __call__(self, n):
        return self.margin + n*(self.cellSize + self.margin)

class GenerateBarcodes():
    def __init__(self, data, paperWidth, paperHeight, scale = 1 ):
        self.scale = scale
        self.data = data
        if len(self.data) > 15:
            ncol = 4
        else:
            ncol = 2
        nrows = math.ceil(len(self.data)/ncol)
        paperWidth = 40*ncol*1.4
        paperHeight = 300/16*nrows*1.4
        self.paperWidth = paperWidth
        self.paperHeight = paperHeight
        self.X = TableAxis(paperWidth, ncol, 10)
        self.Y = TableAxis(paperHeight, int(math.ceil(len(data) / self.X.count)), 5)
    def render(self):
        result = '''<svg
   xmlns="http://www.w3.org/2000/svg"
   xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
   xmlns:sodipodi="http://sodipodi.sourceforge.net/DTD/sodipodi-0.dtd"
   version="1.1"
   width="%smm"
   height="%smm"
   viewBox="0 0 %s %s">
''' % (self.paperWidth, self.paperHeight, self.paperWidth, self.paperHeight)
        row = 0
        col = 0
        for code, name in self.data:
            unit = self.Y.cellSize/2
            x = self.X(col)
            y = self.Y(row)
            fontSize = unit*self.scale
            result += renderBarcode(x, y, self.X.cellSize, unit, code)
            result += renderText(x + self.X.cellSize/2, y + 1.8*unit, 0,
            "text-anchor: middle; font-size: %spx; font-family: 'HelveticaNeueLT Pro 55 Roman'" % fontSize, name)
            row += 1
            if row >= self.Y.count:
                row = 0
                col += 1
        result += '</g></svg>'
        return result
