import tkinter
import glob
from PIL.ExifTags import GPSTAGS
from PIL.ExifTags import TAGS
from PIL import Image
import reverse_geocoder as rg
from pprint import pprint
import datetime

# Initialize the main window
window = tkinter.Tk()
# Size windows to 400 x 400px
window.minsize(400, 400)
# Give your window a title
window.title("Photo To Location")
# Set Icon
window.wm_iconbitmap("window_icon.ico")

# Place labels
label = tkinter.Label(window, text="Coordinates:")
label.place(x=10, y=10)

label2 = tkinter.Label(window, text="Location:")
label2.place(x=10, y=30)


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
                # raise ValueError("No EXIF geo_tagging found")
                error = 1
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


def convert(date_time):
    format = '%Y:%m:%d' # The format
    datetime_str = datetime.datetime.strptime(date_time, format)
    return datetime_str


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
def press2():
    print("start")
    path = "D:\\OneDrive\\1.Important\\Backups-Pictures\\2015\\03-March\\"
    files = [f for f in glob.glob(path + "**/*.jpg", recursive=True)]
    # coord = []
    visited_cities = []
    visited_cities_clean = []
    for f in files:
        # print(f)
        try:
            exif = get_exif(f)
            geo_tags = get_geotagging(exif)
            # label.config(text=f"Coordinates: {get_coordinates(geo_tags)}")
            # coord.append(get_coordinates(geo_tags))
            results = rg.search(get_coordinates(geo_tags), mode=1)
            city = results[0].get('name') + ", "
            state = results[0].get('admin1') + ", "
            country = results[0].get('cc')
            datum = geo_tags['GPSDateStamp']
            year = str(convert(datum).year)
            month = str(convert(datum).month)

            visited_cities.append(city + state + country + "|" + year+":"+month)

            print("Location:" + city + state + country + " | " + f)
            for word in visited_cities:
                if word not in visited_cities_clean:
                    visited_cities_clean.append(word)
            label2.config(text=f"Location: {city}{state}{country}")
        except:
            # print("GPS Data Missing in " + f)
            error = 2
    print("clean:")
    pprint(visited_cities_clean)
    print("end")


# Place 'Change Label' button on the window
button = tkinter.Button(window, text="Button", command=press2)
button.place(x=10, y=60)
button2 = tkinter.Button(window, text="ListFiles", command=press2)
button2.place(x=10, y=90)

# Show new window
window.mainloop()
