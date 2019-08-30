from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
import sqlite3
import jinja2
import hashlib

app = Flask(__name__)
def open_DB(db):
    connection=sqlite3.connect(db)
    connection.row_factory = sqlite3.Row
    return connection

@app.route('/', methods = ['GET'])
def root():
    return render_template("index.html")

@app.route('/tour', methods = ['GET'])
def tour():
    return render_template("tour.html")

@app.route('/tour-start', methods = ['POST','GET'])
def location():
    
    placeID = list(request.form.to_dict().keys())
    placeID = placeID[0]
    
    con = open_DB("Database.db")
    currentLoc = con.execute('''SELECT Name,Description,Image FROM Location WHERE PlaceID = ''' + str(placeID))
    place = currentLoc.fetchone()
    placeName = place[0]
    placeDesc = place[1]
    placeImage = place[2]

    currentExits = []
    exitIDCur = con.execute('''SELECT ExitPointID FROM Exit WHERE PlaceID = "''' + str(placeID) + '''"''')
    exits = exitIDCur.fetchall()
    
    for exit in exits:
        ExitPointID = exit[0]
        exitPointCur = con.execute('''SELECT Name FROM Location WHERE PlaceID = "''' + str(ExitPointID) + '''"''')
        ExitPointName = exitPointCur.fetchone()
        currentExits.append([ExitPointID, ExitPointName[0]])

    con.close()
    return render_template("locations.html", name=placeName, description=placeDesc, image=placeImage, exits=currentExits)

@app.route('/login', methods = ['POST','GET'])
def login():
    
    if "username" in request.form:
        username = request.form["username"]
        password = request.form["password"]
        password = hashlib.sha256(password.encode('utf-8')).hexdigest()

        if username != "":
            con = open_DB("Database.db")
            userInfoCur = con.execute('''SELECT Password FROM Login WHERE Username = "''' + str(username) + '''"''')
            userInfo = userInfoCur.fetchone()
            con.close()
            if userInfo != None:
                if password == userInfo[0]:
                    return redirect("/update")

    return render_template("login.html")

@app.route('/update', methods = ['POST','GET'])
def update():
    return render_template('update.html')

if __name__ == '__main__':
    app.run()
