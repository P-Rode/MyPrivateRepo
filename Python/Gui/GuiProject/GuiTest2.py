# A GUI displaying a background picture
from tkinter import *
# create the window
root = Tk()
root.title("GUI program")
root.geometry("640x510")
# create a frame in the window to hold widgets
app = Frame(root)
app.grid()
# create a label in the frame
lbl = Label(app, text = "Hi, my name is Greer!")
lbl.grid()
# kick off the windows loop
root.mainloop()
# load background image
def main():
    room_image = load_image("Running.jpg")
    background = room_image
    the_room = Room(image = room_image,
    screen_width = 100,
    screen_height = 500,
    fps = 50)
    add(the_room)
main()