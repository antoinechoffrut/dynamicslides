# monitor.py
# Th 11 Oct 2018
# Antoine Choffrut
#
# Code for the class 'Monitor', which has as subclasses the classes 'Sketch' and 'Timeline'
# previously coded as separate classes.
# - The class 'Sketch' allows to visualize selected graphics using Tkinter
# (hence quicker than drawing then saving the image files).
# - The class 'Timeline' visualizes the timeline of selected graphics, also using Tkinter.


from constants import *
import Tkinter
import inspect
from primitive import Primitive, filter_by_class, current_variables
from curve import Curve
from helpers import *
from geometry import *
from graphic import Graphic
from container import get_subelements_by_class, Compound, Block

def show_and_wait(root):
    root.lift()
    root.attributes('-topmost', True)
    root.after_idle(root.attributes,'-topmost',False)

class Monitor(object):
    def  initialize_canvas(self):
        canvas = Tkinter.Canvas(self.root, width = self.w, height = self.h)
        canvas.pack()
        canvas.create_rectangle(0, 0, self.w, self.h, fill = self.bgcolor)
        return canvas

    def resize(self, ratio):
        self.ratio = ratio

    def display(self):
        pass
    
    def refresh(self):
        self.canvas.delete('all')
        self.canvas.create_rectangle(0, 0, self.w, self.h, fill = self.bgcolor)
        self.display()
        show_and_wait(self.root)

    def report(self, indent = '', **kwargs):
        w = 10
        indent = indent
        frame_locals = inspect.currentframe().f_back.f_locals

        graphics = filter_by_class(frame_locals, Graphic, option = 'inclusive')
        

        print(indent),
        print("\bid: %s"%id(self))

        print(indent + ' '*2),
        print(str('{0:<' + str(w) + '}').format('name') + ':'),
        print(' '*2),
        print('{0:<14}'.format(find_name(self, frame_locals)))

        print(indent + ' '*2),
        print(str('{0:<' + str(w) + '}').format('class') + ':'),
        print(' '*2),
        print('{0:<14}'.format(self.main_class_name()))

        print(indent + ' '*2),
        print(str('{0:<' + str(w) + '}').format('canvas') + ':'),
        print(' '*2),
        print('{0:<14}'.format(self.canvas))

        print(indent + ' '*2),
        print(str('{0:<' + str(w) + '}').format('ratio') + ':'),
        print(' '*2),
        print('{0:<14}'.format(self.ratio))

        print(indent + ' '*2),
        print(str('{0:<' + str(w) + '}').format('width') + ':'),
        print(' '*2),
        print('{0:<14}'.format(str(int(self.w))))

        print(indent + ' '*2),
        print(str('{0:<' + str(w) + '}').format('height') + ':'),
        print(' '*2),
        print('{0:<14}'.format(str(int(self.h))))

        if self.graphics == []:
            print(indent + ' '*2),
            print(str('{0:<' + str(w) + '}').format('no graphics'))
            return
        elif len(self.graphics) == 1:
            print(indent + ' '*2),
            print(str('{0:<' + str(w) + '}').format('1 graphic') + ':'),
        else:
            print(indent + ' '*2),
            print(str('{0:<' + str(w) + '}').format(str(len(self.graphics)) + ' graphics') + ':'),
        graphic = self.graphics[0]
        print(' '*3 + '+ '),
        print("\bid: %s"%id(graphic)),
        print(' '*2),
        print('{0:<14}'.format('(' + find_name(graphic, graphics) + ')'))
        
        for graphic in self.graphics[1:]:
            print(indent + ' '*(w+8) + '+ '),
            print("\bid: %s"%id(graphic)),
            print(' '*2),
            print('{0:<14}'.format('(' + find_name(graphic, graphics) + ')'))
        
    def  add_graphics(self, *graphics):
        self.graphics = list(set(self.graphics + list(graphics)))


    def remove_graphics(self, *graphics):
        if 'all' in graphics:
            self.graphics = []
            return
        for graphic in graphics:
            if graphic in self.graphics:
                self.graphics.remove(graphic)


class Timeline(Monitor):
    def __init__(self, root, *args):
        self.bgcolor = 'linen'
        self.ratio = 1
        self.root = root
        self.root.title = 'Timeline'
        self.w = self.ratio*self.root.winfo_screenwidth()
        self.h = 0.5*self.ratio*self.root.winfo_screenheight()
        self.canvas = self.initialize_canvas()
        self.graphics = list(set([arg for arg in args if isinstance(arg, Graphic)]))
        self.root.geometry(\
                           str(int(self.w)) + 'x' + str(int(self.h)) \
                           + '+0+' + str(int(0.5*self.root.winfo_screenheight())))
        
    def main_class_name(self):
        return 'Timeline'

    def chrono_order(self):
        begin_times = [graphic.epochs['begin time'] for graphic in self.graphics]
        return list(np.argsort(begin_times))

    def all_times(self):
        if self.graphics == []:
            print("WARNING (method 'all_times' of class 'Timeline')."),
            print("No graphics selected.")
        curves = get_subelements_by_class(self.graphics, [], Curve)
        result = [float(epoch)
                  for graphic in self.graphics
                  for epoch in graphic.epochs.values()]\
                 +  [float(epoch)
                     for curve in curves
                     for effect in curve.effects for epoch in effect.epochs.values()]
        return sorted(list(set(result)))
        
    def display(self):
        frame_locals = inspect.currentframe().f_back.f_locals
        prim_names = {frame_locals[key]: key
                      for key in frame_locals
                      if isinstance(frame_locals[key], Primitive)}
        self.canvas.create_text(\
                                (0.5*self.w, 0.95*self.h),
                                text = "TIMELINE (in seconds)",
                                fill = 'black',
                                anchor = 's')
        if self.graphics == []:
            print("WARNING (method 'display' of class 'Timeline')."),
            print("No graphics selected.")
            return
        TW, TH = 0.75*self.w, 0.6*self.h
        X1, X2, Y = 0.5*(self.w-TW), 0.5*(self.w+TW), (self.h + TH)/2
        xy = (X1, Y, X2, Y)
        self.canvas.create_line(xy, fill = 'black')
        all_times = self.all_times()
        begin_time, end_time = all_times[0], all_times[-1]

        #
        d = self.h/120
        #
        self.canvas.create_text(\
                                translate((X1, Y), (-d, 0)),
                                text = '{:.1f}'.format(all_times[0]/SECONDS),
                                fill = 'black',
                                anchor = 'e')
        self.canvas.create_text(\
                                translate((X2, Y), (d, 0)),
                                text = '{:.1f}'.format(all_times[-1]/SECONDS),
                                fill = 'black',
                                anchor = 'w')
        for time in all_times[1:-1]:
            x = X1 + (time - begin_time)/float(end_time - begin_time)*(X2 - X1)
            y = Y
            xy = translate((0, d, 0, -d), (x, y))
            self.canvas.create_line(xy, fill = 'black', width = 3)
            self.canvas.create_text(\
                                    translate((x, y), (0, d)),
                                    text = '{:.1f}'.format(time/SECONDS),
                                    fill = 'black',
                                    anchor = 'n')
        

        for i in range(len(self.graphics)):
            graphic = self.graphics[self.chrono_order()[i]]
            M = 12
            dy = - (i % M +1)/float(M)*TH
            #
            if isinstance(graphic, Curve):
                effects = graphic.effects
            elif isinstance(graphic, Block):
                effects = [effect
                           for element in graphic.elements if isinstance(element, Curve)
                           for effect in element.effects]
            else:
                effects = []
            #
            for effect in effects:
                x = X1 + (effect.epochs['begin time'] - begin_time) / \
                    float(end_time - begin_time)*(X2 - X1)
                y = Y + dy
                dx = (effect.epochs['end time'] - effect.epochs['begin time']) / \
                     float(end_time - begin_time)*(X2-X1)
                xy = (x, y, x + dx, y)
                self.canvas.create_line(xy, fill = 'red', width = 4)
                xy = translate((0, d, 0, -d), (x, y))
                self.canvas.create_line(xy, fill = 'red', width = 3)
                xy = (x + (effect.epochs['end time'] - effect.epochs['begin time']) / \
                      float(end_time - begin_time)*(X2-X1), y)
                xy = translate((0, d, 0, -d), xy)
                self.canvas.create_line(xy, fill = 'red', width = 3)
                self.canvas.create_line((x, y, x, Y), fill = 'red', width = 1, dash = (4, 6))
                self.canvas.create_line((x + dx, y, x + dx, Y), fill = 'red', width = 1, dash = (4, 6))

            #
            x = X1 + (graphic.epochs['begin time'] - begin_time) / \
                float(end_time - begin_time)*(X2 - X1)
            y = Y + dy
            dx = (graphic.epochs['end time'] - graphic.epochs['begin time']) / \
                 float(end_time - begin_time)*(X2-X1)


            text = graphic.name
            self.canvas.create_text(\
                                    translate((x, y), (-d, 0)),
                                    text = text,
                                    fill = 'blue',
                                    anchor = 'e')

            xy = (x, y, x + dx, y)
            self.canvas.create_line(xy, fill = 'blue', width = 1)

            xy = translate((0, d, 0, -d), (x, y))
            self.canvas.create_line(xy, fill = 'blue', width = 3)

            xy = translate((0, d, 0, -d), (x + dx, y))
            self.canvas.create_line(xy, fill = 'blue', width = 3)

            self.canvas.create_line((x, y, x, Y), fill = 'blue', width = 1, dash = (4, 6))
            self.canvas.create_line((x + dx, y, x + dx, Y), fill = 'blue', width = 1, dash = (4, 6))

                
        show_and_wait(self.root)


class Sketch(Monitor):
    def __init__(self, root, *args):

        self.bgcolor = 'black'
        self.ratio = 0.5
        self.root = root
        self.root.title = 'Sketch'
        self.w = self.ratio*self.root.winfo_screenwidth()
        self.h = self.w*H/float(W)
        self.canvas = self.initialize_canvas()
        self.graphics = list(set([arg for arg in args]))
        self.root.geometry(str(int(self.w)) + 'x' + str(int(self.h)) + '+0+0')

    
    def main_class_name(self):
        return 'Sketch'

    def display(self):
        for graphic in self.graphics:
            graphic.sketch(self.root, self.canvas, self.ratio)
        show_and_wait(self.root)

    
if __name__ == '__main__':
    from primitive import Primitive
    from curve import Rectangle
    from effect import Fade
    
    #rootsketch = Tkinter.Tk()
    #sketch = Sketch(rootsketch)
    roottimeline = Tkinter.Tk()
    timeline = Timeline(roottimeline)



    rect0 = Rectangle(anchor = ORIGIN, width = 0.25*W, height = 0.25*H)
    rect1 = Rectangle(anchor = ORIGIN, width = 0.25*W, height = 0.25*H)
    rect1.set_times((-1*SECONDS, 5*SECONDS))
    effectA = Fade()
    rect1.add_effects(effectA)
    effectA.set_duration(2*SECONDS)
    
    rect1.move_to(CENTER)

    #sketch.add_graphics(rect0, rect1)
    #sketch.display()

    timeline.add_graphics(rect0, rect1)
    timeline.report()
    timeline.display()


    #rootsketch.mainloop()
    roottimeline.mainloop()
