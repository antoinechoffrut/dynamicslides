# effect.py
# Th 11 Oct 2018
# Antoine Choffrut
#
# Code for the class 'Effect', which is a subclass of 'Primitive',
# the other (immediate) subclass being 'Graphic'.

from constants import *
from helpers import *
from geometry import col_to_array, wring, translate
from primitive import Primitive
import inspect
import math


# ------------------------------------------------------------------------------------------------------------------------
def initialize_epochs(stage, duration):
    if stage == 'intro':
        return dict({'begin time': 0, 'end time': duration})
    elif stage == 'outro':
        return dict({'begin time': - duration, 'end time': 0})
    else:
        return dict(DEFAULT_EPOCHS)

class Effect(Primitive):
    """Attributes:
    - name
    - masters
    - epochs
    - stage
    """
    def __init__(self, stage = 'intro', pace = 'smooth', duration = DEFAULT_EFFECT_DURATION):
        Primitive.__init__(self)
        self.stage = stage
        self.epochs = initialize_epochs(stage, duration)
        self.pace = pace
            
    # -------------------- BASIC METHODS --------------------
    def get_progress_rate(self, t):
        if self.epochs['end time'] <= self.epochs['begin time']:
            s = 0
        else:
            s = (t - self.epochs['begin time'])/float(self.epochs['end time'] - self.epochs['begin time'])
        s = max(0, min(1, s))
        if self.stage == 'intro':
            s = 1-s
        s = apply_pace(self.pace, s)
        return s

    def initial_filter(self, curve, avatar, t):
        if ((self.epochs['end time'] <= t) and (self.stage == 'intro')) \
           or ((self.epochs['begin time'] >= t) and (self.stage == 'outro')):
            return 0
        if ((self.epochs['begin time'] > t) and (self.stage == 'intro')) \
           or ((self.epochs['end time'] < t) and (self.stage == 'outro')):
            return 1

    # -------------------- METADATA METHODS --------------------
    def main_class_name(self):
        return 'Effect' #, self.__class__.__name__


    # -------------------- FEEDBACK METHODS --------------------
    def print_epochs(self, indent = '', **kwargs):
        indent = indent
        Primitive.print_epochs(self, indent = indent, **kwargs)
        print('')


    def print_report(self, indent = '', **kwargs):
        w = 14 # should be same as Primitive.print_report
        indent = indent
        Primitive.print_report(self, indent = indent, **kwargs)
        print(indent + ' '*2),
        print(str('{0:<' + str(w) + '}').format('stage') + ':'),
        print(' '*2),
        print('{0:<14}'.format(self.stage))


class Fade(Effect):
    """Attributes:
    - masters
    - epochs
    - stage
    - drawing_kit
    - tools
    """
    def __init__(self,
                 stage = 'intro',
                 tools = ['pen', 'brush'],
                 pace = 'linear',
                 drawing_kit = {\
                                'pen color': DEFAULT_BACKGROUND_COLOR,
                                'pen width': 0,
                                'brush color': DEFAULT_BACKGROUND_COLOR
                 },
                 duration = DEFAULT_EFFECT_DURATION
    ):
        Effect.__init__(self, stage = stage, pace = pace, duration = duration)
        self.drawing_kit = dict(drawing_kit)
        self.tools = list(tools)


    def apply_to(self, curve, avatar, t):
        if self.initial_filter(curve, avatar, t) == 0:
            return 
        if self.initial_filter(curve, avatar, t) == 1:
            if 'pen' in self.tools:
                avatar.drawing_kit['pen color'] = None
            if 'brush' in self.tools:
                avatar.drawing_kit['brush color'] = None
            return
        
        s = self.get_progress_rate(t)

        if ('pen' in self.tools)  and (not curve.drawing_kit['pen color'] == None):
            pen_color = interpolate_colors(curve.drawing_kit['pen color'], self.drawing_kit['pen color'], s)
            avatar.drawing_kit['pen color'] = pen_color
        if ('brush' in self.tools) and (not curve.drawing_kit['brush color'] == None):
            brush_color = interpolate_colors(curve.drawing_kit['brush color'], self.drawing_kit['brush color'], s)
            avatar.drawing_kit['brush color'] = brush_color

class Travel(Effect):
    def __init__(self, stage = 'intro', center = ORIGIN, pace = 'smooth', duration = DEFAULT_EFFECT_DURATION):
        Effect.__init__(self, stage = stage, pace = pace, duration = duration)
        self.center = center

    def apply_to(self, curve, avatar, t):
        if self.initial_filter(curve, avatar, t) == 0:
            return 
        if self.initial_filter(curve, avatar, t) == 1:
            avatar.drawing_kit['pen color'] = None
            avatar.drawing_kit['brush color'] = None
            return
        
        s = self.get_progress_rate(t)

        avatar.anchor = interpolate(curve.anchor, self.center, s)



class Zoom(Effect):
    """Attributes:
    - masters
    - epochs
    - stage
    - center
    - scale
    """
    def __init__(self, stage = 'intro', center = ORIGIN, ratio = 1, pace = 'smooth', duration = DEFAULT_EFFECT_DURATION):
        Effect.__init__(self, stage = stage, pace = pace, duration = duration)
        self.center = center
        self.ratio = ratio
        

    def  apply_to(self, curve, avatar, t):
        if self.initial_filter(curve, avatar, t) == 0:
            return 
        if self.initial_filter(curve, avatar, t) == 1:
            avatar.drawing_kit['pen color'] = None
            avatar.drawing_kit['brush color'] = None
            return
        
        s = self.get_progress_rate(t)

        avatar.homothety(center = self.center,
                         sx = interpolate(1, self.ratio, s),
                         sy = interpolate(1, self.ratio, s))

class Spin(Effect):
    """Attributes:
    - masters
    - epochs
    - stage
    - center
    - angle
    """
    def __init__(self, stage = 'intro', center = ORIGIN, angle = 0, pace = 'smooth', duration = DEFAULT_EFFECT_DURATION):
        Effect.__init__(self, stage = stage, pace = pace, duration = duration)
        self.center = center
        self.angle = angle

    def  apply_to(self, curve, avatar, t):
        if self.initial_filter(curve, avatar, t) == 0:
            return 
        if self.initial_filter(curve, avatar, t) == 1:
            avatar.drawing_kit['pen color'] = None
            avatar.drawing_kit['brush color'] = None
            return
        s = self.get_progress_rate(t)
        avatar.rotate(self.center, - self.angle)
        avatar.homothety(center = self.center,
                         sx = 1,
                         sy = math.cos(2*math.pi*(4+0.25)*smooth(s)))
        avatar.rotate(self.center, self.angle)

class Sunrise(Effect):
    """Attributes:
    - masters
    - epochs
    - stage
    - center
    - angle
    """
    def __init__(self, stage = 'intro', center = ORIGIN, angle = 0, pace = 'smooth', duration = DEFAULT_EFFECT_DURATION):
        Effect.__init__(self, stage = stage, pace = pace, duration = duration)
        self.center = center
        self.angle = angle

    def  apply_to(self, curve, avatar, t):
        if self.initial_filter(curve, avatar, t) == 0:
            return 
        if self.initial_filter(curve, avatar, t) == 1:
            avatar.drawing_kit['pen color'] = None
            avatar.drawing_kit['brush color'] = None
            return
        s = self.get_progress_rate(t)
        avatar.rotate(self.center, - self.angle)
        avatar.homothety(center = self.center,
                         sx = 1,
                         sy = smooth(1 - s))
        avatar.rotate(self.center, self.angle)

class Wring(Effect):
    """Attributes:
    - masters
    - epochs
    - stage
    - center
    - amplitude
    """
    def __init__(self,
                 stage = 'intro',
                 center = ORIGIN,
                 amplitude = 1,
                 pace = 'smooth', duration = DEFAULT_EFFECT_DURATION):
        Effect.__init__(self, stage = stage, pace = pace, duration = duration)
        self.center = center
        self.amplitude = amplitude

    def  apply_to(self, curve, avatar, t):
        if self.initial_filter(curve, avatar, t) == 0:
            return 
        if self.initial_filter(curve, avatar, t) == 1:
            avatar.drawing_kit['pen color'] = None
            avatar.drawing_kit['brush color'] = None
            return

        s = self.get_progress_rate(t)

        f = s*NORMAL_NUMBER_OF_CHARACTERS_HORIZONTALLY/(2*W)
        avatar.coords = translate(\
                                  col_to_array(\
                                               2, translate(\
                                                            avatar.coords,
                                                            avatar.anchor),
                                               wring, self.center, self.amplitude, f),
                                  scale(-1, avatar.anchor))
        
        
class Trace(Effect):
    def __init__(self, stage = 'intro', index = 0.5, pace = 'smooth', duration = DEFAULT_EFFECT_DURATION):
        Effect.__init__(self, stage = stage, pace = pace, duration = duration)
        self.index = max(min(index, 1), 0)
    
    def apply_to(self, curve, avatar, t):
        if self.initial_filter(curve, avatar, t) == 0:
            return 
        if self.initial_filter(curve, avatar, t) == 1:
            avatar.drawing_kit['pen color'] = None
            avatar.drawing_kit['brush color'] = None
            return

        if not 'M'+'L'*(len(curve.coords)/2-1) in curve.commands:
            print("WARNING."),
            print("Effect 'Trace' only supported for polygonal curves.")
            return
        else:
            if curve.commands[-1] == 'Z':
                coords = curve.coords + select_point(curve.coords, index = 0)
            else:
                coords = curve.coords
            
            L = len(coords)/2
            commands = 'M' + 'L'*(L - 1)

            s = self.get_progress_rate(t)

            i = self.index*(L-1)
            j = int(i)
            if j == L - 1:
                p = select_point(coords, L - 1)
            else:
                p = interpolate(\
                                select_point(coords, index = j),
                                select_point(coords, index = j + 1),
                                i - j)

            k0 = i-(1-s)*i
            m0 = int(k0)
            if m0 == L-1:
                p0 = select_point(coords, index = m0)
            else:
                p0 = interpolate(\
                                 select_point(coords, index = m0),
                                 select_point(coords, index = m0 + 1),
                                 k0 - m0)
                
            k1 = i+(1-s)*(L-1-i)
            m1 = int(math.ceil(k1))
            if m1 == 0:
                p1 = select_point(coords, index = m1) 
            else:
                p1 = interpolate(\
                                 select_point(coords, index = m1 - 1),
                                 select_point(coords, index = m1),
                                 k1 - m1 +1)
            if m0 == j:
                aux = points_to_tuple(p0, p)
            else:
                aux = p0 + coords[2*(m0 + 1): 2*(j + 1)] + p 
            if j + 1 == m1:
                coords = aux + p1
            else:
                coords = aux + coords[2*(j + 1): 2*m1] + p1

            commands = 'M'+'L'*((j - m0) + (m1 - 1 -j) + 2)

        avatar.coords = coords
        avatar.commands = commands
        avatar.drawing_kit['brush color'] = None

# DISTRIBUTIVE EFFECTS
# These effects are not added to Curve objects.
# They need to be processed by Container objects
# which will decide which (other) effects to add to elements.

class Reveal(Effect):
    def __init__(self,
                 stage = 'intro',
                 tools = ['pen', 'brush'],
                 epochs = DEFAULT_EPOCHS,  
                 order = 'increasing',
                 pace = 'smooth',
                 duration = DEFAULT_EFFECT_DURATION,
                 **kwargs):
        Effect.__init__(self, stage = stage, pace = pace, duration = DEFAULT_EFFECT_DURATION)
        self.epochs = dict(epochs) # <----- THIS OVERRIDE THE EPOCHS SET BY Effect.__init__!!!!
        self.tools = list(tools)
        self.order = order
        self.ordering = self.initialize_ordering(**kwargs)

    def initialize_ordering(self, **kwargs):
        if 'ordering' in kwargs.keys():
            return kwargs['ordering']
        else:
            return None

    def apply_to(self, curve, avatar, t):
        print("WARNING."),
        print("Effect '%s' not supported."%self.__class__.__name__)
        return avatar
# ------------------------------------------------------------        
class ThreeBlueOneBrown(Effect):
    def __init__(self,
                 stage = 'intro',
                 pace = 'smooth',
                 order = 'increasing', duration = DEFAULT_EFFECT_DURATION):
        Effect.__init__(self, stage = stage, pace = pace, duration = duration)
        self.order = order
# ------------------------------------------------------------
class Trickle(Effect):
    def __init__(self,
                 stage = 'intro',
                 separation = (0, -2*H),
                 order = 'increasing',
                 pace = 'smooth', duration = DEFAULT_EFFECT_DURATION):
        Effect.__init__(self, stage = stage, pace = pace, duration = duration)
        self.separation = separation
        self.order = order
    


# ========================================
# TEST
# ========================================

if __name__ == '__main__':


    from curve import Rectangle, Circle
    from camera import Camera
    from monitor import Sketch, Timeline

    import os
    import sys
    import Tkinter
    


    os.system('clear')
    
    print("~"*60)
    print("This is %s." %os.path.basename(sys.argv[0]))
    print("~"*60)

    roottimeline = Tkinter.Tk()
    timeline = Timeline(roottimeline)
    #rootsketch = Tkinter.Tk()
    #sketch = Sketch(rootsketch)
    camera = Camera()





    #rect0 = Rectangle

    circ0 = Circle()
    circ0.record_name()
    circ0.set_brush_color(LIMEGREEN)
    circ0.move_to(CENTER)
    circ0.set_end_time(6*SECONDS)
    circ0.add_effects(Trace())
    effect = Fade(tools = ['brush'])
    effect.delay(3*SECONDS)
    circ0.add_effects(effect)

    circ0.report()
    for effect in circ0.effects:
        effect.report()

    timeline.add_graphics(circ0)
    timeline.refresh()
    camera.add_graphics(circ0)
    camera.roll()


    # ============== END OF SCRIPT ================================
    print("="*80)
    print("END OF SCRIPT.")
    print("="*80)
    roottimeline.mainloop()
    #rootsketch.mainloop()
    # ============================================================
                 
