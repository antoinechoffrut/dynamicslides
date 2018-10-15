# constants.py
# Th 11 Oct 2018
# Antoine Choffrut
#
# This file contains the global constants to create videos/animations,
# with the exception of the color constants which are in colors.py.


import numpy as np
import os
from colors import *

F_RATE = 24 # 8 # 24 # 60
SECONDS = F_RATE

W = 1920 # width of 'canvas'
H = 1080 # height of 'canvas'

ARROW_WIDTH = W/120
ARROW_HEIGHT = ARROW_WIDTH/2

ORIGIN = (0, 0)

CENTER = (W/2, H/2)
NW_CORNER = (0, 0)
SW_CORNER = (0, H)
SE_CORNER = (W, H)
NE_CORNER = (W, 0)
WEST_POINT = (0, H/2)
EAST_POINT = (W, H/2)
NORTH_POINT = (W/2, 0)
SOUTH_POINT = (W/2, H)

#ONE_EX_PT = 4.30554 # 1ex = 4.30554pt is roughly the height of an 'x'
ONE_EM_PT = 10.00002 # 1em = 10.00002pt is roughly the width of an 'M'
NORMAL_NUMBER_OF_CHARACTERS_HORIZONTALLY = 30
ONE_EM = int(W/NORMAL_NUMBER_OF_CHARACTERS_HORIZONTALLY)
NORMAL_TEXT_SCALE = int(W/(ONE_EM_PT*NORMAL_NUMBER_OF_CHARACTERS_HORIZONTALLY))

TOL_XY = 0.5 # some numerical tolerance to decide whether two arrays represent same point on canvas


CARDINAL_TAGS = ('nw','w','sw','s','se','e','ne','n','c')
DEFAULT_CARDINALS = {key: ORIGIN for key in CARDINAL_TAGS}
DEFAULT_COORDS = NW_CORNER + SW_CORNER + SE_CORNER + NE_CORNER
DEFAULT_COMMANDS = 'MLLLZ'

TEMPLATE_LATEX_FILE = 'latex_template.tex'
TEMPLATE_LATEX_FILE_PATH = os.path.join(os.getcwd(), TEMPLATE_LATEX_FILE)

TEX_DIR_NAME = 'latex-output'
TEX_DIR_PATH = os.path.join(os.getcwd(),TEX_DIR_NAME)

TEX_TEXT_TO_REPLACE = 'YourTextHere'

MONTHS = ('January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December')

#-------------------- DEFAULT VALUES
DEFAULT_BACKGROUND_COLOR = BLACK
DEFAULT_PEN_COLOR = WHITE
DEFAULT_PEN_WIDTH = 2
DEFAULT_BRUSH_COLOR = WHITE

DEFAULT_DRAWING_KIT = {'pen color': DEFAULT_PEN_COLOR,'pen width': 1,'brush color': None}
DEFAULT_TIMELINE_ELEMENT_SEGMENT_DRAWING_KIT = {'pen color': BLACK, 'pen width': 1, 'brush color': None}
DEFAULT_TIMELINE_ELEMENT_LABEL_DRAWING_KIT = {'pen color': BLACK, 'pen width': 1, 'brush color': BLUE}
DEFAULT_TIMELINE_EFFECT_SEGMENT_DRAWING_KIT = {'pen color': RED1, 'pen width': 5, 'brush color': None}
DEFAULT_TIMELINE_EFFECT_LABEL_DRAWING_KIT = {'pen color': RED1, 'pen width': 1, 'brush color': None}

DEFAULT_PAUSE = 2*SECONDS
DEFAULT_EFFECT_DURATION = 2*SECONDS 
DEFAULT_EPOCHS = {'begin time': 0*SECONDS, 'end time': DEFAULT_EFFECT_DURATION}
DEFAULT_TITLE_DURATION = 5*SECONDS

