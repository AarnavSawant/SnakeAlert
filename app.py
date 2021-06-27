from flask import Flask
from flask import render_template, request, redirect, Flask
import sqlite3
import requests
import geocoder
from geopy import distance
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from datetime import datetime
import time
import numpy as np
from tensorflow.keras.models import load_model
import cv2
import urllib.parse

app = Flask(__name__)

tips = {"Venomous" : "1. If you see a venomous snake, leave it alone. Don't try to kill it or pick it up. If you need to get by it, give it a 6-foot berth. Stay alert when you're climbing rocks or hiking over broken, rocky terrain. Snakes are cold-blooded and like to warm themselves on rocks when it is cool outside. Don't put your hands or feet anywhere you can't see. When it's hot, snakes will cool themselves down by hiding out in cool, shady spots. If you can't avoid walking through tall grass or rocky terrain, wear thick leather boots and/or snake gaiters.", "Non-Venomous" : "If you can safely manage the distance needed between you and it, a snake moving along the ground can be contained by dropping a trash can over it. Put bricks or stones on the top to secure the can in place. Then, if available, an animal control service can be called to remove the snake from the area for you. Call an animal control service if you do not want to remove, kill or encourage a snake to go somewhere else. Always err on the side of extreme safety for the people and other animals nearby as you decide how best to get rid of an unwanted snake. Keep your distance from any venomous snake at all times"}
snakes = {'agkistrodon-contortrix' : ['Venomous', 'Agkistrodon contortrix individuals are known for their distinctive reddish-brown bodies with a crossband pattern consisting of tan, copper, and rich brown colors that extend throughout the body. Adult copperheads average 76 cm in length and are normally described as heavy-bodied snakes. Copperheads are sexually dimorphic, as males tend to have longer bodies than females. The head is very distinct from the rest of the body and has a solid, rich brown color. Temperature-sensitive pit organs are present below the midline between the eye and the nostril. Although copperheads are venomous, their venom is somewhat mild compared to other snake species and is usually not fatal to healthy human adults.', "Copperhead Snake"], 'coluber-constrictor' : ["Non-Venomous", "The mature racer has very smooth shiny scales with a divided anal plate (Conant and Collins, 1998). There are 17 scale rows midbody, and 15 near the tail. The normal coloration is a very dark and uniform dorsum with variations ranging from black, bluish, gray, to olive brown. The head is narrow but still wider than the neck with very distinct brow ridges. The chin and throat areas vary from white to yellowish progressing back to a ventrum that could be black, dark gray, light blue, white, cream or yellow. The average adult length ranges from 90-190 cm. (35-75 in.) (Harding, 1997).", "Eastern Racer Snake"], 'crotalus-scutulatus' : ["Venomous", "C. scutulatus is most active from April to September, and brumates alone or in small groups during the winter. Ambush predators, they eat mostly small rodents and lizards. Females bear live young, from two to 17 (average about eight), from July through September.[4][10] Although they have a reputation for being aggressive towards people, such behavior is not described in scientific literature. Like other rattlesnakes, however, they will defend themselves vigorously when disturbed. \n The Mojave rattlesnake is one of the world's most venomous snakes. The most common subspecies of Mojave rattlesnake (Type A) has a neurotoxic venom that is considered to be one of the most debilitating and potentially deadly of all rattlesnakes, and even matching several elapids.[11] However, chances for survival are very good if medical attention is sought as soon as possible after a bite. There have been reported incidents in Red Mountain California of people finding dead snakes, getting pricked by fangs and succumbing to postmortem envenomations.", "Mojave Green Rattlesnake"],
 'haldea-striatula' : ["Non-Venomous", 'The rough earth snake (Haldea striatula) is a species of non-venomous natricine colubrid snake native to the southeastern regions of the United States. It can be found throughout most of the US southern Coastal Plain. Rough Earth Snake'], 'heterodon-platirhinos' : ["Non-Venomous", "Eastern hognose snakes are characterized by thick bodies, wide heads, and a slightly upturned and pointed snout. Adult length is 45-105cm, and females are larger than males. As juveniles, these snakes have a pinkish coloration with dark brown to black blotches arranged in alternating rows down the length of their bodies. As adults, these snakes vary greatly in color from light brown, light gray, red, tan, grayish green, yellowish, and even solid dark gray or black. The snakes with the lighter colorations usually also exhibit the same alternating pattern of dark blotches as the juveniles and also typically have a darker color pattern on the top of the head. The blotches observed are typically larger on the dorsal side of the body and smaller on the lateral side of the body. The ventral side of the body ranges in color from white to a light gray but is lighter than the dorsal coloration. In addition, the underside of the tail typically has a lighter coloration than the ventral coloration. Eastern hognose snakes typically have twenty-three to twenty-five dorsal scale rows with a divided anal plate. Males of this species typically have an average of one hundred and twenty-six ventral scales and fifty-one subcaudal scales while females have an average of one hundred thirty-eight ventral scales and thirty-nine subcaudal scales. Both sexes of this species typically have between thirty-seven and sixty caudal scales.", "Eastern Hoghose Snake"], 'lampropeltis-californiae' : ["Non-Venomous", "The California kingsnake (Lampropeltis californiae) is a nonvenomous colubrid snake endemic to the western United States and northern Mexico, and is found in a variety of habitats. Due to ease of care and a wide range of color variations, the California kingsnake is one of the most popular snakes in captivity.", "California King Snake"],
 'natrix-natrix' : ["Non-Venomous", "The grass snake (Natrix natrix), sometimes called the ringed snake or water snake, is a Eurasian non-venomous colubrid snake. It is often found near water and feeds almost exclusively on amphibians. The barred grass snake, Natrix helvetica, was split off as a separate species in 2017.", 'Water Snake'], 'nerodia-fasciata' : ["Non-Venomous", "The banded water snake or southern water snake (Nerodia fasciata) is a species of mostly aquatic, nonvenomous, colubrid snakes endemic to the Midwest and Southeastern United States."], 'nerodia-rhombifer' : ["Non-Venomous", "The diamondback water snake is predominantly brown, dark brown, or dark olive green in color, with a black net-like pattern along the back, with each spot being vaguely diamond-shaped. Dark vertical bars and lighter coloring are often present down the sides of the snake. In typical counter-colored fashion, the underside is generally a yellow or lighter brown color, often with black blotching."],
 'pantherophis-emoryi' : ["Non-Venomous", "Pantherophis emoryi, commonly known as the Great Plains rat snake, is a species of nonvenomous rat snake native to the central part of the United States, from Missouri to Nebraska, to Colorado, south to Texas, and into northern Mexico.", "Great Plains Rat Snake"], 'pantherophis-guttatus' : ["Non-Venomous", "Corn snakes are often killed because they are mistaken for the copperhead, a venomous species. Corn snakes, as well as copperheads, are actually beneficial predators of rodents and in turn are important food items for many other animals. The corn snake, also known as the red rat snake, is one of several species of rat snakes occurring in the United States. Rat snakes are large, powerful, nonvenomous snakes that feed on a variety of prey species, which they overpower by constriction. While not venomous, corn snakes will bite. Their striking range is quite long, about 1/3 to 1/2 of their body length.", "Corn Snake"], 'storeria-occipitomaculata' : ["Non-Venomous", "The redbellied snake is a small woodland snake, ranging from 4 - 10 in (10 - 25 cm) long. This species is one of our most variably-colored snakes, with some individuals ranging from bright orange to brown, gray, or nearly black. Occasionally individuals are found that are gray with a brown or orange stripe down the center of the back. Many individuals have a light brown ring behind the head. This species can easily be distinguished from all other small woodland snakes by their unmarked bright orange to red underside.", "Redbellied Snake"],
 'thamnophis-elegans' : ["Venomous", "Like many species of North American garter snake, the western terrestrial garter snake possesses a mildly venomous saliva. Specimens collected from Idaho and Washington produced venom with myonecrotic (muscle tissue-killing) effects when injected into the gastrocnemius muscles of mice.", "North American Garner Snake"], 'thamnophis-marcianus' : ["Mildy Venomous", "Thamnophis marcianus marcianus. Gartersnakes have toxins in their saliva which can be deadly to their prey and their bite might produce an unpleasant reaction in humans, but they are not considered dangerous to humans.", "Garter Snake"], 'thamnophis-proximus' : ["Non Venomous", "Thamnophis proximus, the Western ribbon snake, can be found ranging from the United States specifically Wisconsin and southward, down into Central America, including Belize and Costa Rica. The species is usually found active during early spring into the summer, and is most active during the day or during warm periods. In areas with changeable seasons, the Western Ribbon Snake will hibernate in rocky outcroppings, sometimes with other species. (Clark Jr., 1974; Rossman, 1962; Rossman, et al., 1996; Sunyer, et al., 2013)", "Western Ribbon Snake"]}
model = load_model("model/snakeModel.h5")
@app.route("/postings", methods=["POST", "GET"])
def get_postings():
    db = sqlite3.connect("./login.db", isolation_level=None)
    cursor = db.cursor()
    rows = cursor.execute("SELECT * FROM POSTS ORDER BY Timestamp desc")
    rows = rows.fetchall()
    lngLat = []
    species = []
    imgPaths = []
    danger = []
    addresses = []
    new_colors = []
    dates = []
    colors = {"Venomous": "red", "Non-Venomous": "green"}
    for i in range(len(rows)):
        dates.append(datetime.fromtimestamp(rows[i][0]).strftime("%m/%d/%Y, %H:%M:%S"))
        imgPaths.append((rows[i][-1]))
        species.append(snakes[rows[i][1]][-1])
        danger.append(snakes[rows[i][1]][0])
        new_colors.append(colors[snakes[rows[i][1]][0]])
        lngLat.append((rows[i][2], rows[i][3]))
    print(lngLat)
    print(colors)
    key = "JpugEMTYQgVY7aWxTQsTdOJUp7g33bSW"
    for i in range(len(lngLat)):
        url = 'http://www.mapquestapi.com/geocoding/v1/reverse?key=%s&location=%s,%s' % (key, lngLat[0][0], lngLat[0][1])
        response = requests.get(url).json()
        street = " ".join(response["results"][0]["locations"][0]["street"].split()[1:])
        city = response["results"][0]["locations"][0]["adminArea5"]
        address = "%s in %s" % (street, city)
        addresses.append(address)
    # http: // www.mapquestapi.com / geocoding / v1 / reverse?key = KEY & location = 30.333472, -81.470448
    # species = ["King Snake", "Cobra"]
    # colors = ["red", "green"]
    # danger = ["venomous", "non-venomous"]
    # address = ["Milpitas, "San Jose"]
    return render_template("postings.html", images=imgPaths, len= len(species), species=species, colors=new_colors, danger=danger, address=addresses, user="snakealerttestuser@gmail.com", time= dates)
@app.route('/')
def hello_world():
    return render_template("index.html")
@app.route("/homepage", methods=["POST", "GET"])
def home_page():
    db = sqlite3.connect("./login.db", isolation_level=None)
    if request.method == "POST":
        file = request.files["file"]
        img_path = "static/images/" + file.filename
        file.save(img_path)
        img = cv2.imread(img_path)
        res = cv2.resize(img, dsize=(228, 228))
        res = cv2.cvtColor(res, cv2.COLOR_BGR2RGB)
        res = np.reshape(res, (1, 228, 228, 3))
        pred = model.predict(res)
        print(np.argmax(pred))
        print(list(snakes))
        prediction = list(snakes)[np.argmax(pred)]
        # prediction = "Water Snake"
        g = geocoder.ip("me")
        latitude = g.latlng[0]
        longitude = g.latlng[1]
        coordinates = (latitude, longitude)
        cursor = db.cursor()
        rows = cursor.execute("SELECT * FROM USERS")
        rows = rows.fetchall()
        # emails = []
        # lngLat = []
        for i in range(len(rows)):
            coordinatesTest = (rows[i][-1], rows[i][-2],)
            email = rows[i][0] + "@" + rows[i][1]
            dist = distance.distance(coordinates, coordinatesTest).miles
            print(dist)
            if dist < 4:
                with open(img_path, 'rb') as f:
                    img_data = f.read()
                    msg = MIMEMultipart()
                    msg['Subject'] = 'subject'
                    msg['From'] = 'e@mail.cc'
                    msg['To'] = 'e@mail.cc'
                    text = MIMEText("Hi %s, \n We detected a %s about %f miles away from your home. Just wanted to give you a warning to stay safe and act accordingly. Attached below is an image of the snake we detected. \n Thank you and Stay Safe! \n -Snake Alert" % (email, snakes[prediction][-1], dist))
                    msg.attach(text)
                    image = MIMEImage(img_data, name=file.filename)
                    msg.attach(image)
                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.ehlo()
                    server.starttls()
                    gmail_user = 'snakealert2021@gmail.com'
                    gmail_password = ''
                    server.login(gmail_user, gmail_password)
                    server.sendmail(gmail_user, email, msg.as_string())
                    server.close()
        # print(emails)
        # print(lngLat)
        # for i in r

        try:
            # cursor.execute("DROP TABLE POST")
            # db.commit()
            cursor.execute("CREATE TABLE POSTS(Timestamp double, Species varchar(255), Latitude double, Longitude double, ImagePath varchar(255));")
        except:
            print("POST TABLE ALREADY CREATED")
        cursor.execute("INSERT INTO POSTS (Timestamp, Species, Latitude, Longitude, ImagePath) VALUES (?, ?, ?, ?, ?)", (time.time(), prediction, latitude, longitude, "images/" + file.filename))
        db.commit()
        return render_template("homepage.html", species=snakes[prediction][-1], path ="images/" + file.filename, tips=tips[snakes[prediction][0]], desc=snakes[prediction][1], danger=snakes[prediction][0])
    return render_template("homepage.html")



@app.route("/sign-up", methods=["POST", "GET"])
def sign_up():
    db = sqlite3.connect("./login.db", isolation_level=None)
    if request.method == "POST":
        email, platform = request.form["email"].split("@")
        password = request.form["password"]
        address = request.form["address"]
        zip = int(request.form["zip"])
        state = request.form["state"]
        city = request.form["city"]
        cursor = db.cursor()
        key = "MAPQUEST API KEY"
        full_address = address + ", " + city + ", " + state + " " + str(zip)
        url = 'http://www.mapquestapi.com/geocoding/v1/address?key=%s&location=%s' % (key, full_address)
        response = requests.get(url).json()
        latitude = response["results"][0]["locations"][0]["latLng"]["lat"]
        longitude = response["results"][0]["locations"][0]["latLng"]["lng"]

        try:
            # cursor.execute("DROP TABLE USERS")
            cursor.execute("CREATE TABLE USERS(Email varchar(255), Platform varchar(255), Password varchar(255), Address varchar(255), Zip int, State varchar(255), Longitude double, Latitude double);")
        except:
            print("Table USERS already created")
        query = "INSERT INTO USERS (Email, Platform, Password, Address, Zip, State, Longitude, Latitude) VALUES (?, ?, ?, ?, ?, ?, ?, ?);"
        query2 = "SELECT * FROM USERS;"
        query1 = "SELECT username, password from Users WHERE username = {un} AND password = {password}".format(un=email, password = password)
        print(query)
        rows = cursor.execute(query, (email, platform, password, address, zip, state, longitude, latitude))
        fetched_rows = cursor.execute(query2)
        print(fetched_rows.fetchall())
        # db.commit()
        # db.close()
        rows = rows.fetchall()
        print(rows)
        # print(len(rows))
        return redirect("homepage")

    return render_template("registration.html")


if __name__ == '__main__':
        # TODO: Send email here
    app.run(debug=True)
