import numpy as np
import itertools as it
from random import randrange, seed
from PIL import Image

COMMAND_DIFFERENTIALS = {
        'push':(1,0),
        'pop':(2,0),
        'add':(0,2),
        'subtract':(1,1),
        'multiply':(2,1),
        'divide':(0,2),
        'mod':(1,2),
        'invert':(2,2),
        'greater':(0,3),
        'pointer':(1,3),
        'switch':(2,3),
        'duplicate':(0,4),
        'roll':(1,4),
        'in_num':(2,4),
        'in_char':(0,5),
        'out_num':(1,5),
        'out_char':(2,5),
        }

COMMANDS = list(COMMAND_DIFFERENTIALS.keys())

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

COLORIDXS = \
        dict(
                zip(
                    COLORVALS.flatten(),
                    zip(*np.indices(COLORSHAPE).reshape((2,COLORLEN)))
                    ))

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

class Command (object):
    def __init__ (self, name, *args):
        self.name = name
        self.args = args
        self.has_args = True if args else False
        try:
            self.colordiff = COMMAND_DIFFERENTIALS[self.name]
        except KeyError:
            raise RuntimeError('invalid command recieved: %s' % self.name)

    def __repr__ (self):
        return "Command({}, {})".format(self.name, self.args)

    def __str__ (self):
        return str(self.__repr__())

def apply_color_differential (color, colordiff):
    idx = tuple(map(np.mod, COLORIDXS[color]+np.asarray(colordiff), COLORSHAPE))
    color[:] = COLORVALS[idx]
    return color
