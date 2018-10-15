# curve.py
# Th 11 Oct 2018
# Antoine Choffrut
#
# Code for the class 'Curve', which is a subclass of 'Graphic'.

from constants import *
from helpers import *
from geometry import *
from primitive import Primitive, filter_by_class, fit_within_epochs
from graphic import Graphic, print_geometry
import math
import inspect
import copy
import aggdraw

def draw(anchor, commands, coords, canvas, pen, brush=None):
    aggdraw_path_string = get_aggdraw_path_string(commands, coords)
    symbol = aggdraw.Symbol(aggdraw_path_string)
    if brush == None:
        canvas.symbol(anchor, symbol, pen)
    else:
        canvas.symbol(anchor, symbol, pen, brush)

def get_aggdraw_path_string(commands, coords):
    result = ''
    aux = coords
    i = 0
    if len(coords)/2 == 1:
        result = 'M'+str(aux[0])+','+str(aux[1])
    else:
        for command in commands:
            result += command
            if command == 'Z':
                result += ' '
            elif command in 'ML':
                result += str(aux[i])+','+str(aux[i+1])+' '
                i += 2
            elif command in 'SQ':
                result += str(aux[i])+','+str(aux[i+1])+' '+str(aux[i+2])+','+str(aux[i+3])+' '
                i += 4
            elif command == 'C':
                result += str(aux[i])+','+str(aux[i+1])+' '+str(aux[i+2])+','+str(aux[i+3])+' '+str(aux[i+4])+','+str(aux[i+5])+' '
                i += 6
            else:
                pass
    return result

def d_to_coords_and_commands(string):
    """Takes:
        string = the 'd' attribute of a path element from an .svg file
    and returns tuple 'commands, coords' where:
        1) commands =  a string containing the commands ('M', 'L', 'C', 'S', 'Q', 'Z') where 'H' and 'V' commands have been converted to 'L' commands;
        2) coords = a list of coordinates of the control points (in float format).
    """
    aux = string
    i = len(string)-1
    while i>0:
        if string[i] in  'MLHVCSQZ':
            aux = aux[:i]+'|'+aux[i:]
        elif string[i] in 'TAmlhvcsqzta':
            print("Warning: command '%s' not supported!" % string[i])
        else:
            pass
        i -= 1
    aux = aux.split('|')
    for i in range(len(aux)):
        aux[i] = [aux[i][0], aux[i][1:]]
        aux[i][1] = aux[i][1].split()
    for i in range(0,len(aux)):
        if aux[i][0][0] == 'Z':
            x,y = [None,None] # But don't assign these inside aux!  Just for monitoring...
        elif aux[i][0][0] == 'H':
            x = aux[i][1][0]
            aux[i][1] = [x,y]
            aux[i][0] = 'L'
        elif aux[i][0][0] == 'V':
            y = aux[i][1][0]
            aux[i][1] = [x,y]
            aux[i][0] = 'L'
        else:
            x,y = aux[i][1][-2:]
    commands = [item[0] for item in aux]
    commands = ''.join(commands)
    coords = [item[1] for item in aux]
    coords = [float(coord) for item in coords for coord in item]
    coords = np.array(coords)
    coords = coords.reshape((2,int(len(coords)/2)),order = 'F')
    return coords, commands



class PostponeTimeUpdatingToEnd(object):
    def __init__(self, curve):
        self.curve = curve
        self.old_curve_times = tuple(curve.epochs.values())

    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        if self.curve.external_call == False:
            self.curve.update_epochs()
            self.curve.update_effects(self.old_curve_times)
        return self

class PostponeGeometricUpdatingToEnd(object):
    def __init__(self, curve):
        self.curve = curve

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        if self.curve.external_call == False:
            Graphic.update_cardinals(self.curve)
        return self


class Curve(Graphic):
    """ Attributes:
    - name
    - masters
    - epochs
    - external_call
    - anchor
    - cardinals
    - coords
    - commands
    - drawing_kit
    - decoration
    - effects
    """
    def __init__(self, anchor = ORIGIN, coords = DEFAULT_COORDS, commands = DEFAULT_COMMANDS):
        self.coords = coords
        self.cardinals = get_cardinals(self.coords)
        Graphic.__init__(self, anchor, self.cardinals)
        self.commands = self.initialize_commands(commands)
        self.drawing_kit = dict(DEFAULT_DRAWING_KIT)
        self.decoration = []
        self.effects = []

    def initialize_commands(self, commands):
        if commands[-1] == 'Z':
            Z = 'Z'
        else:
            Z = ''
        n = commands.count('M') \
            + commands.count('L') \
            + 2*commands.count('Q') \
            + 2*commands.count('S') \
            + 3* commands.count('C')

        if n > len(self.coords)/2:
            print("WARNING (id %s)."%id(self)),
            print("Argument 'commands' ('%s') too long, has been truncated."%commands)
            return commands[0: len(self.coords)/2]
        elif n < len(self.coords)/2:
            print("WARNING (id %s)."%id(self)),
            print("Argument 'commands' ('%s') too short, has been filled with 'L'."%commands)
            return commands.replace('Z', '') + 'L'*(len(self.coords)/2 - len(commands.replace('Z','')))
        else:
            return commands
            

    # -------------------- BASIC METHODS --------------------

    def close(self):
        """ Closes the curve if not already closed. """
        if not self.commands[-1] == 'Z':
            self.commands = self.commands + 'Z'

    def unclose(self):
        """ Un-closes the curve if it is closed. """
        if self.commands[-1] == 'Z':
            self.commands = self.commands[0:-1]
        
    def points(self):
        """ Returns a tuple containing the *absolute* coordinates of the points in coords. """
        return translate(self.coords, self.anchor)

    def point(self, s):
        """ Returns the point at "time" s along the curve.  
        Then endpoints on the curve correspond to s = 0 and s = 1. 
        """
        i = 0.5*s*(len(self.coords) - 2)
        j = int(math.floor(i))
        r = i - math.floor(i)
        p0 = self.coords[2*j], self.coords[2*j + 1]
        if 2*j < len(self.coords) - 2:
            p1 = self.coords[2*j + 2], self.coords[2*j + 3]
        else:
            p1 = self.coords[-2], self.coords[-1]
        return interpolate(p0, p1, r)

    def main_class_name(self):
        return 'Curve'


    def add_decoration(self, *args):
        """ item is a list of dictionaries, each containing
        - position of decoration ('foot' or 'tip')
        - type of decoration ('point', 'tick', 'arrow')
        """
        self.decoration = self.decoration + [dict(arg) for arg in args]

    def set_drawing_kit(self, drawing_kit):
        self.drawing_kit = dict(drawing_kit)
            
    def set_pen_color(self, pen_color):
        self.drawing_kit['pen color'] = pen_color
            
    def set_pen_width(self, pen_width):
        self.drawing_kit['pen width'] = pen_width

    def set_brush_color(self, brush_color):
        self.drawing_kit['brush color'] = brush_color

    def add_effects(self, *effects):
        for effect in effects:
            effect_copy = copy.deepcopy(effect)
            effect_copy.masters = [self]
            self.effects.append(effect_copy)
            self.synchronize_effect(effect_copy)

    def synchronize_effect(self, effect):
        dt = effect.epochs['end time'] - effect.epochs['begin time']
        if effect.stage == 'intro':
            effect.epochs['begin time'] = fit_within_epochs(effect.epochs['begin time'] + self.epochs['begin time'], self)
            effect.epochs['end time'] = fit_within_epochs(effect.epochs['begin time'] + dt, self)
        elif effect.stage == 'outro':
            effect.epochs['end time'] = fit_within_epochs(self.epochs['end time'] + effect.epochs['end time'], self)
            effect.epochs['begin time'] = fit_within_epochs(effect.epochs['end time'] - dt, self)
        
    def update_effects(self, old_times):
        times = list(self.epochs.values())
        for effect in self.effects:
            dt = effect.epochs['end time'] - effect.epochs['begin time']
            if effect.stage == 'intro':
                dt_begin = effect.epochs['begin time'] - old_times[0]
                effect.epochs['begin time'] = fit_within_epochs(times[0] + dt_begin, self)
                effect.epochs['end time'] = fit_within_epochs(times[0] + dt_begin + dt, self)
            elif effect.stage == 'outro':
                dt_end = effect.epochs['end time'] - old_times[1]
                effect.epochs['end time'] = max(times[1] + dt_end, self.epochs['begin time'])
                effect.epochs['begin time'] = max(times[1] + dt_end - dt, self.epochs['begin time'])

    # -------------------- GEOMETRIC METHODS --------------------
    def foot(self):
        """ Returns the absolute coordinates of the first point on the curve. """
        return translate(self.anchor, (self.coords[0], self.coords[1]))

    def tip(self):
        """ Returns the absolute coordinates of the last point on the curve. """
        return translate(self.anchor, (self.coords[-2], self.coords[-1]))
    
    def change_anchor_to(self, new_anchor):
        self.coords = translate(self.coords, subtract(self.anchor, new_anchor))
        Graphic.change_anchor_to(self, new_anchor)

    def translate(self,v):
        with PostponeGeometricUpdatingToEnd(self):
            Graphic.translate(self, v)

    def homothety(self, center, sx, sy):
        with PostponeGeometricUpdatingToEnd(self):
            self.coords = homothety(self.coords, ORIGIN, sx, sy)
            Graphic.homothety(self, center, sx, sy)
    
    def rotate(self, center, angle):
        with PostponeGeometricUpdatingToEnd(self):
            self.coords = rotate(self.coords, ORIGIN, angle)
            Graphic.rotate(self, center, angle)
    
    def move_to(self,p):
        with PostponeGeometricUpdatingToEnd(self):
            Graphic.move_to(self, p)

    def corrugate(self, center):
        with PostponeGeometricUpdatingToEnd(self):
            self.coords = col_to_array(2, self.coords, corrugate, ORIGIN)
            Graphic.corrugate(self, center)

    # -------------------- DRAWING METHODS --------------------
    def draw(self, canvas, *t):
        if len(t) == 0:
            pen = aggdraw.Pen(self.drawing_kit['pen color'], self.drawing_kit['pen width'])
            if self.drawing_kit['brush color'] ==  None:
                brush = None
            else:
                brush = aggdraw.Brush(self.drawing_kit['brush color'])
            draw(self.anchor, self.commands, self.coords, canvas, pen, brush)
            self.draw_decoration(canvas)
            return
        else:
            t = t[0] # unpacking gives a list, which should be a single integer.

        if (t < self.epochs['begin time']) or (t >= self.epochs['end time']):
            pass
        else:
            avatar = self.update_avatar(t)
            avatar.decoration = self.decoration
            if not avatar == None:
                avatar.draw(canvas)
    
    def draw_decoration(self, canvas):
        for D in self.decoration:
            if D['type']  == 'point':
                decoration = self.create_point(D['position'])
            elif D['type'] == 'tick':
                decoration = self.create_tick(D['position'])
            elif D['type'] == 'arrow':
                if 'style' in D.keys():
                    decoration = self.create_arrow(D['position'], D['style'])
                else:
                    decoration = self.create_arrow(D['position'])
            else:
                decoration = None
            if not decoration == None:
                decoration.draw(canvas)
    
    def create_point(self, position):
        if position == 'tip':
            center = self.tip()
        elif position == 'foot':
            center = self.foot()
        result = Point(center = center, radius = 5)
        result.set_pen_color(self.drawing_kit['pen color'])
        result.set_brush_color(self.drawing_kit['pen color'])
        return result
    
    
    def create_tick(self, position):
        if position == 'tip':
            index = -1
            angle = get_angle_on_curve(self.coords, 1)
        elif position == 'foot':
            index = 0
            angle = get_angle_on_curve(self.coords, 0)
        else:
            return
        
        if angle == None:
            return None
        else:
            pass
        result =  Polyline(
            points = (0, W/200, 0, -W/200))
        result.rotate(center = ORIGIN, angle = angle)
        result.set_pen_color(self.drawing_kit['pen color'])
        result.set_pen_width(4)
        result.change_anchor_to(result.center())

        if position == 'tip':
            result.move_to(self.tip())
        elif position == 'foot':
            result.move_to(self.foot())
        return result
    
    
    def create_arrow(self, position, *style):
        result = None
        if position == 'tip':
            index = -1
            angle = get_angle_on_curve(self.coords, 1)
            anchor = self.tip()
        elif position == 'foot':
            index = 0
            angle = get_angle_on_curve(self.coords, 0)
            if not angle == None:
                angle += math.pi
            anchor = self.foot()

        if angle == None:
            return None

        if len(style) > 0:
            style = style
        else:
            style = 'stealth'
    
        if style  == 'stealth':
            coords = points_to_tuple(\
                                     (0, 0),
                                     (-ARROW_WIDTH, -0.5*ARROW_HEIGHT),
                                     (-0.5*ARROW_WIDTH, 0),
                                     (-ARROW_WIDTH, 0.5*ARROW_HEIGHT))                                     
            commands = 'MLLLZ'
        elif style == 'curvy':
            coords = points_to_tupe(\
                                    (0, 0),
                                    (-0.5*ARROW_WIDTH, 0),
                                    (-ARROW_WIDTH, -0.5*ARROW_HEIGHT),
                                    (-0.5*ARROW_WIDTH, 0),
                                    (-ARROW_WIDTH, 0.5*ARROW_HEIGHT)
                                    (-0.5*ARROW_WIDTH, 0))
                                    
            commands = 'MQQQZ'
        else: # style: 'triangle'
            coords = points_to_tuple(\
                                     (0, 0),
                                     (-ARROW_WIDTH, -0.5*ARROW_HEIGHT),
                                     (-ARROW_WIDTH, 0.5*ARROW_HEIGHT))
            commands = 'MLLZ'
    
        result = Curve(anchor = anchor,
                       coords = coords,
                       commands = commands)
        result.set_drawing_kit(self.drawing_kit)
        result.translate((-self.drawing_kit['pen width'], 0)) # otherwise arrow "pokes through"/goes past where it should stop

    
        result.rotate(center = anchor, angle = angle)
    
        return result
    
    def update_avatar(self, t):
        if (t < self.epochs['begin time']) or (t > self.epochs['end time']):
            return

        avatar = Curve(
            anchor = self.anchor,
            coords = self.coords,
            commands = self.commands)
        avatar.set_drawing_kit(self.drawing_kit)
    
        for effect in self.effects:
            if not avatar == None:
                effect.apply_to(self, avatar, t)
        return avatar


    # -------------------- SYNCHRONIZATION METHODS --------------------
    def set_times(self, times_or_object, **kwargs):
        with PostponeTimeUpdatingToEnd(self):
            times = Primitive.set_times(self, times_or_object, **kwargs)
        return times

    def set_begin_time(self, begin_time_or_object, **kwargs):
        with PostponeTimeUpdatingToEnd(self):
            begin_time = Primitive.set_begin_time(self, begin_time_or_object, **kwargs)
        return begin_time

    def set_end_time(self, end_time_or_object, **kwargs):
        with PostponeTimeUpdatingToEnd(self):
            end_time = Primitive.set_end_time(self, end_time_or_object, **kwargs)
        return end_time

    def set_duration(self, duration, **kwargs):
        with PostponeTimeUpdatingToEnd(self):
            duration = Primitive.set_duration(self, duration, **kwargs)
        return duration

    def delay(self, delay):
        with PostponeTimeUpdatingToEnd(self):
            delay = Primitive.delay(self, delay)
        return delay

    def shift_to_begin_at(self, begin_time_or_object, **kwargs):
        with PostponeTimeUpdatingToEnd(self):
            begin_time = Primitive.shift_to_begin_at(self, begin_time_or_object, **kwargs)
        return begin_time

    def shift_to_end_at(self, end_time_or_object, **kwargs):
        with PostponeTimeUpdatingToEnd(self):
            end_time = Primitive.shift_to_end_at(self, end_time_or_object, **kwargs)
        return end_time

    # -------------------- FEEDBACK METHODS --------------------
    def sketch(self, root, cvsketch, ratio):
        s = ratio*root.winfo_screenwidth()/float(W)
        xy = self.points()
        hexcolor = '#%02x%02x%02x' % self.drawing_kit['pen color']
        cvsketch.create_polygon(scale(s, xy), outline = hexcolor, fill = '', width = 2)

    def print_epochs(self, indent = '', **kwargs):
        indent = indent
        Primitive.print_epochs(self, indent = indent, **kwargs)
        print('')
        for effect in self.effects:
            effect.print_epochs(indent = ' '*len(indent) + '> ', **kwargs)

    def report(self, indent = '', **kwargs):
        w = 14 # this should be the same as that from Primitive.report
        indent = indent
        if 'primitives' in kwargs.keys():
            primitives = kwargs['primitives']
        else:
            frame_locals = inspect.currentframe().f_back.f_locals
            primitives = filter_by_class(frame_locals, Primitive, option = 'inclusive')

        Primitive.report(self, indent = indent, primitives = primitives)
        if self.effects == []:
            print(indent + ' '*2),
            print(str('{0:<' + str(w) + '}').format('no effects'))
        elif len(self.effects) == 1:
            print(indent + ' '*2),
            print(str('{0:<' + str(w) + '}').format('1 effect') + ':'),
            effect = self.effects[0]
            print(' '*3 + '- '),
            print("\bid: %s"%id(effect)),
            print(' '*2),
            print('{0:<14}'.format('(' + find_name(effect, primitives) + ')'))
        else:
            print(indent + ' '*2),
            print(str('{0:<' + str(w) + '}').format(str(len(self.effects)) + ' effects') + ':'),
            effect = self.effects[0]
            print(' '*3 + '- '),
            print("\bid: %s"%id(effect)),
            print(' '*2),
            print('{0:<14}'.format('(' + find_name(effect, primitives) + ')'))
        
            for effect in self.effects[1:]:
                print(indent + ' '*(w+8) + '- '),
                print("\bid: %s"%id(effect)),
                print(' '*2),
                print('{0:<14}'.format('(' + find_name(effect, primitives) + ')'))
            
        print(indent + ' '*2),
        print(str('{0:<' + str(w) + '}').format('drawing kit') + ':'),
        print(' '*2),
        print('{0:<14}'.format(str(self.drawing_kit)))

        print(indent + ' '*2),
        print(str('{0:<' + str(w) + '}').format('decoration') + ':'),
        print(' '*2),
        print('{0:<14}'.format(str(self.decoration)))

# ------------------------------------------------------------------------------------------------------------------------
class Point(Curve):
    """ Attributes:
    - name
    - masters
    - epochs
    - external_call
    - anchor
    - cardinals
    - coords
    - commands
    - drawing_kit
    - decoration
    - effects
    """
    def __init__(self, center = ORIGIN, radius = 3):
        """ Input argument 'center' is a tuple with the (absolute) (x,y)-coordinates of the point.
        """
        if len(center) > 2:
            print("WARNING (method 'Point.__init__')."),
            print("Input 'center' too long, has %s entries, truncated to the first two." % len(center))
            center = center[0], center[1]
        Curve.__init__(
            self,
            anchor = tuple(center),
            coords = points_to_tuple((radius, 0),  (radius, -radius/2.0),  (radius/2.0, -radius), \
                                     (0, -radius),  (-radius/2.0, -radius),  (-radius, -radius/2.0), \
                                     (-radius, 0),  (-radius, radius/2.0),  (-radius/2.0, radius), \
                                     (0, radius),  (radius/2.0, radius),  (radius, radius/2.0), \
                                     (radius, 0)),
            commands = 'MCCCCZ')

        
# ------------------------------------------------------------------------------------------------------------------------
class Polyline(Curve):
    """ Attributes:
    - name
    - masters
    - epochs
    - external_call
    - anchor
    - cardinals
    - coords
    - commands
    - drawing_kit
    - decoration
    - effects
    """
    def __init__(self, points = (W/4, H/4, W/2, H, 2*W/3, H/4)):
        """ Input argument 'points' is a tuple 
        containing the (absolute) (x,y)-coordinates of the vertices of the polyline.
        By default, a Polyline is NOT closed.
        WARNING.  
        A Polyline which is a line segment between two points will not draw if it is closed.
        """
        anchor = points[0], points[1]
        commands = 'M'+'L'*(len(points)/2 - 1)

        Curve.__init__(self,
                       anchor = anchor,
                       coords = translate(points, scale(-1, anchor)),
                       commands = commands)
# ----------------------------------------------------------------------------------------------------
class RegularPolygon(Polyline):
    """ Input argument 'center' is a tuple.
    Attributes:
    - name
    - masters
    - epochs
    - external_call
    - anchor
    - cardinals
    - coords
    - commands
    - drawing_kit
    - decoration
    - effects
    """
    def __init__(self, center = CENTER, radius = H/4, edge_number = 6):
        N = edge_number
        angle = np.arange(0, 2*math.pi, 2*math.pi/float(N))
        x = [center[0] + radius*math.cos(alpha) for alpha in angle]
        y = [center[1] + radius*math.sin(alpha) for alpha in angle]
        points = x_and_y_to_xy(x, y)
        Polyline.__init__(self, points = points)
        self.change_anchor_to(center)
        self.close()

class Circle(RegularPolygon):
    """Attributes:
    - name
    - masters
    - epochs
    - external_call
    - anchor
    - cardinals
    - coords
    - commands
    - drawing_kit
    - decoration
    - effects
    """
    def __init__(self, center = CENTER, radius = W/16):
        RegularPolygon.__init__(self,
                                center = center,
                                radius = radius,
                                edge_number = radius)

class Arc(Polyline):
    """Attributes:
    - name
    - masters
    - epochs
    - external_call
    - anchor
    - cardinals
    - coords
    - commands
    - drawing_kit
    - decoration
    - effects
    """
    def __init__(self, center = CENTER, radius = H/4, angle_init = -math.pi/6, angle_fin = -math.pi/4):
        N = int(radius)
        angles = np.array([angle_init + i/float(N)*(angle_fin-angle_init) for i in range(N+1)])
        x = [center[0] + radius*math.cos(angle) for angle in angles]
        y = [center[1] + radius*math.sin(angle) for angle in angles]
        points = x_and_y_to_xy(x, y)
        Polyline.__init__(self,
                          points = points)
        self.change_anchor_to(center)

# ----------------------------------------------------------------------------------------------------
class Rectangle(Polyline):
    """Attributes:
    - name
    - masters
    - epochs
    - external_call
    - anchor
    - cardinals
    - coords
    - commands
    - drawing_kit
    - decoration
    - effects
    """
    def __init__(self, anchor = CENTER, width = W/4, height = H/4):
        nw = anchor
        sw = translate(anchor, (0, height))
        se = translate(anchor, (width, height))
        ne = translate(anchor, (width, 0))
        Polyline.__init__(self, points = points_to_tuple(nw, sw, se, ne))
        self.close()
        
        
# ------------------------------ MAIN ------------------------------


if __name__ == '__main__':
    import os
    import sys
    import Tkinter
    from monitor import Sketch
    from PIL import Image
    import aggdraw

    os.system('clear')
    
    print("~"*60)
    print("This is %s." %os.path.basename(sys.argv[0]))
    print("~"*60)

    #rootsketch = Tkinter.Tk()
    #sketch = Sketch(rootsketch)

    # Create a rectangle, set parameters and add features
    rect0 = Rectangle(CENTER, width = W/8, height = H/8)
    rect0.record_name()
    rect0.set_pen_color(COBALT)
    rect0.add_decoration({'type': 'point', 'position': 'foot'})
    rect0.homothety(rect0.anchor, 0.66, 1)

    # Create a polygonal curve, set parameters and add features
    polyline0 = Polyline(points = (200, 200, 400, 600))
    # polyline0 = Rectangle(ORIGIN, width = W/4, height = H/8)
    # polyline0 = Polyline(points = points_to_tuple(ORIGIN, CENTER))
    polyline0.record_name()
    polyline0.set_pen_color(LIMEGREEN)
    polyline0.set_brush_color(LIMEGREEN)
    polyline0.add_decoration({'type': 'tick', 'position': 'tip'})
    polyline0.add_decoration({'type': 'arrow', 'position': 'foot'})

    #
    #sketch.add_graphics(rect0, polyline0)
    #sketch.refresh()    


    #
    img = Image.new('RGBA', (W, H), DEFAULT_BACKGROUND_COLOR)

    canvas = aggdraw.Draw(img)

    # This draws on the canvas directly, without creating an object
    pen = aggdraw.Pen((255, 0, 255), DEFAULT_PEN_WIDTH)
    aggdrawstring = 'M600,200 L400,600'
    symbol = aggdraw.Symbol(aggdrawstring)
    canvas.symbol((0,0), symbol, pen)


    # Draw the objects created earlier via their method
    polyline0.draw(canvas)
    rect0.draw(canvas)
    

    canvas.flush()
    img.save('alinesegment.png')
    
    os.system(' '.join(['open -a preview alinesegment.png']))

    
    # ============== END OF SCRIPT ================================
    
    print("="*80)
    print("END OF SCRIPT.")
    print("="*80)
    #rootsketch.mainloop()
    # ============================================================

