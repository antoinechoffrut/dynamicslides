# What is `dynamicslides`?  
This project is a tool to create videos with animated text and graphics.
These can be thought of as dynamic slide presentations.
There are of course several applications which already do this,
but the important feature is this project is that it allows to incorporate
text generated with LATEX, in particular elegant mathematical equations.


The video [*"Nash's twist and the lazy cyclist"*](https://youtu.be/KgHTeqdkTPM),
from my youtube channel [100-second mathematics](https://www.youtube.com/channel/UCmFg_nmPhu2Uvy5y4XfnnYA),
gives an idea of what `dynamicslides` can do.

This Gist explains how to use the program
and how it is structured.

# Genesis of this project
Like most mathematicians working in academia, I use LATEX to type my articles as well as to create slide presentations (most people would use [Beamer](https://www.sharelatex.com/learn/Beamer)).  LATEX offers high quality typography, especially when it comes to mathematical equations, but not only.

In recent years I had decided to create videos explaining my research.  This I started to do by incorporating slides (in pdf) of existing presentations I had already done into a video using Apple's iMovie (and added voice-over).  (The graphics were actually generated in [METAPOST](https://tug.org/metapost.html).)  The outcome was not bad and I have posted a few of these videos on my youtube channel ["100-second mathematics"](https://www.youtube.com/channel/UCmFg_nmPhu2Uvy5y4XfnnYA?view_as=subscriber).

On ther other hand there was definitely room for improvement.  I am really fond of Grant Anderson's [3Blue1Brown](https://www.youtube.com/channel/UCYO_jab_esuFRV4b17AJtAw)'s videos and this was very much the looks of videos I wished I could create.  Eventually I read his [FAQ](http://www.3blue1brown.com/about/) page and learned that he creates his videos "from scratch" in Python.  

Of course I knew about Python and had contemplated learning it if only out of curiosity.  Having no experience in Python nor in object-oriented programming, I was not able to use Grant Anderson's code which he posted on his GitHub account.  This is when I decided that I was going to create my own Python application.

Just for the fun and challenge.

Within about four months I went from `print('hello world')` to a pretty reasonably well structured programme which I can now use to create videos with simple yet elegant and somewhat sophisticated visual effects.  Certainly not of the quality of 3Blue1Brown videos, but on the other hand I wouldn't know how else to make those videos (and without paying...). Remember, one of the important features is the ability to incorporate mathematical equations generated from LATEX.  Also, paraphrasing Grant Anderson, one very appealing aspect of this project is that it is my own tool.  Furthermore, it gives me the freedom to implement any visual effect that I can think up, something that one cannot always do even with a very sophisticated software, precisely because it is limited to a fixed set of functionalities (which of course can potentially be combined in extremely elaborate ways).  Quite frankly, I simply wanted to take up the challenge of learning a new programming paradigm (object-oriented), a new programming language that has become one of go-to languages in industry, and to entirely design an application from scratch with a real and meaningful purpose.

# Usage
## Creating elements: text and graphics
### Example 1: text followed by equation
The video of this example is available [here](https://www.youtube.com/watch?v=XoPexCjKsY8).  
The following
```
text = TexObject("Euler's identity")
equation = TexObject("$e^{i\pi} + 1 = 0$")
equation.move_after(text)
Compound(text, equation).add_effects(Fade(stage = 'in'), Fade(stage = 'out'))
```
creates a text element (*"Euler's identity"*) which will appear for three seconds (default value, customizable),
followed by another text element with the corresponding equation (also three seconds).
Both text elements have *fade in* and *fade out* effects.

### Example 2: tracing an arrow along a broken line
The video of this example is available [here](https://youtu.be/3XZ6AfuRnJY).  
The following
```
polyline = Polyline((300, 300, 500, 500, 700, 400, 900, 600, 1100, 500, 1300, 700, 1500, 600, 1700, 800, 1900, 300))
polyline.add_decoration({'type': 'arrow', 'position': 'tip'})
polyline.set_pen_color((255, 0, 0))
polyline.add_effects(Trace(stage = 'in', index = 0), Trace(stage = 'out', index = 1))
```
will
- create a broken line with a life span set to 3 seconds by default,
- add an arrow at the tip,
- set the color to red (RGB code = `(255, 0, 0)`), and
- add *trace* effects at the beginning and the end of its lifespan.

### Example 3: a rectangle and a square (and geometric transformations)
The video of this example is available
[here](https://youtu.be/biB14icc3Ok).  

To create the rectangle (with default dimensions) and rotate it by 45 degrees:
```
rectangle = Rectangle()
rectangle.rotate(0.25*math.pi)
```

To create the square (with specified `width` and `height`) and place it (according to position specified in `anchor`):
```
square = Rectangle(anchor = (W/4, H/4), width = H/3, height = H/3)
```
where `W` and `H` are the width and height of the image (set by default to 1980 and 1080 respectively).

To change its appearance (outline color, width of pen, and fill color):
```
square.set_pen_color((255, 0, 0)
square.set_pen_width(3)
square.set_brush_color((227, 207, 87))
square.close()
```

To synchronize the rectangle and the square:
```
rectangle.set_duration(5)
square.move_after(rectangle, offset = -2)
```

To add effects:
```rectangle.add_effects(Travel(stage = 'in'), Zoom(stage = 'out'))
square.add_effects(Zoom(stage = 'in'), Fade(stage = 'out'))
```

## Creating the video
To create the video corresponding to Example 1 for example:
```
camera = Camera(text, equation)
camera.roll()
```
This will
- create the frames in `.png`;
- convert the frames in `.jpg`;
- invoke `ffmpeg` to generate the video in `.mp4` from the `.jpg` files.

## Performance/Benchmark
On my laptop (a MacBook Pro running on High Sierra, with a 2.5GHz Intel Core i7), for a resolution of  
- **width = 1920 points**  
- **height = 1080 points**

an empty frame (one without any element in it) takes about
- **0.17 seconds** to generate a `.png` image and
- **0.15 seconds** to convert each `.png` image to `.jpg`.
This is because it takes quite a bit of time to store an image to memory and to retrieve it.
Creating the elements themselves does not take very long (relatively speaking).
For examples, for the video [*"Nash's twist and the lazy cyclist"*](https://youtu.be/KgHTeqdkTPM) (2 minutes and 10 seconds)
it takes about **17 seconds** to generate all of the graphical elements.
For comparison, creating the image files and the video from them takes on the order of **40 minutes**.


## Streamlining the workflow
For simple examples, such as Example 1 and Example 2, the above code is sufficient.
But for more complex videos, which last longer, and with a higher frame rate, 
it very quickly becomes very tedious to work with just the type of tools that are illustrated above.

This means that it takes over 20 seconds to generate a video containing just a single object lasting 3 seconds.
Making even small changes when there are just a couple of elements quickly starts to feel tedious.

I have added two features to speed up the process of creating the videos.

### Timeline
I have found that the most delicate, and certainly time-consuming part of creating a video,
is to **synchronize** the elements.
In addition to the class `Camera` which generates the `.mp4` file,
there is a class `Sketch` which opens up a `Tkinter` window 
with the timeline of a list of selected graphical elements.
For Example 3 above, 
```
root = Tkinter.Tk()
timeline = Timeline(root)
timeline.add_graphics(rectangle, square)
timeline.refresh()
```
will result in an image as shown below.
![timeline for Example 3 with a rectangle and a square](https://github.com/antoinechoffrut/dynamicslides/blob/master/dynamicslides-example-rectangles-timeline.png)

The times of existence for the graphical elements (`rectangle` and `square`) are indicated in blue line segments,
with red line segments superimposed to indicate the time of existence of the effects attached to them.
Here, 
- `rectangle` appears between 0 seconds and 5 seconds), with effects between 0 seconds and 1 seconds on the one hand, and another between 4 seconds and 5 seconds;
- `square` appears between 3 seconds and 6 seconds), with effects between 3 seconds and 4 seconds on the one hand, and another between 5 seconds and 6 seconds.

### Sketch
There is a class `Sketch` for a quick sketch of a selected list of graphical objects.
For Example 3 above,
```
root = Tkinter.Tk()
sketch = Sketch(root)
sketch.add_graphics(rectangle, square)
sketch.refresh()
```
produces an image as below.
![sketch for Example 3 with a rectangle and a square](https://github.com/antoinechoffrut/dynamicslides/blob/master/dynamicslides-example-rectangles-sketch.png)
Note that it only draws the contour of the elements, and does not fill them in.
This feature is only meant as a rudimentary tool for a quick check that the objects created look as they are meant to
and are placed correctly.


# Libraries and external applications
For the purpose of learning Python, I have **deliberately** chosen to program using the minimal set of packages.
The most relevant are as follows.
- `numpy` and `math` for basic mathematics;
- `Tkinter` for `Canvas` and `Tk`;
- the `Image` module from `PIL`; 
- `aggdraw`, a high-quality graphics engine for `PIL`.

In addition to these `Python` packages, 
the program *invokes* the following external applications:
- `LATEX` to create the text elements;
- `dvisvgm` to convert `.dvi` files to `.svg` files;
- `convert` to convert `.png` files (created by `PIL`'s `Image` module) to `.jpg` files; and
- `ffmpeg` to generate the video in `.mp4` format from the `.jpg` image files.

# Curves
The most basic graphical element is a *curve*.
Every curve is represented as a Bézier curve, and therefore encoded via:
- **control points**, and
- **commands**, such as `M`, `L`, `Q`, `S` and `C`.
The coordinates of the control points in fact represented via
- an `anchor`, which is a point on the canvas;
- the coordinates of the control points, relative to the `anchor`.
The position of the `anchor` can be changed, and the coordinates of the control points,
relative to the `anchor`, will automatically be upated (and the position of the curve will not change).
This choice of representation turns out to be very convenient when performing **geometric transformations**,
and in particular the standard affine transformations:
- **translation**;
- **rotation**;
- **homothety** (rescaling in the x- and y-direction).


# On generating and manipulating text
All text elements are generated with `LATEX`.
This results in a `.dvi` file, 
which is then converted to a `.svg` file, with the `no fonts` option,
resulting in Bézier curves (for most, though not all glyphs).
Now that the text is represented as a collection of Bézier curves,
it becomes easy to create visual affects by applying (mostly affine) geometric transformations on them.

A text element is therefore a collection of (Bézier) curves and are drawn just like any other curves.

# Features
## Synchronization
*To do...*
## Geometric transformations
*To do...*
