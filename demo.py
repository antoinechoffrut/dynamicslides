# demo.py
# Mo 15 Oct 2018
# Antoine Choffrut
#
# Short demo of DynamicSlides

import os
import sys
import time
import Tkinter
import math
from PIL import Image
import aggdraw

from constants import *
from helpers import *
from graphic import Graphic
from colors import *
from curve import Rectangle, Polyline
from container import Container, Compound, TexObject
from effect import Fade, Travel, Zoom, Spin, Reveal, ThreeBlueOneBrown, Trace, Trickle, Wring
from monitor import Timeline, Sketch
from camera import Camera

if __name__ == '__main__':


    os.system('clear')
    
    print("~"*60)
    # print("This is %s." %os.path.basename(sys.argv[0]))
    print("Demo for 'DynamicSlides'")
    print("https://github.com/antoinechoffrut/dynamicslides")
    print("~"*60)

    roottimeline = Tkinter.Tk()
    rootsketch = Tkinter.Tk()

    # CREATE GRAPHICS
    texobject0 = TexObject(expression = "DynamicSlides\dots")
    texobject0.record_name()
    texobject0.set_brush_color(CORAL)
    texobject0.change_anchor_to(texobject0.base_center())
    texobject0.move_to(CENTER)
    texobject1 = TexObject(expression = "\dots combines LaTeX: $e^{i\pi}+1=0$")
    texobject1.record_name()
    texobject1.set_brush_color(NAVAJOWHITE1)
    texobject1.change_anchor_to(texobject1.base_center())
    texobject1.move_to(CENTER)
    texobject2 = TexObject(expression = "\dots to graphics\dots")
    texobject2.record_name()
    texobject2.set_brush_color(NAVAJOWHITE1)
    texobject2.change_anchor_to(texobject2.base_center())
    texobject2.move_to(CENTER)
    rect0 = Rectangle(anchor = ORIGIN, width = 0.5*W, height = 0.5*H)
    rect0.record_name()
    rect0.set_pen_color(COBALT)
    rect0.set_pen_width(4)
    rect0.set_brush_color(MAGENTA)
    rect0.move_to((W/4, H/4))
    # rect1 = Rectangle(anchor = ORIGIN, width = 0.5*W, height = 0.5*H)
    # rect1.record_name()
    # rect1.set_pen_color(LIMEGREEN)
    # rect1.translate((10, 40))
    # texobject0 = TexObject(expression = "$y = f(x)$")
    # polyline0 = Polyline(points = (100, 100, 100, 400, 300, 700))
    # polyline0.add_effects(Trace(stage = 'intro', index = .2))


    # ADD EFFECTS
    #Compound(rect0, rect1).add_effects(Fade(), Fade('outro'))
    #texobject0.add_effects(Fade())
    texobject0.add_effects(Wring(center = (0, texobject0.base_to_waist)))
    texobject0.add_effects(Fade(stage='outro'))
    texobject1.add_effects(Zoom())
    texobject1.add_effects(Fade(stage='outro'))
    texobject2.add_effects(Travel())
    rect0.add_effects(Trace())


    # SYNCHRONIZE
    # rect0.set_end_time((0*SECONDS, 14*SECONDS))
    # rect1.set_times((1*SECONDS, 5*SECONDS))
    # texobject0.set_end_time(3*SECONDS)
    # rect0.shift_to_begin_at(texobject0, epoch='end time')
    texobject1.shift_to_begin_at(texobject0, epoch='end time')
    texobject2.shift_to_begin_at(texobject1, epoch='end time')
    rect0.shift_to_begin_at(texobject2, epoch='end time')



    # LOAD TO CAMERA
    camera = Camera(texobject0, texobject1, texobject2, rect0)
    # camera = Camera(texobject0, rect0)
    #camera = Camera(rect0, rect1, texobject0)
    #camera = Camera(rect0)
    #camera = Camera(polyline0)


    timeline = Timeline(roottimeline, texobject0, texobject1, texobject2, rect0) # rect0, rect1, 
    timeline.refresh()

    sketch = Sketch(rootsketch, texobject0, texobject1, texobject2, rect0)
    sketch.display()
    
    #camera.capture()
    camera.roll()

    # ============== END OF SCRIPT ================================
    
    print("="*80)
    print("END OF SCRIPT.")
    print("="*80)
    rootsketch.mainloop()
    roottimeline.mainloop()
    # ============================================================
