# geometry.py
# Th 11 Oct 2018
# Antoine Choffrut
#
# Code for global functions performing geometric operations.

import numpy as np
import math
from constants import *
from helpers import *

def get_cardinals(coords):
    """"" 
    Takes: an array with coordinates of points.
    Returns: a dictionary of the cardinal points (nw, w, sw, s, se, e, ne, n, c) of the bounding box corresponding to the points.
    """
    xmin = min(coords[0::2])
    xmax = max(coords[0::2])
    ymin = min(coords[1::2])
    ymax = max(coords[1::2])
    result = {}
    result['nw'] = (xmin, ymin)
    result['sw'] = (xmin, ymax)
    result['se'] = (xmax, ymax)
    result['ne'] = (xmax, ymin)
    result['w'] = interpolate(result['nw'], result['sw'], 0.5)
    result['e'] = interpolate(result['ne'], result['se'], 0.5)
    result['n'] = interpolate(result['nw'], result['ne'], 0.5)
    result['s'] = interpolate(result['sw'], result['se'], 0.5)
    result['c'] = interpolate(result['n'], result['s'], 0.5)
    return result

def affine_transformation(p, origin1, origin2, t):
    dimension = len(t[0])
    P = tuple_to_array(p, dimension = dimension)
    O1 = tuple_to_array(origin1, dimension = dimension)
    O2 = tuple_to_array(origin2, dimension = dimension)
    O1 = tuple_to_array(origin1, dimension = dimension)
    T = tuple_to_matrix(t)
    aux = O2+np.dot(T, P-O1)
    return array_to_tuple(aux)

def  translate(points, vector):
    """ 
    - Input 'points' is a tuple containing coordinates of points.
    - Input 'vector' is a tuple containing coordinates of one vector.
    """
    if not len(points) % len(vector) == 0:
        print("WARNING."),
        print("Dimension of translation vector does not match that of points to be translated.")
        return points
    V = vector*(len(points)/len(vector))
    return add(points, V)
                  

def rotate(p, center, angle):
    R = np.array([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
    r = matrix_to_tuple(R)
    result = affine_transformation(p, center, center, r)
    return result

def homothety(p, center, sx, sy):
    t = ((sx, 0), (0, sy))
    result = affine_transformation(p, center, center, t)
    return result

def wring(p, c, a, f):
    return p[0], c[1]+a*(p[1]-c[1])*math.cos(2*math.pi*(p[0]-c[0])*f)

def corrugate(p, center = ORIGIN):
    n = 12
    amp = 0.2
    sx = 1 + amp*math.cos(n*np.arctan2(p[1] -center[1], p[0] - center[0]))
    sy = sx
    return homothety(p, center, sx, sy)


def col_to_array(dimension, atuple, function, *args, **kwargs):
    if not len(atuple) % dimension == 0:
        print("ERROR (global function 'col_to_array')."),
        print("Input argument does not have the correct length.")
        return
    n = len(atuple)/dimension
    result = flatten([function(atuple[i*dimension: (i + 1)*dimension], *args, **kwargs) for i in range(n)])
    return result


def get_angle_on_curve(atuple, s):
    """ Input 'atuple' is a tuple consisting of the (x,y)-coordinates of points making up a curve. """
    # SHOULD REDO THIS - REFORMAT ARRAYS INTO TUPLES
    coords = tuple_to_array(atuple)
    result = None

    if coords.shape[1]>0:
        i = int(s*(coords.shape[1]-1))
    else:
        i=0

    j = i
    search = True
    while (j > 0) and search:
        if np.linalg.norm(coords[:,j] - coords[:,i]) < TOL_XY:
            j -= 1
        else:
            search = False

    k = i
    search = True
    while (k < coords.shape[1]-1) and search:
        if np.linalg.norm(coords[:,k] - coords[:,i]) < TOL_XY:
            k += 1
        else:
            search = False

    if np.linalg.norm(coords[:,j] - coords[:,k]) < TOL_XY:
        result = None
    else:
        result = np.arctan2(coords[1,k]-coords[1,j], coords[0,k]-coords[0,j])
        
    return result


if __name__ == '__main__':



    corrugate((1,1))
