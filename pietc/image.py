import numpy as np
import itertools as it
from random import randrange, seed
from PIL import Image
from pietc.piet import Command

COLORSHAPE = (6,3)
COLORLEN = 18
COLORVALS = np.empty(COLORSHAPE,dtype=object)
COLORVALS[:] = [
    [(255,192,192), (255,0,0), (192,0,0)],
    [(255,255,192), (255,255,0), (192,192,0)],
    [(192,255,192), (0,255,0), (0,192,0)],
    [(192,255,255), (0,255,255), (0,192,192)],
    [(192,192,255), (0,0,255), (0,0,192)],
    [(255,192,255), (255,0,255), (192,0,192)],
]
COLORIDXS = dict(zip(COLORVALS.flatten(),
                     zip(*np.indices(COLORSHAPE).reshape((2,COLORLEN)))))
COLORNAMES = [
    'RED',
    'YELLOW',
    'GREEN',
    'CYAN',
    'BLUE',
    'PURPLE',
]
COLORS = dict(zip(COLORNAMES, COLORVALS))
BLACK = (0,0,0)
WHITE = (255,255,255)
seed()
CURRENT_COLOR = COLORNAMES[randrange(len(COLORNAMES))]

CODELLEN = 16
BUSWIDTH = 3

class Codel (object):
    def __init__ (self, context, color=CURRENT_COLOR):
        self.is_vertical = context.is_main
        self.is_horizontal = not self.is_vertical
        self.is_branch = False
        self.needs_branch = False
        self.branch_depth = 0
        self.context = context
        self.data = np.empty((CODELLEN, 1) if self.is_vertical
                                          else (1, CODELLEN), 'O')
        self.data.fill(BLACK)
        self.value = 0

    @property
    def base_color (self):
        return self.data[0]

    def _check_value (self):
        rval = 0
        for c in self.data:
            if (c == BLACK) or (c != self.base_color):
                return rval
            else:
                rval += 1
        return rval

    def put (self, value, color=CURRENT_COLOR):
        if isinstance(value, (tuple, list)):
            start, value = value
        else:
            start = 0
        if start+value > len(self.data):
            raise RuntimeError('codel overflow')
        self.data.put(range(start, value+1), color)
        self.value = self._check_value()

    def append (self, value, color):
        if (self.value + value) > len(self.data):
            raise RuntimeError('codel overflow')
        self.data.put(range(self.value, value+1), color)
        if color == self.base_color:
            self.value = self._check_value()

    def branch_to (self, codel):
        if not codel.is_branch:
            raise RuntimeError('broken branch')
        if self.needs_branch or self.is_branch:
            raise RuntimeError('cannot overwrite branch')
        self.needs_branch = True
        self.branch_depth = codel.branch_depth

    def make_branch (self):
        if self.needs_branch or self.is_branch:
            raise RuntimeError('cannot overwrite branch')
        self.is_branch = True
        self.branch_depth = self.context.add_track()

    def __len__ (self):
        return len(self.data)

    def __repr__ (self):
        return 'Codel({}, {})'.format(self.value, self.base_color)

    def __str__ (self):
        return str(self.data.flatten())

class Context (object):
    def __init__ (self, index):
        self.index = int(index)
        self.is_main = (self.index == 0)
        self.tracks = 0
        self.codels = []

    @property
    def shape (self):
        size = CODELLEN + BUSWIDTH*self.tracks
        if self.is_main:
            return (len(self.codels), size)
        else:
            return (size, len(self.codels))

    def append (self, codel):
        self.codels.append(codel)

    def add_track (self):
        self.tracks += 1
        return self.tracks

    def draw (self):
        pass

def shift_color (command, color=CURRENT_COLOR):
    idx = tuple(map(np.mod, COLORIDXS[color] + command.shift, COLORSHAPE))
    color[:] = COLORVALS[idx]
    return color
