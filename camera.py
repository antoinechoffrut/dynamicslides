# camera.py
# Th 11 Oct 2018
# Antoine Choffrut
#
# Code for the class 'Camera', which essentially contains a list of 'Graphic' objects,
# with the following being the main methods.
# - 'capture': draws the selected graphics and saves it as an image file.
# - 'roll': generates all the images needed for the video, then produces an mp4 file out of them.

from constants import *
from helpers import *
from graphic import Graphic
from PIL import Image
import aggdraw
import os
import sys
import time

def create_subdirectory(dir_path, sub_name_or_keyword):
    """ Creates a subdirectory with name specified in argument 'sub_name',
    within directory with path specified in argument 'dir_path',
    if subdirectory does not already exists.
    Returns 'None' and prints error message if parent directory does not exist.
    Returns path of subdirectory otherwise.
    """
    if not os.path.exists(dir_path):
        print("ERROR (global function 'create_subdirectory')."),
        print("No directory with path '%s'."% dir_path)
        return
    #
    if sub_name_or_keyword == 'run':
        date_and_time = [time.localtime()[i] for i in range(5)]
        date_and_time[0] = '{:04d}'.format(int(date_and_time[0]))
        for i in range(1,5):
            date_and_time[i] = '{:02d}'.format(int(date_and_time[i]))
        sub_name =  '-'.join(date_and_time[0:4]) + 'h' + date_and_time[4] +'min'
    else:
        sub_name = sub_name_or_keyword
    #
    result = os.path.join(dir_path, sub_name)
    #
    if not os.path.exists(result):
        os.mkdir(result)
    return result




class Camera(object):
    def __init__(self, *args):
        self.graphics = list(set([arg for arg in args if isinstance(arg, Graphic)]))
        self.img = Image.new('RGBA', (W, H), DEFAULT_BACKGROUND_COLOR)
        self.canvas = aggdraw.Draw(self.img)
        self.archive_subdirectory = create_subdirectory(\
                                                        os.getcwd(),
                                                        'ARCHIVES')

    def erase(self):
        self.img = Image.new('RGBA', (W, H), DEFAULT_BACKGROUND_COLOR)
        self.canvas = aggdraw.Draw(self.img)

    def main_class_name(self):
        return 'Camera'

    def  add_graphics(self, *graphics):
        for graphic in graphics:
            if not graphic in self.graphics:
                self.graphics.append(graphic)


    def remove_graphics(self, *graphics):
        if 'all' in graphics:
            self.graphics = []
            return
        for graphic in graphics:
            if graphic in self.graphics:
                self.graphics.remove(graphic)

    def capture(self, show_capture = True, **kwargs):
        for graphic in self.graphics:
            if 'frame' in kwargs.keys():
                t = kwargs['frame']
                graphic.draw(self.canvas, t)
            else:
                graphic.draw(self.canvas)                
        self.canvas.flush()

        #
        if 'path' in kwargs.keys():
            image_subdirectory = kwargs['path']
            if not 'index' in kwargs.keys():
                print("WARNING (method capture).")
                print(" "*2),
                print("Option 'index' must be provided along with option 'path'.")
                print(" "*2),
                print("Calling 'capture' with option 'path' is meant to be used by the 'roll' method only.")
                return
            else:
                index = kwargs['index']
            if not 'width' in kwargs.keys():
                width = 4
            else:
                width = kwargs['width']
                
            image_file_name = str('IMAGE-{:0' + str(width) + 'd}').format(index) + '.png'
        else:
            run_subdirectory = create_subdirectory(self.archive_subdirectory, 'run')
             
            image_subdirectory = create_subdirectory(run_subdirectory, 'CAMERA-CAPTURES')
            hash_string = str(sum([hash(graphic) for graphic in self.graphics]))
            image_file_name = 'CAMERA-CAPTURE-' + str(hash(self)) + '.png'
        image_file_path = os.path.join(image_subdirectory, image_file_name)
        #
        self.img.save(image_file_path)
        if show_capture == True:
            print("Image file has been saved under %s."%image_file_name)
            print("Full path:")
            os.system(' '.join(['open -a preview', image_file_path]))
            
            
    def frame_count(self):
        end_times = [graphic.epochs['end time'] for graphic in self.graphics]
        begin_times = [graphic.epochs['begin time'] for graphic in self.graphics]
        if end_times == []:
            return 0, 0
        else:
            return int(min(begin_times)), int(max(end_times))


    def roll(self):
        run_subdirectory = create_subdirectory(self.archive_subdirectory, 'run')
        video_subdirectory = create_subdirectory(run_subdirectory, 'VIDEOS')
        image_subdirectory = create_subdirectory(video_subdirectory, 'IMAGES')
        #
        first_frame, last_frame = self.frame_count()
        N = last_frame - first_frame

        print("Generating frames (.png):")
        start_time = time.time()
        for t in range(N):
            print("\rframe: %s (%s)" % (\
                                        str('{:>'+ str(len(str(N))) + '}').format(t),
                                        N - 1)),

            self.erase()
            self.capture(\
                         show_capture = False,
                         path = image_subdirectory,
                         index = t,
                         frame = t + first_frame,
                         width = len(str(N)))
            elapsed_time = time.time() - start_time
            est_time = (N - t - 1)*elapsed_time/(t+1)
            est_min = int(est_time)/60
            est_sec = int(est_time) % 60
            total_est_time = elapsed_time + est_time
            print(" | elapsed time: %s min %s sec" %(int(elapsed_time)/60, int(elapsed_time) %60)),
            print(" | total estimated time: %s min %s sec" % (int(total_est_time)/60, int(total_est_time) %60)),
            print(" | estimated time remaining: %s min %s sec" % (est_min, est_sec)),
            sys.stdout.flush()
        print('')
        total_time = time.time() - start_time
        total_min = int(total_time)/60
        total_sec = int(total_time) % 60
        print("It took %s min and %s sec to generate the %s frames, for an average of %s sec per frame." \
              % (total_min, total_sec, N, '{:.2f}'.format(total_time/N)))

        print("Converting to .jpg:")
        os.chdir(image_subdirectory)
        start_time = time.time()
        for t in range(N):
            image_name = str('IMAGE-{0:0' + str(len(str(N))) + 'd}').format(t)
            print("\r{0}.png ".format(image_name)),
            print("(%s)" % (N - 1)),
            command = ['convert',
                       image_name + '.png',
                       image_name + '.jpg']
            os.system(' '.join(command))
            elapsed_time = time.time() - start_time
            est_time = (N - t - 1)*elapsed_time/(t+1)
            est_min = int(est_time)/60
            est_sec = int(est_time) % 60
            total_est_time = elapsed_time + est_time
            print(" | elapsed time: %s min %s sec" %(int(elapsed_time)/60, int(elapsed_time) %60)),
            print(" | total estimated time: %s min %s sec" % (int(total_est_time)/60, int(total_est_time) %60)),
            print(" | estimated time remaining: %s min %s sec" % (est_min, est_sec)),
            sys.stdout.flush()
        print('')
        total_time = time.time() - start_time
        total_min = int(total_time)/60
        total_sec = int(total_time) % 60
        print("It took %s min and %s sec to convert the %s image files, for an average of %s sec per image file." \
              % (total_min, total_sec, N, '{:.2f}'.format(total_time/N)))

        hash_string = str(sum([hash(graphic) for graphic in self.graphics]))
        video_file_path = os.path.join(video_subdirectory,
                                       str('VIDEO-' + hash_string + '.mp4'))
        print("The video file path is:")
        print(video_file_path)
        

        astring = 'IMAGE-%0' + str(len(str(N))) + 'd.jpg'
        commands = [
            'ffmpeg',
            ' -framerate',
            str(F_RATE),
             ' -i ',
            astring,
            '-pix_fmt',
            'yuv420p',
            " -vf 'scale=trunc(iw/2)*2:trunc(ih/2)*2'",
            video_file_path]

        start_time = time.time()
        print("\n\nCheck what command is sent:\n\n")
        # print(' '.join(commands))
        os.system(' '.join(commands))
        total_time = time.time() - start_time
        print('')
        print("It took %s min and %s sec for ffmpeg to generate the .mp4 file from the %s image files." \
              % (int(total_time)/60, int(total_time) % 60, N))

        start_time = time.time()
        print("Deleting the .jpg image files..."),
        os.system('rm *.jpg')
        print("in %s sec." %int(time.time() - start_time))
        os.system('open -a "quicktime player" '+ video_file_path)

        #
        print("Images for video have been saved in directory %s."\
              %image_subdirectory)
        

if __name__ == '__main__':
    from colors import *
    from curve import Rectangle, Polyline
    from container import Container, Compound, TexObject
    from effect import Fade, Travel, Zoom, Spin, Reveal, ThreeBlueOneBrown, Trace, Trickle, Wring
    from monitor import Timeline
    import os
    import sys
    import Tkinter
    import math


    os.system('clear')
    
    print("~"*60)
    print("This is %s." %os.path.basename(sys.argv[0]))
    print("~"*60)

    #roottimeline = Tkinter.Tk()

    # CREATE STANDALONES
    rect0 = Rectangle(anchor = ORIGIN, width = 0.25*W, height = 0.25*H)
    rect0.record_name()
    #rect0.set_pen_color(COBALT)
    #rect0.set_brush_color(MAGENTA)
    rect1 = Rectangle(anchor = ORIGIN, width = 0.5*W, height = 0.5*H)
    rect1.record_name()
    rect1.set_pen_color(LIMEGREEN)
    rect1.translate((10, 40))
    texobject0 = TexObject(expression = "$y = f(x)$")
    texobject0.record_name()
    texobject0.move_to(CENTER)
    texobject0.set_brush_color(WHITE)
    polyline0 = Polyline(points = (100, 100, 100, 400, 300, 700))
    polyline0.add_effects(Trace(stage = 'intro', index = .2))

    # LOAD TO CAMERA
    #camera = Camera(rect0, rect1, texobject0)
    camera = Camera(texobject0)
    #camera = Camera(rect0)
    #camera = Camera(polyline0)

    # SYNCHRONIZE
    rect0.set_end_time((0*SECONDS, 14*SECONDS))
    rect0.move_to(CENTER)
    rect0.add_effects(Trace())
    #texobject0.set_end_time(3*SECONDS)

    #rect0.add_effects(Trace())
    #rect1.set_times((1*SECONDS, 5*SECONDS))
    #texobject0.set_end_time(6*SECONDS)


    # ADD EFFECTS
    #Compound(rect0, rect1).add_effects(Fade(), Fade('outro'))
    #texobject0.add_effects(Fade())
    texobject0.change_anchor_to(texobject0.base_center())
    texobject0.move_to(CENTER)
    texobject0.add_effects(Wring(center = (0, texobject0.base_to_waist)))
    #texobject0.add_effects(ThreeBlueOneBrown(stage = 'intro', order = 'increasing'))
    #texobject0.add_effects(ThreeBlueOneBrown(stage = 'outro', order = 'decreasing'))
    #texobject0.add_effects(Trickle(\
    #                               stage = 'intro',
    #                               order = 'random',
    #                               separation = (2*W, 0)))
    #texobject0.add_effects(Trickle(\
    #                               stage = 'outro',
    #                               order = 'decreasing',
    #                               separation = (2*W, 0)))

    #timeline = Timeline(roottimeline, rect0, rect1, texobject0)
    #timeline.refresh()
    
    #camera.capture()
    camera.roll()

    # ============== END OF SCRIPT ================================
    
    print("="*80)
    print("END OF SCRIPT.")
    print("="*80)
    #rootsketch.mainloop()
    #roottimeline.mainloop()
    # ============================================================
