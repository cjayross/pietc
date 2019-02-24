import numpy as np
import random
from PIL import Image

# list of value, command
__all__ = ['commands', 'colors']

# darkness, hue
commands = {'push':(1,0), 'pop':(2,0),
            'add':(0,1), 'subtract':(1,1), 'multiply':(2,1),
            'divide':(0,2), 'mod':(1,2), 'invert':(2,2),
            'greater':(0,3),'pointer':(1,3),'switch':(2,3),
            'duplicate':(0,4),'roll':(1,4),'in_num':(2,4),
            'in_char':(0,5),'out_num':(1,5),'out_char':(2,5)}

colors = [  ["FFC0C0", "FF0000","C00000"],
            ["FFFFC0", "FFFF00","C0C000"],
            ["C0FFC0", "00FF00","00C000"],
            ["C0FFFF", "00FFFF","00C0C0"],
            ["C0C0FF", "0000FF","0000C0"],
            ["FFC0FF", "FF00FF","C000C0"],
            ["FFFFFF", "000000"]]

def hexrgb(hex):
    return list(int(hex[i:i+2], 16) for i in (0, 2 ,4))

colors = [list(map(hexrgb,x)) for x in colors]

random.seed()

test_commands = [['push',4],['push',2],['divide',0],['out_num',0]]

image = np.full((1,1,3),0,dtype=int)

color_indices = [random.randrange(6),random.randrange(3)]
color = colors[color_indices[0]][color_indices[1]]
image[0][0] = color
for x in test_commands:
    color_indices[0] = (color_indices[0] + commands[x[0]][1]) % 6
    color_indices[1] = (color_indices[1] + commands[x[0]][0]) % 3
    color = colors[color_indices[0]][color_indices[1]]
    if x[0] == 'push':
        length = x[1] # height of line codel
    else:
        length = 1

    diff = length - image.shape[1]
    if diff > 0:
        #expand the image
        y = np.full((image.shape[0],length,3),0,int)
        y[:image.shape[0],:image.shape[1]] = image
        image = y
    z = np.full((image.shape[0]+1,image.shape[1]),color,dtype=(int,3))
    z[:,length:] = [0,0,0]
    z[:image.shape[0],:image.shape[1]] = image
    image = z

y = np.full((image.shape[0]+4,max(image.shape[1],3),3),0,int)
y[:image.shape[0],:image.shape[1]] = image
y[image.shape[0]:image.shape[0]+3,0] = colors[6][0]
y[image.shape[0]+2,1] = colors[6][0]
y[image.shape[0]+1:image.shape[0]+4,2] = colors[random.randrange(6)][random.randrange(3)]
image = y


img = Image.new('RGB',(image.shape[0],image.shape[1]),'black')
pixels = img.load()

for i in range(img.size[0]):
    for j in range(img.size[1]):
        pixels[i,j] = tuple(image[i,j])

# img.show()

img.save('out.png')
