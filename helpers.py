# helpers.py
# Th 11 Oct 2018
# Antoine Choffrut
#
# Code for global functions with general use.

from constants import *
import inspect
import numpy as np
import os
import time

def in_seconds(t):
    return '{:.2f}'.format(t/float(SECONDS))

def sigmoid(x):
    return 1.0/(1 + np.exp(-x))

def smooth(t, inflection = 10.0):
    error = sigmoid(-inflection / 2)
    return (sigmoid(inflection*(t - 0.5)) - error) / (1 - 2*error)

def soft_landing(x, inflection = 10.0): # 10.0 soft but quick
    return np.exp(inflection*(x-1))

def surprise(x, inflection = 10.0):
    return 1 - np.exp(-inflection*x)

def smooth_plateau(x):
    if x < 0.25:
        result = smooth(x)
    elif x > 0.75:
        result = smooth(1-x)
    else:
        result = 1
    return result

def apply_pace(pace, s):
    result = s
    if pace == 'linear':
        result = s
    elif pace == 'smooth':
        return smooth(s)
    elif pace == 'soft landing':
        return soft_landing(s)
    elif pace == 'surprise':
        return surprise(s)
    else:
        pass
    return result



def add(in1, in2):
    """ Assumes inputs 'in1' and 'in2' are tuples, returns a tuple which addes inputs entrywise. """
    if len(in1) < len(in2):
        print("WARNING (global function 'add'). Input 2, %s,  is longer (%s) than input 1%s (%s), has been truncated ."%(id(in2), len(in2), id(in1), len(in1)))
        in2 = in2[0:len(in1)]
    elif len(in1) > len(in2):
        print("WARNING (global function 'add'). Input 1 id %s is longer (%s) than id %s (%s), has been truncated ."%(id(in1), len(in1), id(in2), len(in2)))
        in1 = in1[0:len(in2)]
    return tuple(in1[i] + in2[i] for i in range(len(in1)))

def subtract(in1, in2):
    """ Assumes inputs 'in1' and 'in2' are tuples, returns a tuple which addes inputs entrywise. """
    if len(in1) < len(in2):
        print("WARNING (global function 'subtract'). Input 2 id %s is longer (%s) than id %s (%s), has been truncated ."%(id(in2), len(in2), id(in1), len(in1)))
        in2 = in2[0:len(in1)]
    elif len(in1) > len(in2):
        print("WARNING (global function 'subtract'). Input 1 id %s is longer (%s) than id %s (%s), has been truncated ."%(id(in1), len(in1), id(in2), len(in2)))
        in1 = in1[0:len(in2)]
    return tuple(in1[i] - in2[i] for i in range(len(in1)))
                  

def scale(s, in1):
    """ Scales input 'in1' by factor 's'. Assumes in1 is a tuple, returns a tuple."""
    if hasattr(in1, '__iter__'):
        return tuple(s*i for i in in1)
    else:
        return s*in1


def interpolate(in1, in2, s):
    """ Assumes inputs 'in1' and 'in2' are tuples, returns a tuple. """
    if hasattr(in1, '__iter__') and hasattr(in2, '__iter__'):
        if not len(in1) == len(in2):
            print("WARNING.  Inputs to global function 'interpolate' should have same lengths, returning the first argument.")
            return in1
        else:
            return add(scale(1-s, in1), scale(s, in2))
    else:
        return (1-s)*in1 + s*in2

def interpolate_colors(color1, color2, s):
    return tuple(int(i) for i in interpolate(color1, color2, s))

def select_point(atuple, index, dimension = 2):
    if not len(atuple) % dimension == 0:
        print("ERROR."),
        print("Input has incorrect length: should contain coordinates of points of dimension %s."%dimension)
    index = index % (len(atuple)/dimension)
    return atuple[index*dimension: index*dimension+dimension]
    
def tuple_to_array(atuple, dimension = 2):
    """Assumes input 'atuble' is a list of (x,y)-coordinates: x0, y0, x1, y1, ... x(n-1), y(n-1).
    Returns a (2, n)-matrix where columns represent points/vectors with coordinates (x(i), y(i)).
    Similarly if the dimension is specified to a value different from 2.
    """
    return np.array(atuple).reshape((dimension, len(atuple)/dimension), order = 'F')

def  array_to_tuple(arr):
    """Assumes 'points' is a two-dimensional array (i.e. a 'matrix'). """
    return tuple(arr[j][i] for i in range(arr.shape[1]) for j in range(arr.shape[0]))
    
def points_to_tuple(*args):
    """ Input consists of tuples (representing coordinates of points), 
    returns a single tuple of type 'xy'. 
    """
    return tuple(args[i][j] for i in range(len(args)) for j in range(len(args[i])))
    
def flatten(args):
    """ Input is a tuple of tuples, returns a single tuple. """
    return tuple(args[i][j] for i in range(len(args)) for j in range(len(args[i])))
    
def tuple_to_matrix(t):
    """ Input 't' is a tuple containing the images of the basis vectors under a linear transformation.
    Returns the matrix representing this transformation as a numpy array. 
    """
    return tuple_to_array(flatten(t))

def matrix_to_tuple(T):
    return tuple(tuple(T[i][j] for i in range(T.shape[0])) for j in range(T.shape[1]))
    
def x_and_y_to_xy(x, y):
    """ Inputs 'x' and 'y' are tuples of same length.
    Returns xy = x0, y0, x1, y1, ... """
    return flatten(zip(x,y))
    




def find_name(obj, D_objs):
    obj_names_to_id = {key: str(id(D_objs[key]))
                        for key in D_objs.keys()}
    id_to_obj_names = {item: key for key, item in obj_names_to_id.iteritems()}
    if obj in D_objs.values():
        return id_to_obj_names[str(id(obj))]
    else:
        return '[no name]'


def get_null():
    if os.name == "nt":
        return "NUL"
    return "/dev/null"

def generate_tex_file(expression):
    """Generate tex file from expression"""
    result = os.path.join(TEX_DIR_PATH, str(hash(expression))) + '.tex'

    if not os.path.exists(TEX_DIR_PATH):
        os.mkdir(TEX_DIR_PATH)
        print("Subdirectory '%s' did not exist, has been created." % TEX_DIR_NAME)
    else:
        pass


    tex_hack =  '\n'.join(['\setlength{\unitlength}{1ex}%',
                            '\\begin{picture}(0,1)',
                            '\\put(0,0){\\line(0,1){1}}',
                            '\\end{picture}%',
                            '\\hspace{-0.75pt}%'])
    with open(TEMPLATE_LATEX_FILE_PATH, 'r') as infile:
        body = infile.read()
        body = body.replace(TEX_TEXT_TO_REPLACE, '\n'.join([tex_hack, expression]))
    
    with open (result, 'w') as outfile:
        outfile.write(body)

    return result
    
def tex_to_dvi(tex_file):
    """Run .tex file and return name of .dvi file"""
    result = tex_file.replace('.tex', '.dvi')
    commands = [
        "latex",
        "-interaction=batchmode",
        "-halt-on-error",
        "-output-directory=" + TEX_DIR_PATH,
        tex_file,
        "> ",
        get_null()]

    exit_code = os.system(" ".join(commands))
    if exit_code !=0:
        print("Latex error.")
    else:
        pass
    return result 

def dvi_to_svg(dvi_file):
    """Convert .dvi file to .svg file"""
    result = dvi_file.replace(".dvi", ".svg")
    commands = [
        "dvisvgm",
        dvi_file,
        "-n", # for 'no fonts', get path instead
        "-v",
        "0", # 0 = no message output at all
        "-o",
        result,
        ">",
        get_null()
    ]
    os.system(" ".join(commands))
    return result


if __name__ == '__main__':



    pass
