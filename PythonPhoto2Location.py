import calendar, datetime, glob, os, os.path, tkinter, webbrowser
from decimal import Decimal
from threading import Thread
from tkinter import *
from tkinter import filedialog
from typing import Optional, Any
import country_converter as coco
import pandas as pd
import reverse_geocoder as rg
from PIL import Image
from PIL.ExifTags import GPSTAGS
from PIL.ExifTags import TAGS
from gmplot import gmplot

# ADD YOUR OWN GOOGLE MAPS API KEY (the one below is a fake ID)
google_api_key = "IzaSyD2KMkrfQkzqNBEo-5iZDhDOlbvvDrO0dM"

# Initialize the main window and all components
window = tkinter.Tk()
window.minsize(500, 500)
window.title("Photo To Location")
window.wm_iconbitmap("window_icon.ico")
entryText = tkinter.StringVar()
textbox = tkinter.Entry(window, width=75, textvariable=entryText)
textbox.place(x=10, y=20)
link2 = Label(window, text="", fg="blue", cursor="hand2")
link2.place(x=160, y=90)
link1 = Label(window, text="", fg="blue", cursor="hand2")
link1.place(x=270, y=90)
label = tkinter.Label(window, text="")
label.place(x=10, y=80)
label2 = tkinter.Label(window, text="")
label2.place(x=10, y=96)
status_message = StringVar()
status = Label(window, textvariable=status_message, bd=1, relief=SUNKEN, anchor=W)
status.pack(side=BOTTOM, fill=X)
text = Text(window, height=22, width=59)
text.place(x=10, y=120)
cpt = 0


def get_labeled_exif(exif):
    labeled = {}
    for (key, val) in exif.items():
        labeled[TAGS.get(key)] = val
    return labeled


def get_exif(filename):
    image: Optional[Any] = Image.open(filename)
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


def converter(date_time):
    format = '%Y:%m:%d'  # The format
    datetime_str = datetime.datetime.strptime(date_time, format)
    return datetime_str


# Function to find the screen dimensions, calculate the center and set geometry
def center(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry('{}x{}+{}+{}'.format(width, height, x, y))


def ask_quit():
    window.destroy()
    exit()


def on_closing():
    root = Tk()
    root.destroy()
    window.destroy()
    exit()


def open_file_dialog():
    global cpt
    root = Tk()
    root.withdraw()
    folder_selected = filedialog.askdirectory()
    entryText.set(folder_selected)
    print("Directory to Process: " + folder_selected)
    cpt = sum([len(files) for r, d, files in os.walk(folder_selected)])
    print("Number of Files using listdir method#1 :", cpt)


def open_excel(event):
    os.startfile("results.xlsx")


def percentage(part, whole):
    return round(100 * float(part) / float(whole), 2)


def start_thread():
    Thread(target=process,
           daemon=True).start()


def callback(url):
    webbrowser.open_new(url)


# Define button press function
def process():
    print("Starting to Parse Image Exif Information")
    global cpt
    global status_message
    status_message.set("")
    link1.config(text="")
    link2.config(text="")
    text.delete('1.0', END)
    status.config(text="")
    count = 0
    path = entryText.get() + "/"
    # path = entryText.get().replace("/", "//")+"//"
    files = [f for f in glob.glob(path + "**/*.jpg", recursive=True)]
    visited_cities = []
    visited_cities_clean = []
    visited_coordinates_lat = []
    visited_coordinates_lon = []
    visited_coordinates = []
    months = []
    years = []
    cities = []
    countries = []

    for f in files:
        f = f.replace("\\", "/")
        count = count + 1
        if count % 10 == 0:
            status_message.set(
                "Processing Image: " + str(count) + " of " + str(cpt) + " (" + str(percentage(count, cpt)) + "%)")
        try:
            exif = get_exif(f)
            geo_tags = get_geotagging(exif)
            coordinates = get_coordinates(geo_tags)
            lat = float(Decimal(coordinates[0]).quantize(Decimal(10) ** -3))
            lon = float(Decimal(coordinates[1]).quantize(Decimal(10) ** -3))
            results = rg.search(coordinates, mode=1)
            city = results[0].get('name') + ", "
            state = results[0].get('admin1') + ", "
            country = results[0].get('cc')
            cc = coco.CountryConverter(include_obsolete=True)
            country = cc.convert(country, to='name_short')

            try:
                datum = geo_tags['GPSDateStamp']
                year = str(converter(datum).year)
                month = str(converter(datum).month)
            except:
                try:
                    datum = str(Image.open(f)._getexif()[36867]).split(" ", 1)[0]
                    year = str(converter(datum).year)
                    month = str(converter(datum).month)
                except:
                    year = "1970"
                    month = "00"

            if len(year) == 1:
                year = "0" + year
            if len(month) == 1:
                month = "0" + month

            # print(f)
            if year != "1970" and month != "00":
                visited_cities.append(year + ":" + month + " | " + city + state + country)

            # print("Location:" + city + state + country + " | " + f)
            for word in visited_cities:
                if word not in visited_cities_clean:
                    visited_cities_clean.append(word)
                    label.config(text=f"Processing Coordinates: {coordinates}")
                    label2.config(text="Successfully Resolved: " + city + state + country)
                    if lat != 0.000 and lon != 0.000:
                        visited_coordinates_lat.append(lat)
                        visited_coordinates_lon.append(lon)
                        pathr, filenamer = f.rsplit('/', 1)
                        visited_coordinates.append(
                            city + country + "|" + str(lat) + "|" + str(lon) + "|" + year + ":" + month + "|" + pathr)
                        months.append(month)
                        years.append(year)
                        cities.append(results[0].get('name'))
                        countries.append(country)
                        text.insert(tkinter.END,
                                    year + "/" + month + " - " + city + country + "\n")
                        text.see("end")


        except:
            # print("GPS Data Missing in " + f)
            error = 2

    status_message.set("Processed: " + str(count) + " images")
    label.config(text="")
    label2.config(text="")
    print("--- GOOGLE MAP Generated ---")
    google_map = gmplot.GoogleMapPlotter(0, 0, 2)
    google_map.coloricon = "http://www.googlemapsmarkers.com/v1/%s/"
    google_map.apikey = google_api_key
    google_map.heatmap(visited_coordinates_lat, visited_coordinates_lon)
    google_map.plot(visited_coordinates_lat, visited_coordinates_lon, c='#046CC6', edge_width=1.0)

    # ADD MARKERS
    for word in visited_coordinates:
        title = word.split("|")[0]
        lati = word.split("|")[1]
        long = word.split("|")[2]
        date = word.split("|")[3]
        path_directory = word.split("|")[4]
        date = date.split(":")
        month_word = (calendar.month_name[int(date[1])])
        google_map.marker(float(lati), float(long), 'cornflowerblue',
                          title=str(title) + " (" + str(date[0]) + " " + str(month_word) + ")")

    google_map.draw("result.html")

    link1.config(text="Open Map")
    link1.bind("<Button-1>", lambda e: callback("result.html"))

    link2.config(text="Open Excel")
    link2.bind("<Button-1>", open_excel)

    # EXCEL
    df = pd.DataFrame(
        {'Month': months, 'Year': years, 'City': cities, 'Country': countries, 'Lat.': visited_coordinates_lat,
         'Long.': visited_coordinates_lon, 'Directory': path_directory})
    writer = pd.ExcelWriter("results.xlsx", engine='xlsxwriter')
    df.to_excel(writer, sheet_name='Sheet1', startrow=1, header=False)
    workbook = writer.book
    worksheet = writer.sheets['Sheet1']

    header_format = workbook.add_format(
        {'bold': True, 'text_wrap': False, 'valign': 'top', 'fg_color': '#D7E4BC', 'border': 1})

    # Write the column headers with the defined format.
    for col_num, value in enumerate(df.columns.values):
        worksheet.write(0, col_num + 1, value, header_format)

    # Close the Pandas Excel writer and output the Excel file.
    df.sort_values(['Month', 'Year'], ascending=[True, True])
    writer.save()

    # Write END to Textbox
    text.insert(tkinter.END, "\n")
    text.insert(tkinter.END, "---------------END---------------\n")
    text.insert(tkinter.END, "\n")
    text.see("end")
    print("-------------END------------")


# Place 'Change Label' button on the window
button = tkinter.Button(window, text="...", command=open_file_dialog)
button.place(x=470, y=17)
process_button = tkinter.Button(window, text="Process Images", command=start_thread)
process_button.place(x=10, y=50)

# Center Window on Screen
center(window)

# close the program and tkinter window on exit
window.protocol("WM_DELETE_WINDOW", ask_quit)
# Show new window
window.mainloop()