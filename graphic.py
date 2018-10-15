# graphic.py
# Th 11 Oct 2018
# Antoine Choffrut
#
# Code for the class 'Graphic',
# which is the most basic class
# whose instance represent graphical elements taking part in the video.
# It is a subclass of the class 'Primitive'.
# The other subclass of 'Primitive' is the class 'Effect'.
# Subclasses of the class Graphic:
# + Curve
# + Container

import numpy as np
from constants import *
from geometry import *
from primitive import Primitive, filter_by_class
import inspect
import PIL as Image
import aggdraw

# ============================== FUNCTIONS ==============================
def sketch(root, cvsketch, ratio, *args):
    frame_locals = inspect.currentframe().f_back.f_locals
    graphics = filter_by_class(frame_locals, Graphic, option = 'inclusive')

    requested_graphic_names = [graphic_name for graphic_name in args if graphic_name in graphics.keys()]
    for graphic_name in requested_graphic_names:
        graphics[graphic_name].sketch(root, cvsketch, ratio)
    

def print_geometry(*args):
    print("\n"+'-'*60)
    print("GEOMETRY: anchors and corners.\n")
    frame_locals = inspect.currentframe().f_back.f_locals
    graphics = filter_by_class(frame_locals, Graphic, option = 'inclusive')

    requested_graphic_names = tuple(graphic_name for graphic_name in args if graphic_name in graphics.keys())
    for graphic_name in requested_graphic_names:
        graphics[graphic_name].print_geometry(graphics = graphics)
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
            graphics = {graphic_name: graphics[graphic_name]
                     for graphic_name in graphics.keys()
                     if graphics[graphic_name].main_class_name() == class_name}
            if not graphics == {}:
                print('+'),
                print("'%s' (%s):"%(class_name, len(graphics)))
                for graphic_name in graphics.keys():
                    graphics[graphic_name].print_geometry(graphics = graphics, indent = ' '*4 + '- ')


# ============================== CLASSES ==============================
class Graphic(Primitive):
    """ Attributes: 
    - masters
    - epochs
    - external_call 
    - anchor
    - cardinals
    """
    def __init__(self, anchor = ORIGIN, cardinals = DEFAULT_CARDINALS):
        Primitive.__init__(self)
        self.external_call = False
        self.anchor = anchor
        self.cardinals = cardinals

    def width(self):
        return np.linalg.norm(tuple_to_array(self.ne()) - tuple_to_array(self.nw()))

    def  height(self):
        return np.linalg.norm(tuple_to_array(self.nw()) - tuple_to_array(self.sw()))

    # -------------------- FEEDBACK METHODS --------------------
    def print_geometry(self, indent = '', **kwargs):
        indent = indent
        if 'graphics' in kwargs.keys():
            graphics = kwargs['graphics']
        else:
            frame_locals = inspect.currentframe().f_back.f_locals
            graphics = filter_by_class(frame_locals, Primitive, option = 'inclusive')

        self.print_identity(indent = indent, **kwargs)

        print('')
        print(indent + ' '*2),
        print('{0:<8}'.format('width') + ':'),
        print(' '*2),
        print('{0:>8}'.format(int(self.width())))
        print(indent + ' '*2),
        print('{0:<8}'.format('height') + ':'),
        print(' '*2),
        print('{0:>8}'.format(int(self.height())))
        print(indent + ' '*2),
        print('{0:<8}'.format('anchor') + ':'),
        print(' '*2),
        print('{0:>5}'.format('(' + str(int(self.anchor[0]))) \
              + ', ' \
              + '{0:<5}'.format(str(int(self.anchor[1])) + ')'))
        
        for key in ['nw', 'sw', 'se', 'ne']:
            print(indent + ' '*2),
            print('{0:<8}'.format(key) + ':'),
            print(' +'),
            print('{0:>5}'.format('(' + str(int(self.cardinals[key][0]))) \
                  + ', ' \
                  + '{0:<5}'.format(str(int(self.cardinals[key][1])) + ')'))

    def sketch(self, root, cvsketch, ratio = 0.5, color = 'white', width = 1):
        """Traces a polygon through the four corners of the instance"""
        s = ratio*root.winfo_screenwidth()/float(W)
        xy = self.corners()
        cvsketch.create_polygon(scale(s, xy), outline = color, fill = '', width = width)

        d = W/240
        xy = (0, d, 0, -d)
        xy = translate(xy, self.anchor)
        cvsketch.create_line(scale(s, xy), fill = 'green', width = 3)

        xy = (d, 0, -d, 0)
        xy = translate(xy, self.anchor)
        cvsketch.create_line(scale(s, xy), fill = 'green', width = 3)


    # -------------------- SYNCHRONIZATION METHODS --------------------
    def update_epochs(self):
        for master in self.masters:
            master.update_epochs()

    # GEOMETRIC METHODS

    def nw(self):
        return add(self.anchor, self.cardinals['nw'])

    def west(self):
        return add(self.anchor, self.cardinals['w'])

    def sw(self):
        return add(self.anchor, self.cardinals['sw'])

    def  south(self):
        return add(self.anchor, self.cardinals['s'])

    def se(self):
        return add(self.anchor, self.cardinals['se'])

    def east(self):
        return add(self.anchor, self.cardinals['e'])

    def ne(self):
        return add(self.anchor, self.cardinals['ne'])

    def north(self):
        return add(self.anchor, self.cardinals['n'])

    def center(self):
        return add(self.anchor, self.cardinals['c'])

    def corners(self):
        """ Returns a tuple with the (x,y)-coordinates of the four corners of the bounding box. """
        return self.nw() + self.sw() + self.se() + self.ne()

    def change_anchor_to(self, new_anchor):
        for key in self.cardinals.keys():
            self.cardinals[key] = translate(self.cardinals[key], subtract(self.anchor, new_anchor))
        self.anchor = new_anchor

    def update_cardinals(self):
        for master in self.masters:
            master.update_cardinals()

    def translate(self,v):
        self.anchor = translate(self.anchor, v)

    def homothety(self, center, sx, sy):
        self.anchor = homothety(self.anchor, center, sx, sy)
        for key in self.cardinals.keys():
            self.cardinals[key] = homothety(self.cardinals[key], ORIGIN, sx, sy)

    def rotate(self, center, angle):
        self.anchor = rotate(self.anchor, center, angle)
        for key in self.cardinals.keys():
            self.cardinals[key] = rotate(self.cardinals[key], ORIGIN, angle)

    def move_to(self, p):
        self.anchor = p

    # ==================== DRAWING METHODS ====================
    def print_to_file(self):
        img = Image.new('RGBA',(W,H),DEFAULT_BACKGROUND_COLOR)
        canvas = aggdraw.Draw(img)

        if (isinstance(self, Curve)):
            self.draw(canvas)
        elif hasattr(self, 'elements'):
            for element in self.elements:
                element.draw(canvas)
        else:
            pass

        canvas.flush()

        image_subdirectory = create_image_subdirectory()
        run_subdirectory = create_run_subdirectory(image_subdirectory)
        file_path = run_subdirectory + '/' + self.__class__.__name__ + '-' + str(hash(self)) + '-image.png'
        img.save(file_path)
        
        os.system(' '.join(['open -a preview', file_path]))
        


if __name__ == '__main__':
    import Tkinter
    root = Tkinter.Tk()
    w, h = W/2, H/2
    cvsketch = Tkinter.Canvas(root, width = w, height = h)

    cvsketch.create_rectangle(0, 0, w, h, fill = 'black')
    cvsketch.pack()

    raw_input('type in anything and press ENTER:')

    # This will create a 'Graphic' which is really only a container
    graphic0 = Graphic(anchor = (100, 300))
    graphic0.print_geometry()   # will give position of corners

    # Since all four corners are at the same location,
    # will only show as a cross
    graphic0.sketch(root, cvsketch)
    
    raw_input('type in anything and press ENTER:')

    # No visible effect since all corners coincide
    graphic0.rotate(ORIGIN, 0.25*math.pi)

    raw_input('type in anything and press ENTER:')

    graphic0.move_to((200, 50))
    graphic0.print_geometry()   # notice change in position of corners
    graphic0.sketch(root, cvsketch)

    root.mainloop()
