try:
    # for Python2
    from Tkinter import *
except ImportError:
    # for Python3
    from tkinter import *

from PIL import ImageTk, Image
import os

root = Tk()
starting = ImageTk.PhotoImage(Image.open("Starting.jpg"))
running = ImageTk.PhotoImage(Image.open("Running.jpg"))
stopped = ImageTk.PhotoImage(Image.open("Stopped.jpg"))
stopping = ImageTk.PhotoImage(Image.open("Stopping.jpg"))
aborted = ImageTk.PhotoImage(Image.open("Aborted.jpg"))

panel = Label(root, image = starting)
panel = Label(root, image = stopping)

panel.pack(side = "top", fill = "both", expand = "yes")
panel.pack(side = "bottom", fill = "both", expand = "yes")
root.mainloop()
