import numpy as np
import random
import itertools
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

"""
command structure:
    each layer contains dicts and lists
    dict means either a while loop (really a do while loop) or if elif else statement
        - first input is a comparison command, greater than or not for now
        - rest are commands, need to make sure the two things to compare end up on top
    list means a basic command

takes the command structure and build a list of commands
"""

# test_commands = [["push",2],
#                 ["out_num",0],
#                 ["push",10],
#                 ["out_char",0]]

test_commands = [
                ["push",4],
                ["push",1],
                ["while",0],
                ["greater",0],
                ["end_cond",0],
                ["push",2],
                ["add",0],
                ["duplicate",0],
                ["out_num",0],
                ["push",32],
                ["out_char",0],
                ["copy2",0],
                ["end_while",0]
                ]

# test_commands = [
#                 ["push",4],
#                 ["push",2],
#                 ["if",0],
#                 ["mod",0],
#                 ["invert",0],
#                 ["end_cond",0],
#                 ["print_string", "4 is divisible by 2"],
#                 ["end_if",0]
#                 ]

# test_commands = [['push',18],['push',2],['divide',0],['out_num',0]]

color_indices = [random.randrange(6),random.randrange(3)]
color = colors[color_indices[0]][color_indices[1]]

def command_image(command_list):
    global color
    image = np.full((0,0,3),0,dtype=int)
    # image[1][0] = colors[6][0]

    for i,x in enumerate(command_list):
        length = 1
        if x[0] == 'push':
            length = x[1] # height of line codel
            #! add negative numbers
            # flatten large numbers
            if length > 16:
                # replace with sequence
                q = int(length / 16)
                r = length % 16
                if q > 16:
                    raise RuntimeError('number is too big')
                if q != 0:
                    command_list.insert(i+1,['push',16])
                    command_list.insert(i+2,['push',q])
                    command_list.insert(i+3,['multiply',0])
                    if r != 0:
                        command_list.insert(i+4,['push',r])
                        command_list.insert(i+5,['add',0])
                else:
                    raise RuntimeError("number isn't actually too big")
                continue
        #custom functions
        elif x[0] == 'copy2':
            command_list.insert(i+1,['duplicate',0])
            command_list.insert(i+2,['push',3])
            command_list.insert(i+3,['push',2])
            command_list.insert(i+4,['roll',0])
            command_list.insert(i+5,['duplicate',0])
            command_list.insert(i+6,['push',4])
            command_list.insert(i+7,['push',1])
            command_list.insert(i+8,['roll',0])
            command_list.insert(i+9,['push',2])
            command_list.insert(i+10,['push',1])
            command_list.insert(i+11,['roll',0])
            continue
        elif x[0] == 'print_string':
            if isinstance(x[1],str):
                j=1
                for i,s in enumerate(x[1]):
                    command_list.insert(i+j,['push',ord(s)])
                    command_list.insert(i+j+1,['out_char',0])
                    j+=2
            else:
                print("not a string")
            continue


        diff = length - image.shape[1]
        if diff > 0:
            #expand the image
            y = np.full((image.shape[0],length,3),0,dtype=int)
            y[:image.shape[0],:image.shape[1]] = image
            image = y
        z = np.full((image.shape[0]+1,image.shape[1]),color,dtype=(int,3))
        z[:,length:] = [0,0,0]
        z[:image.shape[0],:image.shape[1]] = image
        image = z

        color_indices[0] = (color_indices[0] + commands[x[0]][1]) % 6
        color_indices[1] = (color_indices[1] + commands[x[0]][0]) % 3
        color = colors[color_indices[0]][color_indices[1]]


    y = np.full((image.shape[0]+1,max(image.shape[1],3),3),0,int)
    y[:image.shape[0],:image.shape[1]] = image
    y[image.shape[0],0] = color
    return y

def extend_black(image, size):
    if size == image.shape[0]:
        return image
    y = np.full((image.shape[0],size,3),0,int)
    y[:image.shape[0],:image.shape[1]] = image
    return y

def concatenate_images(program):
    img = np.full((0,0,3),0,dtype=int)
    tmp_list = []
    in_block = False# need something that accommodates nested blocks
    for i,x in enumerate(program):
        if x[0] != "while" and x[0] != "if" and not in_block:
            tmp_list.append(x)
        elif x[0] == "while":
            if len(tmp_list) > 0:
                img1 = command_image(tmp_list)
                img1 = extend_black(img1, max(img1.shape[1],img.shape[1]))
                img = extend_black(img, max(img1.shape[1],img.shape[1]))
                img = np.concatenate((img,img1),axis=0)
                tmp_list = []
            in_block = True

            condition_program = list(itertools.takewhile(lambda x: x[0] != "end_cond",program[i+1:]))
            j = i + len(condition_program)
            block_program = list(itertools.takewhile(lambda x: x[0] != "end_while",program[j+2:]))

            #take block program and add another column on the right, with one white dot at the top
            img1 = concatenate_images(block_program)
            y = np.full((img1.shape[0]+1,img1.shape[1],3),0,int)
            y[:img1.shape[0],:img1.shape[1]] = img1
            while_img = y
            while_img[img1.shape[0],0] = colors[6][0]

            #add condition part to the block program
            img1 = concatenate_images(condition_program)
            img1 = extend_black(img1, max(img1.shape[1],while_img.shape[1]))
            while_img = extend_black(while_img, max(img1.shape[1],while_img.shape[1]))
            while_img = np.concatenate((while_img, img1),axis=0)

            #create white border around everything
            y = np.full((while_img.shape[0]+2,while_img.shape[1]+1),colors[6][0],dtype=(int,3))
            y[1:while_img.shape[0]+1,:while_img.shape[1]] = while_img
            while_img = y

            #create branch
            color_indices[0] = (color_indices[0] + commands["pointer"][1]) % 6
            color_indices[1] = (color_indices[1] + commands["pointer"][0]) % 3
            color = colors[color_indices[0]][color_indices[1]]

            while_img[-1,0] = color

            img1 = extend_black(while_img, max(while_img.shape[1],img.shape[1]))
            img = extend_black(img, max(while_img.shape[1],img.shape[1]))
            img = np.concatenate((img, img1),axis=0)
        elif x[0] == "if":
            if len(tmp_list) > 0:
                img1 = command_image(tmp_list)
                img1 = extend_black(img1, max(img1.shape[1],img.shape[1]))
                img = extend_black(img, max(img1.shape[1],img.shape[1]))
                img = np.concatenate((img,img1),axis=0)
                tmp_list = []
            in_block = True

            condition_program = list(itertools.takewhile(lambda x: x[0] != "end_cond",program[i+1:]))
            j = i + len(condition_program)
            block_program = list(itertools.takewhile(lambda x: x[0] != "end_if",program[j+2:]))

            #make it so it separates each while and if statement on its own level
            img1 = concatenate_images(condition_program)
            img1 = extend_black(img1,max(img1.shape[1],img.shape[1],17))
            img  = extend_black(img,max(img1.shape[1],img.shape[1],17))

            #create branch
            color_indices[0] = (color_indices[0] + commands["pointer"][1]) % 6
            color_indices[1] = (color_indices[1] + commands["pointer"][0]) % 3
            color = colors[color_indices[0]][color_indices[1]]

            y = np.full((img.shape[0]+1,img.shape[1]),colors[6][0],dtype=(int,3))
            y[:img.shape[0]] = img
            img = y
            img[-1,0] = color

            block_img = concatenate_images(block_program)
            block_img = extend_black(block_img,19)
            y = np.full((block_img.shape[0]+1,block_img.shape[1],3),0,int)
            y[1:block_img.shape[0]+1] = block_img
            y[0,0] = colors[6][0]
            block_img = y

            y = np.full((block_img.shape[0]+2,block_img.shape[1]+1),colors[6][0],dtype=(int,3))
            y[1:block_img.shape[0]+1,:block_img.shape[1]] = block_img
            block_img = y
            block_img = numpy.rot90(block_img,3,(0,1))
            

            # if img.shape[0] < 20:
                #assume img.shape[0] > 1
                # y = np.full((20,img.shape[1]+))




    if len(tmp_list) > 0:
        img1 = command_image(tmp_list)
        img1 = extend_black(img1, max(img1.shape[1],img.shape[1]))
        img = extend_black(img, max(img1.shape[1],img.shape[1]))
        img = np.concatenate((img,img1),axis=0)
    return img




image = concatenate_images(test_commands)

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

img.save('../test/out.png')