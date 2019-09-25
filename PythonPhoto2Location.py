import tkinter
from PIL.ExifTags import GPSTAGS
from PIL.ExifTags import TAGS
from PIL import Image
import requests
from shapely.geometry import mapping, shape
from shapely.prepared import prep
from shapely.geometry import Point

# Initialize the main window
window = tkinter.Tk()
# Size windows to 400 x 400px
window.minsize(400, 400)
# Give your window a title
window.title("Photo To Location")
# Set Icon
window.wm_iconbitmap("pacman.ico")

# Place 'Hello World' label on the window
label = tkinter.Label(window, text="Click the Button")
# Place label at coordinates x=10 and y=10 (top right hand corner)
label.place(x=10, y=10)
countries = {}
data = requests.get("C:\\code\\Python\\PythonPhoto2Location\\countries.geojson").json()
for feature in data["features"]:
    geom = feature["geometry"]
    country = feature["properties"]["ADMIN"]
    countries[country] = prep(shape(geom))


def get_country(lon, lat):
    point = Point(lon, lat)
    for country, geom in countries.tems():
        if geom.contains(point):
            return country

    return "unknown"


def get_labeled_exif(exif):
    labeled = {}
    for (key, val) in exif.items():
        labeled[TAGS.get(key)] = val
    return labeled


def get_exif(filename):
    image = Image.open(filename)
    image.verify()
    return image._getexif()


def get_geotagging(exif):
    if not exif:
        raise ValueError("No EXIF metadata found")
    geo_tagging = {}
    for (idx, tag) in TAGS.items():
        if tag == 'GPSInfo':
            if idx not in exif:
                raise ValueError("No EXIF geo_tagging found")

            for (key, val) in GPSTAGS.items():
                if key in exif[idx]:
                    geo_tagging[val] = exif[idx][key]
    return geo_tagging


def get_decimal_from_dms(dms, ref):
    degrees = dms[0][0] / dms[0][1]
    minutes = dms[1][0] / dms[1][1] / 60.0
    seconds = dms[2][0] / dms[2][1] / 3600.0
    if ref in ['S', 'W']:
        degrees = -degrees
        minutes = -minutes
        seconds = -seconds
    return round(degrees + minutes + seconds, 5)


def get_coordinates(geotags):
    lat = get_decimal_from_dms(geotags['GPSLatitude'], geotags['GPSLatitudeRef'])
    lon = get_decimal_from_dms(geotags['GPSLongitude'], geotags['GPSLongitudeRef'])
    return lat, lon


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
    path = 'C:\\code\\Python\\PythonPhoto2Location\\testimages\\20150927_174958.jpg'
    # geo_tags = get_geotagging(exif)
    exif = get_exif(path)
    geo_tags = get_geotagging(exif)
    print(get_coordinates(geo_tags))
    # print(geo_tags)
    label.config(text=f"Coordinates: {get_coordinates(geo_tags)}")
    print(get_country(10.0, 47.0))


# Place 'Change Label' button on the window
button = tkinter.Button(window, text="Button", command=press)
# Place label at coordinates x=10 and y=10 (top right hand corner)
button.place(x=10, y=40)

# Show new window
window.mainloop()
