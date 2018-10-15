# primitive.py
# Th 11 Oct 2018
# Antoine Choffrut
#
# Code for the class 'Primitive', which is the most basic class.
# The two (immediate) subclasses are:
# - 'Graphic', which consists of graphical elements,
# - 'Effect', which affect how 'Graphic' instances behave in the video.


from constants import *
from helpers import *
import inspect
import numpy as np

def current_variables():
    print("-"*30)
    print("List of current named variables.")
    print("-"*30)
    frame_locals = inspect.currentframe().f_back.f_locals
    varnames_to_id = {key: id(frame_locals[key])
                      for key in frame_locals.keys()
                      if isinstance(frame_locals[key], Primitive)}
    varlist = [[key, id(frame_locals[key])] for key in varnames_to_id.keys()]
    varlist = sorted(varlist, key = lambda x: int(x[1]))
    for item in varlist:
        print("id %s:  %s"%(str(item[1]), item[0]))
    

def filter_by_class(frame_locals, aclass, option = 'inclusive'):
    """ Returns a dictionary of variables of class 'aclass'. """
    varnames = tuple(key for key in frame_locals.keys()
                if isinstance(frame_locals[key], Primitive))
    if option == 'inclusive':
        return {key: frame_locals[key]
                for key in varnames
                if isinstance(frame_locals[key], aclass)}
    elif option == 'exclusive':
        return {key: frame_locals[key]
                for key in varnames
                if type(frame_locals[key]) == aclass}
    else:
        print("WARNING. Unknown option '%s'."%option)
        return frame_locals



def print_epochs(*args):
    print("\n"+'-'*60)
    print("EPOCHS.\n")

    frame_locals = inspect.currentframe().f_back.f_locals
    primitives = filter_by_class(frame_locals, Primitive, option = 'inclusive')

    requested_prim_names = tuple(prim_name for prim_name in args if prim_name in primitives.keys())
    for prim_name in requested_prim_names:
        primitives[prim_name].print_epochs(primitives = primitives)
        print('')

    default_class_name_list = 'Effect', 'Primitive', 'Graphic', 'Curve', 'Container', 'Compound', 'Block'
    if 'all' in args:
        class_name_list = default_class_name_list
    else:
        class_name_list = tuple(class_name
                           for class_name in args
                           if class_name in default_class_name_list)

    if not class_name_list == ():
        print("Objects by class.")
        for class_name in class_name_list:
            prims = {prim_name: primitives[prim_name]
                     for prim_name in primitives.keys()
                     if primitives[prim_name].main_class_name() == class_name}
            if not prims == {}:
                print('+'),
                print("'%s' (%s):"%(class_name, len(prims)))
                for prim_name in prims.keys():
                    primitives[prim_name].print_epochs(primitives = primitives, indent = ' '*4 + '- ')

def extract_times(times_or_object, **kwargs):
    if isinstance(times_or_object, Primitive):
        times = times_or_object.epochs['begin time'], times_or_object.epochs['end time']
    elif type(times_or_object) == tuple:
        times = list(times_or_object)
    elif (type(times_or_object) ==  int) or (type(times_or_object) == float):
        times = times_or_object, times_or_object
    if 'offset' in kwargs.keys():
        times = times[0] + kwargs['offset'], times[1] + kwargs['offset']
    if 'epoch' in kwargs.keys():
        if kwargs['epoch'] == 'begin time':
            times = (times[0], times[0])
        elif kwargs['epoch'] == 'end time':
            times = (times[1], times[1])
        else:
            print("WARNING (global function 'extract_times')."),
            print("Unknown value '%s' for option 'epoch'."%str(kwargs['epoch']))
    if times[1] < times[0]:
        print("WARNING."),
        print("Epoch 'end time' (%s) must remain after 'begin time' (%s), has been set to 'begin time'."\
              %(times[1]/float(SECONDS), times[0]/float(SECONDS)))
        times = times[0], times[0]
    return times

def  fit_within_epochs(t, obj):
    return max(min(t, obj.end()), obj.begin())

# -------------------- CLASSES --------------------
class Primitive(object):
    """ Attributes: 
    - name
    - masters
    - epochs
    """

    def __init__(self):
        self.name = str(id(self))
        self.masters = []
        self.epochs = dict(DEFAULT_EPOCHS)

    def record_name(self):
        frame_locals = inspect.currentframe().f_back.f_locals
        primitives = {frame_locals[key]: key
                          for key in frame_locals.keys()
                          if isinstance(frame_locals[key], Primitive)}
        if self in primitives.keys():
            self.name = primitives[self]
            print("Recording name: %s (id %s)."%('{:>30}'.format("'" + self.name + "'"), str(id(self))))

    # -------------------- BASIC METHODS --------------------
    def begin(self):
        return self.epochs['begin time']

    def end(self):
        return self.epochs['end time']

    # -------------------- METADATA METHODS --------------------
    def main_class_name(self):
        return self.__class__.__name__

    def lifespan(self):
        return self.epochs['end time'] - self.epochs['begin time']

    def name(self):
        frame_locals = inspect.currentframe().f_back.f_back.f_locals
        primitives = filter_by_class(frame_locals, Primitive, option = 'inclusive')
        
        return find_name(self, primitives)



    # -------------------- SYNCHRONIZATION METHODS --------------------
    def set_times(self, times_or_object, **kwargs):
        times = extract_times(times_or_object, **kwargs)
        self.epochs['begin time'] = times[0]
        self.epochs['end time'] = times[1]
        return times

    def set_begin_time(self, begin_time_or_object, **kwargs):
        times = extract_times(begin_time_or_object, **kwargs)
        begin_time = times[0]

        self.epochs['begin time'] = begin_time

        if self.epochs['end time'] < begin_time:
            print("WARNING (%s)."% self.name),
            print("Epoch 'end time' (%ssec) could not be left before new 'begin time' (%ssec)," \
                  %(int(self.epochs['end time']/float(SECONDS)), int(begin_time/float(SECONDS)))),
            print("has been set to 'begin time'.")
            self.epochs['end time'] = begin_time
        return begin_time

    def set_end_time(self, end_time_or_object, **kwargs):
        times = extract_times(end_time_or_object, **kwargs)
        end_time = times[1]

        self.epochs['end time'] = end_time

        if self.epochs['begin time'] > end_time:
            # SOMETHING FUNNY WITH THE MESSAGE BELOW.
            # THE FIRST LINE (with "WARNING") prints, but not the rest.
            print("*********WARNING (%s)."% self.name),
            print("Epoch 'begin time' (%ssec) could not be left after new 'end time' (%ssec)," \
                  %(int(self.epochs['begin time']/float(SECONDS), int(end_time/float(SECONDS))))),
            print("has been matched to 'end time'.")
            self.epochs['begin time'] = end_time
        return end_time
    
    def set_duration(self, duration, **kwargs):
        if duration < 0:
            print("WARNING (%s)."% self.name),
            print("Cannot set a negative value to duration, has been set to 0.")
            duration = 0
        if 'direction' in kwargs.keys():
            if kwargs['direction'] == 'reverse':
                self.epochs['begin time'] = self.epochs['end time'] - duration
        else:
            self.epochs['end time'] = self.epochs['begin time'] + duration
        return duration

    def delay(self, dt):
        self.epochs['begin time'] += dt
        self.epochs['end time'] += dt
        return dt


    def shift_to_begin_at(self, begin_time_or_object, **kwargs):
        times = extract_times(begin_time_or_object, **kwargs)
        if ('epoch' in kwargs.keys()) and (kwargs['epoch'] == 'end time'):
            begin_time = times[1]
        else:
            begin_time = times[0]

        return Primitive.delay(self, begin_time - self.epochs['begin time'])

    def shift_to_end_at(self, end_time_or_object, **kwargs):
        times = extract_times(end_time_or_object, **kwargs)
        if ('epoch' in kwargs.keys()) and (kwargs['epoch'] == 'begin time'):
            end_time = times[0]
        else:
            end_time = times[1]

        return Primitive.delay(self, end_time - self.epochs['end time'])


    # -------------------- FEEDBACK/MONITORING METHODS
    def print_identity(self, indent = '', **kwargs):
        indent = indent

        print(indent),
        print("\bid: %s"%id(self)),
        print(' '*4),
        print('{0:<14}'.format('(' + self.name + ')')),
        print(' '*2),
        print('{0:<10}'.format('[' + self.main_class_name() + ']')),


    def print_epochs(self, indent = '', **kwargs):
        indent = indent
        self.print_identity(indent = indent, **kwargs)
        print(' '*4),
        print("begins: %ssec,"%('{0:>4}'.format(str(int(self.epochs['begin time']/float(SECONDS)))))),
        print(' '*4),
        print("ends: %ssec"%'{0:>4}'.format(str(int(self.epochs['end time']/float(SECONDS))))),
        print(' '*4),
        print('{0:>8}'.format('(' + str(int(self.lifespan()/float(SECONDS))) + 'sec)')),

    def report(self, indent = '', **kwargs):
        self.w = 14
        w = self.w
        indent = indent
        if 'primitives' in kwargs.keys():
            primitives = kwargs['primitives']
        else:
            frame_locals = inspect.currentframe().f_back.f_locals
            primitives = filter_by_class(frame_locals, Primitive, option = 'inclusive')

        print(indent),
        print("\bid: %s"%id(self))

        print(indent + ' '*2),
        print(str('{0:<' + str(w) + '}').format('name') + ':'),
        print(' '*2),
        print('{0:<14}'.format(find_name(self, primitives)))

        print(indent + ' '*2),
        print(str('{0:<' + str(w) + '}').format('class') + ':'),
        print(' '*2),
        print('{0:<14}'.format(self.main_class_name()))

        print(indent + ' '*2),
        print(str('{0:<' + str(w) + '}').format('epochs') + ':'),
        print(' '*2),
        print("%ssec"%('{0:>4}'.format(str(int(self.epochs['begin time']/float(SECONDS)))))),
        print(' '*2 + '-' + ' '*2),
        print(" %ssec"%'{0:>4}'.format(str(int(self.epochs['end time']/float(SECONDS))))),
        print(' '*4),
        print('{0:>8}'.format('(' + str(int(self.lifespan()/float(SECONDS))) + 'sec)'))

        if self.masters == []:
            print(indent + ' '*2),
            print(str('{0:<' + str(w) + '}').format('no masters'))
            return
        elif len(self.masters) == 1:
            print(indent + ' '*2),
            print(str('{0:<' + str(w) + '}').format('1 master') + ':'),
        else:
            print(indent + ' '*2),
            print(str('{0:<' + str(w) + '}').format(str(len(self.masters)) + ' masters') + ':'),
        master = self.masters[0]
        print(' '*3 + '+ '),
        print("\bid: %s"%id(master)),
        print(' '*2),
        print('{0:<14}'.format('(' + find_name(master, primitives) + ')'))
        
        for master in self.masters[1:]:
            print(indent + ' '*(w+8) + '+ '),
            print("\bid: %s"%id(master)),
            print(' '*2),
            print('{0:<14}'.format('(' + find_name(master, primitives) + ')'))

if __name__ == '__main__':

    prim0 = Primitive()
    prim1 = Primitive()


    print(prim0.name)
    prim0.record_name()
    print(prim0.name)


