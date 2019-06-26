# import Image and the graphics package Tkinter
#from Tkinter import *
#import Tkinter
#import Image
#import ImageTk

from PIL import Image
from Tkinter import *

# http://effbot.org/imagingbook/image.htm

# open a SPIDER image and convert to byte
format
im = Image.open('Running.jpg').convert2byte()

root = Tkinter.Tk()  
# A root window for displaying objects

 # Convert the Image object into a TkPhoto 
object
tkimage = ImageTk.PhotoImage(im)

Tkinter.Label(root, image=tkimage).pack() 
# Put it in the display window

root.mainloop() # Start the GUI