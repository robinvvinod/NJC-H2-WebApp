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
    currentLoc = con.execute('''SELECT Name,Description,Image FROM Location WHERE PlaceID = "''' + str(placeID) +
    '''"''')
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
                    return redirect("/selector")
                else:
                    return render_template("login.html", failed="")
            else:
                return render_template("login.html", failed="")
        else:
            return render_template("login.html", failed="")

    return render_template("login.html", failed="hidden")

@app.route('/selector', methods = ['GET'])
def selector():
    return render_template('selector.html')

@app.route('/add', methods = ['POST','GET'])
def add():
    
    exitList = []
    con = open_DB("Database.db")
    selectCur = con.execute('''SELECT PlaceID, Name FROM Location''')
    exitL = selectCur.fetchall()
    con.close()

    for exit in exitL:
        exitList.append([exit[0], exit[1]])

    if "name" in request.form:
        name = request.form["name"]
        desc = request.form["description"]
        addExit = request.form["exitPoint"]
        newPlaceID = hashlib.sha256(name.encode('utf-8')).hexdigest()
        image = request.files["image"]
        image_path = image.filename

        if name != "" and desc != "":
            if image_path != "":
                con = open_DB("Database.db")
                con.execute('''INSERT INTO Location (PlaceID, Name, Description, Image) VALUES
                (?,?,?,?)''', (newPlaceID, name, desc, image_path))
                con.commit()
                con.close()
                try:
                    image.save("static/images/"+image_path)
                except:
                    return render_template('add.html', exits=exitList, failed="", success="hidden")

            else:
                con = open_DB("Database.db")
                con.execute('''INSERT INTO Location (PlaceID, Name, Description, Image) VALUES
                (?,?,?,?)''', (newPlaceID, name, desc, None))
                con.commit()
                con.close()
                
            if addExit != "NULL":
                con = open_DB("Database.db")
                con.execute('''INSERT INTO Exit (PlaceID, ExitPointID) VALUES
                (?,?)''', (newPlaceID, addExit))
                con.commit()
                con.close()

            return render_template('add.html', exits=exitList, failed="hidden", success="")

        else:
            return render_template('add.html', exits=exitList, failed="", success="hidden")
        
    return render_template('add.html', exits=exitList, failed="hidden", success="hidden")

@app.route('/update', methods = ['POST','GET'])
def update():
    
    exitList = []
    con = open_DB("Database.db")
    selectCur = con.execute('''SELECT PlaceID, Name FROM Location''')
    exitL = selectCur.fetchall()
    con.close()

    nameList = []
    con = open_DB("Database.db")
    selectCur = con.execute('''SELECT PlaceID, Name FROM Location''')
    nameL = selectCur.fetchall()
    con.close()

    for exit in exitL:
        exitList.append([exit[0], exit[1]])

    for name in nameL:
        nameList.append([name[0], name[1]])

    if "name" in request.form:
        placeID = request.form["name"]
        desc = request.form["description"]
        addExit = request.form["exitPoint"]
        image = request.files["image"]
        image_path = image.filename

        if addExit != "NULL":
            con = open_DB("Database.db")
            checkCur = con.execute('''SELECT ExitPointID FROM Exit WHERE PlaceID = ?''', (placeID,))
            check = checkCur.fetchall()
            con.close()
                
            for item in check:
                if item[0] == addExit:
                    return render_template('update.html', exits=exitList, names=nameList, failed="", success="hidden")

            if placeID == addExit:
                return render_template('update.html', exits=exitList, names=nameList, failed="", success="hidden")
            
            con = open_DB("Database.db")
            con.execute('''INSERT INTO Exit (PlaceID, ExitPointID) VALUES (?,?)''', (placeID, addExit))
            con.commit()
            con.close()

        if desc != "":
            con = open_DB("Database.db")
            con.execute('''UPDATE Location SET Description = ? WHERE PlaceID = ?''', (desc, placeID))
            con.commit()
            con.close()

        if image_path != "":
            con = open_DB("Database.db")
            con.execute('''UPDATE Location SET Image = ? WHERE PlaceID = ?''', (image_path, placeID))
            con.commit()
            con.close()
            try:
                image.save("static/images/"+image_path)
            except:
                return render_template('update.html', exits=exitList, names=nameList, failed="", success="hidden")

        return render_template('update.html', exits=exitList, names=nameList, failed="hidden", success="")
        
    return render_template('update.html', exits=exitList, names=nameList, failed="hidden", success="hidden")

@app.route('/delete', methods = ['POST','GET'])
def delete():

    nameList = []
    con = open_DB("Database.db")
    selectCur = con.execute('''SELECT PlaceID, Name FROM Location''')
    nameL = selectCur.fetchall()
    con.close()

    for name in nameL:
        nameList.append([name[0], name[1]])

    if "name" in request.form:
        placeID = request.form["name"]
        con = open_DB("Database.db")
        con.execute('''DELETE FROM Exit WHERE PlaceID = ? OR ExitPointID = ?''', (placeID,placeID))
        con.execute('''DELETE FROM Location WHERE PlaceID = ?''', (placeID,))
        con.commit()
        con.close()

        return redirect('/delete')

    return render_template('delete.html', names=nameList)

if __name__ == '__main__':
    app.run()
