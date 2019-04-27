import tkinter
# 1988 - The Tcl (Tool Command Language) programming language was created (cross-platform, dynamic, open source).
# 1991 - Tk extension came to Tcl, enabling building of GUIs (graphical user interfaces) natively in Tcl (Tcl/TK).
# Tk provided all basic widgets (canvas, textbox, button, label) needed for the development of native look/feel apps in Windows, Linux, Mac OS, Unix.
# 1999 - Fredrik Lundh wrote a Tkinter (TK + Interface) as a Python binding/interface to the Tk GUI toolkit.
# 2000 - Tkinter became de facto a standard GUI. In Python 3+, Tkinter is shipped as part of Linux, Windows and Mac OS X installs of Python.

# Initialize the main window
window = tkinter.Tk()
# Size windows to 400 x 400px
window.minsize(400, 400)
# Give your window a title
window.title("Application Name")
# Set Icon
window.wm_iconbitmap("pacman.ico")

# Place 'Hello World' label on the window
label = tkinter.Label(window, text="Click the Button")
# Place label at coordinates x=10 and y=10 (top right hand corner)
label.place(x=10, y=10)


# Function to find the screen dimensions, calculate the center and set geometry
def center(win):
    # Call all pending idle tasks - carry out geometry management and redraw widgets.
    win.update_idletasks()
    # Get width and height of the screen
    width = win.winfo_width()
    height = win.winfo_height()
    # Calculate geometry
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    # Set geometry
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


# Center Window on Screen
center(window)

# Initialize counter
counter = 0

# Define button press function
def press():
    # use globally set counter variable
    global counter
    # count each button press
    counter = counter + 1
    # set label
    label.config(text=f"Button clicked: {counter} times")


# Place 'Change Label' button on the window
button = tkinter.Button(window, text="Button", command=press)
# Place label at coordinates x=10 and y=10 (top right hand corner)
button.place(x=10, y=40)

# Show new window
window.mainloop()
