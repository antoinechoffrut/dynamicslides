# container.py
# Th 11 Oct 2018
# Antoine Choffrut
#
# Code for the class 'Container'.


from geometry import *
from primitive import Primitive, filter_by_class, extract_times
from effect import Effect, Fade, Travel, Zoom, Trace, Spin, Sunrise, Reveal, ThreeBlueOneBrown, Trickle, Wring
from graphic import Graphic
from curve import Curve, Point, Polyline, RegularPolygon, Circle, Arc, Rectangle
import inspect
import random
from xml.dom import minidom

def extract_standalones(alist, subelements):
    """ Iteratively search for all standalones, i.e. Curve objects or Block objects, and removes duplicates.
    Standalone objects inside a Block object are not searched.
    If a Compound object contains other Compound objects, these will be searched iteratively.
    """
    if alist == []:
        return [element
                       for element in subelements
                       if (isinstance(element, Curve) or isinstance(element, Block))]
    else:
        new_subelements = subelements \
                          + [element
                             for element in alist
                             if (isinstance(element, Curve) or isinstance(element, Block))]                          
        new_alist = [elt
                     for element in alist
                     if isinstance(element, Compound)
                     for elt in element.elements]
                     
        return list(set(extract_standalones(new_alist, new_subelements)))

def get_subelements_by_class(alist, subelements, aclass):
    """ Iteratively searches for all objects of the specified class 'aclass'. 
    The content of Container objects are also searched.
    Removes duplicates. """
    if alist == []:
        return subelements
    else:
        new_subelements = subelements \
                          + [element for element in alist if isinstance(element, aclass)]
        new_alist = [elt
                     for element in alist
                     if isinstance(element, Container)
                     for elt in element.elements]
                     
        return list(set(get_subelements_by_class(new_alist, new_subelements, aclass)))


class PostponeCurveTimeUpdatingToEnd(object):
    def __init__(self, container):
        self.container = container
        self.curves_with_old_times = {}
        if self.container.external_call == False:
            self.curves_with_old_times = dict({curve: tuple(curve.epochs.values())
                                               for curve in get_subelements_by_class(self.container.elements, [], Curve)})
        
    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        if self.container.external_call == False:
            for curve in self.curves_with_old_times.keys():
                curve_old_times = self.curves_with_old_times[curve]
                curve_new_times = curve.epochs.values()
                for effect in curve.effects:
                    dt = effect.lifespan()
                    if effect.stage == 'intro':
                        dt_begin = effect.epochs['begin time'] - curve_old_times[0]
                        effect.epochs['begin time'] = max(min(curve_new_times[0] + dt_begin, \
                                                              curve_new_times[1]), curve_new_times[0])
                        effect.epochs['end time'] = max(min(curve_new_times[0] + dt_begin + dt, \
                                                            curve_new_times[1]), curve_new_times[0])
                    elif effect.stage == 'outro':
                        dt_end = effect.epochs['end time'] - curve_old_times[1]
                        effect.epochs['end time'] = max(min(curve_new_times[1] + dt_end, \
                                                            curve_new_times[1]), curve_new_times[0])
                        effect.epochs['begin time'] = max(min(curve_new_times[1] + dt_end - dt, \
                                                              curve_new_times[1]), curve_new_times[0])
                curve.update_epochs()

            for graphic in get_subelements_by_class(self.container.elements, [], Graphic):
                graphic.external_call = False


        
class PostponeCurveGeometricUpdatingToEnd(object):
    def __init__(self, container):
        self.container = container

    def __enter__(self):
        for element in self.container.elements:
            element.external_call = True

    def __exit__(self, type, value, traceback):
        if self.container.external_call == False:
            for element in self.container.elements:
                element.update_cardinals()
                element.external_call = False
        

class Container(Graphic):
    """ Attributes:
    - name
    - masters
    - epochs
    - external_call
    - anchor
    - cardinals
    - elements
    """
    def __init__(self, *elements):
        Graphic.__init__(self)
        self.elements = []
        self.initialize_elements(*elements)
        self.update_epochs()
        self.external_call = False

    def  initialize_elements(self, *elements):
        self.elements = []
        for element in elements:
            self.add_element(element)


    # -------------------- BASIC METHODS --------------------

    def  set_drawing_kit(self, drawing_kit):
        for element in self.elements:
            element.set_drawing_kit(drawing_kit)
            
    def  set_pen_color(self, pen_color):
        for element in self.elements:
            element.set_pen_color(pen_color)
            
    def  set_pen_width(self, pen_width):
        for element in self.elements:
            element.set_pen_width(pen_width)
            
    def  set_brush_color(self, brush_color):
        for element in self.elements:
            element.set_brush_color(brush_color)
            
    def standalones(self):
        return extract_standalones(self.elements, [])

    def get_blocks(self):
        return get_subelements_by_class(self.elements, [], Block)

    def update_epochs(self):
        if self.elements == []:
            print("WARNING."),
            print("Object %s of class '%s' contains no element." % (self.name, self.__class__.__name__)),
            print("Set epochs to default value.")
            self.epochs = dict(DEFAULT_EPOCHS)
            return
        subelements = get_subelements_by_class(self.elements, [], Graphic)
        self.epochs['begin time'] = min([element.epochs['begin time'] for element in subelements])
        self.epochs['end time'] = max([element.epochs['end time'] for element in subelements])
        Graphic.update_epochs(self)

    def add_element(self, element):
        if not element.masters == []:
            if isinstance(element.masters[0], Animation):
                print("WARNING."),
                print("Cannot add %s of class %s to %s of class %s," \
                      % (element.name, element.__class__.__name__, self.name, self.__class__.__name__))
                print("since it is an element of an object of class Animation.")
                return
        if element in self.elements:
            print("WARNING."),
            print("Object %s of class %s already an element of object %s of class %s, will not be added." \
                  % (element.name, element.__class__.__name__, self.name, self.__class__.__name__))
            return
        if self is element:
            print("WARNING."),
            print("Cannot add self to elements.")
            return
        if isinstance(element, Effect):
            print("WARNING."%id(element)),
            print("Cannot add Effect object (id %s) to Compound (id %s)."%(id(element), id(self)))
            return 

        if isinstance(element, Container):
            containers = get_subelements_by_class(element.elements, [], Container)
        else:
            containers = []

        # This is to avoid infinite loops when calling update_epochs method.
        for elt in containers:
            if (self is elt):
                print("WARNING."),
                print("Cannot add to elements of self"),
                print("a container which contains self among subelements.")
                return
            else:
                pass

        element.masters.append(self)
        self.elements.append(element)
        self.update_epochs()
        Container.update_cardinals(self)

    # -------------------- GEOMETRIC METHODS --------------------
    def update_cardinals(self):
        aux = flatten(tuple(element.corners() for element in self.elements))
        self.cardinals = get_cardinals(aux)
        for key in self.cardinals.keys():
            self.cardinals[key] = translate(self.cardinals[key], scale(-1, self.anchor))
        self.change_anchor_to(self.nw())
        Graphic.update_cardinals(self)




    # -------------------- SYNCHRONIZATION METHODS --------------------
    def delay(self, delay):
        with PostponeCurveTimeUpdatingToEnd(self):
            for curve in get_subelements_by_class(self.elements, [], Curve):
                delay = Primitive.delay(curve, delay)                
        return delay


    # -------------------- FEEDBACK METHODS --------------------
    def sketch(self, root, cvsketch, ratio, color):
        Graphic.sketch(self, root, cvsketch, ratio, color = color)
        for graphic in self.elements:
            graphic.sketch(root, cvsketch, ratio)


    def print_epochs(self, indent = '', **kwargs):
        indent = indent
        Primitive.print_epochs(self, indent = indent, **kwargs)
        print('')
        for element in self.elements:
            element.print_epochs(indent = ' '*len(indent) + '- ', **kwargs)
            print('')

    def report(self, indent = '', **kwargs):
        w = 14 # this should be the same as that from Primitive.report
        indent = indent
        if 'primitives' in kwargs.keys():
            primitives = kwargs['primitives']
        else:
            frame_locals = inspect.currentframe().f_back.f_locals
            primitives = filter_by_class(frame_locals, Primitive, option = 'inclusive')


        Primitive.report(self, indent = indent, primitives = primitives)
        if self.elements == []:
            print(indent + ' '*2),
            print(str('{0:<' + str(w) + '}').format('no elements'))
            return
        elif len(self.elements) == 1:
            print(indent + ' '*2),
            print(str('{0:<' + str(w) + '}').format('1 element') + ':'),
        else:
            print(indent + ' '*2),
            print(str('{0:<' + str(w) + '}').format(str(len(self.elements)) + ' elements') + ':'),
        element = self.elements[0]
        print(' '*3 + '- '),
        print("\bid: %s"%id(element)),
        print(' '*2),
        print('{0:<14}'.format('(' + find_name(element, primitives) + ')'))
        
        for element in self.elements[1:]:
            print(indent + ' '*(w+8) + '- '),
            print("\bid: %s"%id(element)),
            print(' '*2),
            print('{0:<14}'.format('(' + find_name(element, primitives) + ')'))

    # -------------------- DRAWING METHODS --------------------
    def  draw(self, canvas, *t):
        for element in self.elements:
            element.draw(canvas, *t)
    
# ==================== COMPOUND ====================
class Compound(Container):

    def add_effects(self, *effects):
        for element in self.elements:
            element.add_effects(*effects)

    # -------------------- FEEDBACK METHODS --------------------
    def sketch(self, root, cvsketch, ratio):
        Container.sketch(self, root, cvsketch, ratio, color = 'green')

    # -------------------- GEOMETRIC METHODS --------------------

    def translate(self, v):
        with PostponeCurveGeometricUpdatingToEnd(self):
            for element in self.elements:
                element.translate(v)

    def homothety(self, center, sx, sy):
        with PostponeCurveGeometricUpdatingToEnd(self):
            for element in self.elements:
                element.homothety(center, sx, sy)

    def rotate(self, center, angle):
        with PostponeCurveGeometricUpdatingToEnd(self):
            for element in self.elements:
                element.rotate(center, angle)

    def move_to(self, p):
        with PostponeCurveGeometricUpdatingToEnd(self):
            for element in self.elements:
                element.move_to(p)

    # -------------------- SYNCHRONIZATION METHODS --------------------
    def set_times(self, times_or_object, **kwargs):
        with PostponeCurveTimeUpdatingToEnd(self):
            for standalone in self.standalones():
                standalone.external_call = True
                times = standalone.set_times(times_or_object, **kwargs)
        return times

    def set_begin_time(self, begin_time_or_object, **kwargs):
        with PostponeCurveTimeUpdatingToEnd(self):
            for standalone in self.standalones():
                standalone.external_call = True
                begin_time = standalone.set_begin_time(begin_time_or_object, **kwargs)
        return begin_time

    def set_end_time(self, end_time_or_object, **kwargs):
        with PostponeCurveTimeUpdatingToEnd(self):
            for standalone in self.standalones():
                standalone.external_call = True
                end_time = standalone.set_end_time(end_time_or_object, **kwargs)
        return end_time


    def set_duration(self, duration, **kwargs):
        with PostponeCurveTimeUpdatingToEnd(self):
            for standalone in self.standalones():
                standalone.external_call = True
                duration = standalone.set_duration(duration, **kwargs)
        return duration


    def shift_to_begin_at(self, begin_time_or_object, **kwargs):
        with PostponeCurveTimeUpdatingToEnd(self):
            for standalone in self.standalones():
                standalone.external_call = True
                begin_time = standalone.shift_to_begin_at(begin_time_or_object, **kwargs)
        return begin_time

    def shift_to_end_at(self, end_time_or_object, **kwargs):
        with PostponeCurveTimeUpdatingToEnd(self):
            for standalone in self.standalones():
                standalone.external_call = True
                end_time = standalone.shift_to_end_at(end_time_or_object, **kwargs)
        return end_time


# ==================== BLOCK =========================
class Block(Container):

    def add_effects(self, *effects):
        for effect in effects:
            if isinstance(effect, Fade) \
               or isinstance(effect, Spin) \
               or isinstance(effect, Sunrise) \
               or isinstance(effect, Zoom) \
               or isinstance(effect, Trace):
                for element in self.elements:
                    element.add_effects(effect)
            elif isinstance(effect, Travel):
                for element in self.elements:
                    center = translate(effect.center, translate(element.anchor, scale(-1, self.anchor)))
                    element.add_effects(Travel(\
                                               stage = effect.stage,
                                               center = center,
                                               duration = effect.lifespan(),
                    ))
            elif isinstance(effect, Wring):
                if not isinstance(self, TexObject):
                    print("WARNING."),
                    print("Effect 'Wring' not supported for class '%s', only for class 'TexObject'." \
                          % self.__class__.__name__)
                else:
                    center = effect.center
                    c = (0.5*self.width()*center[0], -self.base_to_waist*center[1])
                    c = translate(c, self.base_center())
                    for element in self.elements:
                        element.add_effects(Wring(\
                                                  stage = effect.stage,
                                                  center = c,
                                                  amplitude = effect.amplitude,
                                                  pace = effect.pace,
                                                  duration = effect.lifespan(),
                        ))
            elif isinstance(effect, Trickle):
                N = len(self.elements)
                #
                ordering = range(N)
                if effect.order == 'decreasing':
                    ordering.reverse()
                elif effect.order == 'random':
                    random.shuffle(ordering)
                #
                for i in range(N):
                    element = self.elements[i]
                    dt = effect.lifespan()/8 # or divide by 2, 4, ...?
                    DT = effect.lifespan() - dt
                    center = translate(element.anchor, effect.separation)
                    elt_eff = Travel(\
                                     stage = effect.stage,
                                     center = center,
                                     pace = 'soft landing',
                                     )
                    elt_eff.set_times((effect.begin() + ordering[i]*DT/N, effect.begin() + ordering[i]*DT/N + dt))
                    if effect.stage == 'outro':
                        elt_eff.delay(-effect.lifespan())                    
                    element.add_effects(elt_eff)
            elif isinstance(effect, Reveal):
                N = len(self.elements)
                if effect.ordering == None:
                    ordering = range(N)
                    if effect.order == 'decreasing':
                        ordering.reverse()
                    elif effect.order == 'random':
                        random.shuffle(ordering)
                else:
                    ordering = effect.ordering
                for i in range(N):
                    element = self.elements[i]
                    dt = effect.lifespan()/4
                    DT = effect.lifespan() - dt
                    elt_eff = Fade(\
                                   stage = effect.stage,
                                   tools = effect.tools,
                    )
                    elt_eff.set_times((effect.begin() + ordering[i]*DT/N, effect.begin() + ordering[i]*DT/N + dt))
                    if effect.stage == 'outro':
                        elt_eff.delay(-effect.lifespan())                    
                    element.add_effects(elt_eff)
            elif isinstance(effect, ThreeBlueOneBrown):
                N = len(self.elements)
                #
                ordering = range(N)
                if effect.order == 'decreasing':
                    ordering.reverse()
                elif effect.order == 'random':
                    random.shuffle(ordering)
                #
                M = 3
                pen_epochs = dict({'begin time': 0*SECONDS, 'end time': (M - 1)*DEFAULT_EFFECT_DURATION/M})
                brush_epochs = dict({'begin time': DEFAULT_EFFECT_DURATION/M, 'end time': DEFAULT_EFFECT_DURATION})
                if effect.stage == 'outro':
                    pen_epochs['begin time'] = pen_epochs['begin time'] - (M - 1)/DEFAULT_EFFECT_DURATION/M
                    pen_epochs['end time'] = pen_epochs['end time'] - (M - 1)/DEFAULT_EFFECT_DURATION/M
                    brush_epochs['begin time'] = brush_epochs['begin time'] - (M + 1)*DEFAULT_EFFECT_DURATION/M
                    brush_epochs['end time'] = brush_epochs['end time'] - (M + 1)*DEFAULT_EFFECT_DURATION/M
                    
                self.add_effects(Reveal(\
                                        stage = effect.stage,
                                        tools = ['pen'],
                                        epochs = pen_epochs,
                                        order = 'does not matter here',
                                        ordering = ordering,
                                        duration = effect.lifespan()))
                self.add_effects(Reveal(\
                                        stage = effect.stage,
                                        tools = ['brush'],
                                        epochs = brush_epochs,
                                        order = 'does not matter here',
                                        ordering = ordering,
                                        duration = effect.lifespan()))
            else:
                print("WARNING"),
                print("Effect '%s' not yet supported."%effect.__class__.__name__)

                

                    
    # -------------------- FEEDBACK METHODS --------------------
    def sketch(self, root, cvsketch, ratio):
        Container.sketch(self, root, cvsketch, ratio, color = 'red')

    # -------------------- GEOMETRIC METHODS --------------------
    def update_cardinals(self):
        Graphic.update_cardinals(self)
    
    def translate(self,v):
        with PostponeCurveGeometricUpdatingToEnd(self):
            Graphic.translate(self, v)
            for element in self.elements:
                element.translate(v)

    def homothety(self, center, sx, sy):
        with PostponeCurveGeometricUpdatingToEnd(self):
            Graphic.homothety(self, center, sx, sy)
            for element in self.elements:
                element.homothety(center, sx, sy)

    def rotate(self, center, angle):
        with PostponeCurveGeometricUpdatingToEnd(self):
            Graphic.rotate(self, center, angle)
            for element in self.elements:
                element.rotate(center, angle)

    def move_to(self, p):
        with PostponeCurveGeometricUpdatingToEnd(self):
            for element in self.elements:
                element.move_to(add(p, subtract(element.anchor, self.anchor)))
            Graphic.move_to(self, p)

    # -------------------- SYNCHRONIZATION METHODS --------------------
    def set_times(self, times_or_object, **kwargs):
        print("WARNING (object %s)." % self.name),
        print("Method 'set_times' not yet supported for object of class Block.")
        print("Used method 'set_begin_time' instead."),
        print("----> TO DO <----")
        return self.set_begin_time(times_or_object, **kwargs)
        
        
    def set_begin_time(self, begin_time_or_object, **kwargs):
        times = extract_times(begin_time_or_object, **kwargs)
        with PostponeCurveTimeUpdatingToEnd(self):
            for standalone in self.standalones():
                standalone.external_call = True
                dt = standalone.epochs['begin time'] - self.epochs['begin time']
                standalone.set_begin_time(times[0] + dt)
        return times[0]

    def set_end_time(self, end_time_or_object, **kwargs):
        times = extract_times(end_time_or_object, **kwargs)
        with PostponeCurveTimeUpdatingToEnd(self):
            for standalone in self.standalones():
                standalone.external_call = True
                dt = standalone.epochs['end time'] - self.epochs['end time']
                standalone.set_end_time(times[1] + dt)
        return times[1]

    def set_duration(self, duration, **kwargs):
        print("WARNING."),
        print("Cannot use 'set_duration' on object (id %s) of class 'Block'."%id(self))

    def shift_to_begin_at(self, begin_time_or_object, **kwargs):
        times = extract_times(begin_time_or_object, **kwargs)
        with PostponeCurveTimeUpdatingToEnd(self):
            for standalone in self.standalones():
                standalone.external_call = True
                dt = standalone.epochs['begin time'] - self.epochs['begin time']
                begin_time = standalone.shift_to_begin_at(times[0] + dt)
        return begin_time

    def shift_to_end_at(self, end_time_or_object, **kwargs):
        times = extract_times(end_time_or_object, **kwargs)
        with PostponeCurveTimeUpdatingToEnd(self):
            for standalone in self.standalones():
                standalone.external_call = True
                dt = standalone.epochs['end time'] - self.epochs['end time']
                end_time = standalone.shift_to_end_at(times[1] + dt)
        return end_time


# ---------------------------------------- SVG ----------------------------------------
def get_svg_elements(file_name):

    doc = minidom.parse(file_name)
    x_min = float(doc.getElementsByTagName("svg")[0].getAttribute('viewBox').split()[0])
    y_min = float(doc.getElementsByTagName("svg")[0].getAttribute('viewBox').split()[1])

    D = {}
    path_elements = doc.getElementsByTagName('path')
    for path_element in path_elements:
        D[path_element.getAttribute('id')] = path_element.getAttribute('d')

    use_elements = doc.getElementsByTagName('use')
    L = len(use_elements)

    elements = []
    for use_element in use_elements:
        dx = float(use_element.getAttribute('x')) - x_min
        dy = float(use_element.getAttribute('y')) - y_min
        anchor = dx, dy

        id = use_element.getAttribute('xlink:href')[1:]
        coords, commands = d_to_coords_and_commands(D[id])
        elements.append(Curve(
            anchor = anchor,
            coords = coords,
            commands = commands))

    w = float(doc.getElementsByTagName("svg")[0].getAttribute('width').replace('pt',''))
    h = float(doc.getElementsByTagName("svg")[0].getAttribute('height').replace('pt',''))
    nw_corner = 0, 0
    sw_corner = 0, h
    se_corner = w, h
    ne_corner = w, 0

    xy = points_to_tuple(nw_corner, sw_corner, se_corner, ne_corner)
    return get_cardinals(xy), elements


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
    coords = tuple(float(coord) for item in coords for coord in item)
    return coords, commands

# --------------------------------------- SVGOBJECT -------------------------------------------------------------
class SVGObject(Block):
    """ Attributes:
    - name
    - masters
    - epochs
    - external_call
    - anchor
    - cardinals
    - elements
    """
    def __init__(self, file_name):
        Primitive.__init__(self)
        self.anchor = ORIGIN
        self.cardinals, self.elements = get_svg_elements(file_name)
        for element in self.elements:
            element.masters.append(self)
        self.external_call = False
        self.update_epochs()

        

# ------------------------------ TEXOBJECT ------------------------------
class TexObject(SVGObject):
    """ Attributes:
    - name
    - masters
    - epochs
    - external_call
    - anchor
    - cardinals
    - elements
    """
    def __init__(self, expression):
        tex_file_name = generate_tex_file(expression)
        dvi_file_name = tex_to_dvi(tex_file_name)
        svg_file_name = dvi_to_svg(dvi_file_name)

        SVGObject.__init__(
            self,
            file_name = svg_file_name)
        self.base_to_waist = self.set_base_to_waist(svg_file_name)
        self.add_base_and_waist_cardinals(svg_file_name)
        self.homothety(self.anchor, NORMAL_TEXT_SCALE, NORMAL_TEXT_SCALE)
        self.set_drawing_kit(DEFAULT_DRAWING_KIT)



    def base_left(self):
        return add(self.anchor, self.cardinals['bl'])

    def base_right(self):
        return add(self.anchor, self.cardinals['br'])

    def base_center(self):
        return add(self.anchor, self.cardinals['bc'])
    
    def waist_left(self):
        return add(self.anchor, self.cardinals['wl'])

    def waist_right(self):
        return add(self.anchor, self.cardinals['wr'])

    def waist_center(self):
        return add(self.anchor, self.cardinals['wc'])

    def right(self):
        return interpolate(self.waist_right(), self.base_right(), 0.5)

    def left(self):
        return interpolate(self.waist_left(), self.base_left(), 0.5)

    def base_line(self):
        points = points_to_tuple(self.cardinals['bl'], self.cardinals['br'])
        points = translate(points, self.anchor)

        result = Polyline(points)
        result.masters.append(self)
        result.set_drawing_kit({'pen color': BLUE, 'pen width': 2, 'brush color': None})
        return result

    def waist_line(self):
        points = points_to_tuple(self.cardinals['wl'], self.cardinals['wr'])
        points = translate(points, self.anchor)

        result = Polyline(points)
        result.masters.append(self)
        result.set_drawing_kit({'pen color': BLUE, 'pen width': 2, 'brush color': None})
        return result

    def set_base_to_waist(self, svgfilename):
        doc = minidom.parse(svgfilename)
        w = float(doc.getElementsByTagName("svg")[0].getAttribute('width').replace('pt',''))
        y_min = float(doc.getElementsByTagName("svg")[0].getAttribute('viewBox').split()[1])
        
        return float(doc.getElementsByTagName('rect')[0].getAttribute('height'))


    def add_base_and_waist_cardinals(self, svgfilename):
        doc = minidom.parse(svgfilename)
        w = float(doc.getElementsByTagName("svg")[0].getAttribute('width').replace('pt',''))
        y_min = float(doc.getElementsByTagName("svg")[0].getAttribute('viewBox').split()[1])
        
        h = float(doc.getElementsByTagName('rect')[0].getAttribute('height'))
        dy = float(doc.getElementsByTagName('rect')[0].getAttribute('y')) - y_min

        self.cardinals['wl'] = 0, dy
        self.cardinals['wr'] = w, dy
        self.cardinals['wc'] = interpolate(self.cardinals['wl'], self.cardinals['wr'], 0.5)
        self.cardinals['bl'] = 0, dy + h
        self.cardinals['br'] = w, dy + h
        self.cardinals['bc'] = interpolate(self.cardinals['bl'], self.cardinals['br'], 0.5)


# ------------------------------------------------------------
class Animation(Block):
    def add_element(self, element):
        if not element.masters == []:
            print("WARNING."),
            print("Object %s of class %s already has a master," % (element.name, element.__class__.__name__))
            print("cannot be added to Animation object %s." % self.name)
            return
        #
        element.set_times((0, 1))
        #
        if not self.elements == []:
            if len(self.elements) == 1:
                element.shift_to_begin_at(self.elements[0], epoch = 'end time')
            else:
                element.set_end_time(self.elements[-1].lifespan())
                self.elements[-1].set_duration(1)
                element.shift_to_begin_at(self.elements[-1], epoch = 'end time')
                
        #
        element.masters.append(self)
        self.elements.append(element)
        self.update_epochs()
        Container.update_cardinals(self)

    def add_effects(self, *effects):
        for effect in effects:
            if isinstance(effect, Fade) \
               or isinstance(effect, Travel) \
               or isinstance(effect, Zoom) \
               or isinstance(effect, Spin) \
               or isinstance(effect, Sunrise) \
               or isinstance(effect, Wring) \
               or isinstance(effect, Trace):
                if effect.stage == 'intro':
                    self.elements[0].add_effects(effect)
                elif effect.stage == 'outro':
                    self.elements[-1].add_effects(effect)
                else:
                    print("WARNING (method 'Animation.add_effects')."),
                    print("Unknown stage '%s'." % effect.stage)
            else:
                print("WARNING (method 'Animation.add_effects')."),
                print("Effect of class '%s' not supported for class 'Animation'." % effect.__class__.__name__)
                
                
               

    def extend(self, dt):
        if self.elements == []:
            return
        if len(self.elements) == 1:
            print("WARNING."),
            print("Object %s of class 'Animation' has only one element." % self.name),
            print("Method 'extend' ignored in this case.")
        else:
            if dt < 0:
                self.elements[0].epochs['begin time'] = self.elements[1].epochs['begin time'] - 1 + dt
            else:
                self.elements[-1].epochs['end time'] = self.elements[-2].epochs['end time'] + 1 + dt
            self.update_epochs()




    def set_times(self, times_or_object, **kwargs):
        print("WARNING (object %s)." % self.name),
        print("Method 'set_times' not implemented for object of class Block.")
        print("Used method 'shift_to_begin_at' instead.")
        return self.shift_to_begin_at(times_or_object, **kwargs)
        
    def set_begin_time(self, begin_time_or_object, **kwargs):
        print("WARNING (object %s)." % self.name)
        print("Method 'set_begin_time' not implemented for class 'Animation',")
        print("used method 'shift_to_begin_at' instead.")
        return self.shift_to_begin_at(begin_time_or_object, **kwargs)

    def set_end_time(self, end_time_or_object, **kwargs):
        print("WARNING (object %s)." % self.name)
        print("Method 'set_end_time' not implemented for class 'Animation',")
        print("used method 'shift_to_end_at' instead.")
        return self.shift_to_end_at(end_time_or_object, **kwargs)


# -------------------- MAIN --------------------

if __name__ == '__main__':
    from camera import Camera
    from monitor import Timeline
    import os
    import sys
    import Tkinter
    import math


    os.system('clear')
    
    print("~"*60)
    print("This is %s." %os.path.basename(sys.argv[0]))
    print("~"*60)

    #timeline_root = Tkinter.Tk()
    #timeline = Timeline(timeline_root)
    camera = Camera()



    # ============================================================
    # ============================================================
    #                               KEEP THIS - TESTING OF THE EFFECTS
    # ============================================================
    # ============================================================
    
    texobject0 = TexObject(expression = "abcde") 
    #texobject0 = TexObject(expression = "$+1$")
    texobject0.record_name()
    texobject0.set_brush_color(LIMEGREEN)
    texobject0.move_to(CENTER)
    #texobject0.move_to((W/4, H/4))
    texobject0.set_end_time(5*SECONDS)

    #texobject0.add_effects(Travel(center = ORIGIN))
    #texobject0.add_effects(Travel(stage = 'outro', center = SOUTH_POINT))
    #texobject0.add_effects(Zoom(center = texobject0.nw(), ratio = 2))
    #texobject0.add_effects(Zoom(stage = 'outro', center = SW_CORNER, ratio = 0.1))
    #texobject0.add_effects(Spin(center = texobject0.north()))
    #texobject0.add_effects(Spin(stage = 'outro', center = texobject0.right(), angle = 0.5*math.pi))
    #texobject0.add_effects(Sunrise(center = texobject0.north()))
    #texobject0.add_effects(Sunrise(stage = 'outro', center = texobject0.right(), angle = 0.5*math.pi))
    #texobject0.add_effects(Wring())
    #texobject0.add_effects(Wring(stage = 'outro'))
    #texobject0.add_effects(Reveal(order = 'random', tools = ['pen']))
    #texobject0.add_effects(Reveal(stage = 'outro', order = 'decreasing', tools = ['brush']))
    #texobject0.add_effects(ThreeBlueOneBrown(order = 'decreasing'))
    #texobject0.add_effects(ThreeBlueOneBrown(stage = 'outro', order = 'random'))
    texobject0.add_effects(Trickle())
    texobject0.add_effects(Trickle(stage = 'outro', separation = (-2*W, -2*H)))

    #rect0 = Rectangle()
    #rect0.record_name()
    #rect0.set_end_time(texojbect0)
    #rect0.add_effects(Sunrise(center = rect0.north()))
    #rect0.add_effects(Sunrise(stage = 'outro', center = rect0.east(), angle = 0.5*math.pi))
    


    
    
    #timeline.add_graphics(texobject0)
    #timeline.refresh()
    camera.add_graphics(texobject0)
    camera.roll()
    
    

    # ============== END OF SCRIPT ================================
    print("="*80)
    print("END OF SCRIPT.")
    print("="*80)
    #timeline_root.mainloop()

