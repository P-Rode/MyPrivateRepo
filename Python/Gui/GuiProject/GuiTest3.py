# https://www.youtube.com/watch?v=82FK-cMbQ04

from Tkinter import *
#from Tkinter import Label, Button
from distutils.cmd import Command
from Tkconstants import BOTTOM

root = Tk()
root.title("Button App")
Label(text = "I am a button").pack(pady = 15)

def quitapp():
    root.destroy()
    
Button(text="Quit", command = quitapp).pack(side=BOTTOM)
root.mainloop()