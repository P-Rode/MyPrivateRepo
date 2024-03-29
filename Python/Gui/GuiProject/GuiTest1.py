#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
#from Tkinter import *
from Tkinter import Tk, Frame, BOTH
from PIL import Image, ImageTk


#mGui = Tk()

#mn = 450
#extHight = 450
#extWidth = 450
#locationYaxis = 100
#locationXaxis = 100


#mGui.geometry("450x450+100+100")
#mGui.title("Test")

# Only used in windows
#mGui.mainloop()

"""
This script centers a small
window on the screen. 

author: Jan Bodnar
last modified: January 2011
website: www.zetcode.com
"""


class Example(Frame):
  
    def __init__(self, parent):
        Frame.__init__(self, parent, background="white")   
         
        self.parent = parent
        self.parent.title("Centered window")
        self.pack(fill=BOTH, expand=1)
        self.centerWindow()

    def centerWindow(self):
      
        w = 290
        h = 150

        sw = self.parent.winfo_screenwidth()
        sh = self.parent.winfo_screenheight()
        
        x = (sw - w)/2
        y = (sh - h)/2
        self.parent.geometry('%dx%d+%d+%d' % (w, h, x, y))

def main():
  
    root = Tk()
    ex = Example(root)
    root.mainloop()  


if __name__ == '__main__':
    main()
    
#image = Image.open("lenna.jpg")
#photo = ImageTk.PhotoImage(image)