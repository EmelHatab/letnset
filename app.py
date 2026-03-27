import sqlite3
from flask import Flask
from flask import redirect, render_template, request, session
from werkzeug.security import check_password_hash, generate_password_hash

import config, db, users, marketplace

app = Flask(__name__)
app.secret_key = config.secret_key

@app.route("/")
def index():
    locations = marketplace.get_locations()
    return render_template("index.html", locations=locations)

@app.route("/location/<int:location_id>")
def show_location(location_id):
    location = marketplace.get_location(location_id)
    # messages = forum.get_messages(thread_id)
    return render_template("location.html", location=location)

@app.route("/new_location", methods=["POST"])
def new_location():
    name = request.form["name"]
    description = request.form["description"]
    user_id = session["user_id"]

    location_id = marketplace.add_location(name, description, user_id)
    return redirect("/location/" + str(location_id))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        sql = "SELECT password_hash FROM Users WHERE username = ?"
        try:
            password_hash = db.query(sql, [username])[0][0]
        except:
            return "VIRHE: käyttäjää ei ole olemassa"

        user_id = users.check_login(username, password)

        if user_id:
            session["username"] = username
            session["user_id"] = user_id
            return redirect("/")
        else:
            return "VIRHE: väärä tunnus tai salasana"

@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    if request.method == "POST":
        username = request.form["username"]
        password1 = request.form["password1"]
        password2 = request.form["password2"]

        if password1 != password2:
            return "VIRHE: salasanat eivät ole samat"

        try:
            users.create_user(username, password1)
            return "Tunnus luotu"
        except sqlite3.IntegrityError:
            return "VIRHE: tunnus on jo varattu"

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        return "VIRHE: salasanat eivät ole samat"
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO Users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
    except sqlite3.IntegrityError:
        return "VIRHE: tunnus on jo varattu"
    
    return redirect("/") 