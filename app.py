import sqlite3
from functools import wraps
from flask import Flask
from flask import redirect, render_template, request, session, Response, url_for, g, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import config, db, users, marketplace

app = Flask(__name__)
app.secret_key = config.secret_key

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def index():
    locations = marketplace.get_locations()
    return render_template("index.html", locations=locations)

@app.route("/search")
def search():
    query = request.args.get("query")
    locations = marketplace.search_locations(query)
    return render_template("search.html", results=locations, query=query)

@app.route("/location/<int:location_id>")
def show_location(location_id):
    location = marketplace.get_location(location_id)
    if not location:
        return abort(404)

    comments = marketplace.get_comments(location_id)
    return render_template("location.html", location=location, comments=comments)

@app.route("/location/<int:location_id>/image")
def get_location_image(location_id):
    location = marketplace.get_location(location_id)
    if location and location["image"]:
        return Response(location["image"], mimetype="image/jpeg")
    abort(404)

@app.route("/new_location", methods=["POST"])
@login_required
def new_location():
    name = request.form["name"]
    description = request.form["description"]
    image_data = None

    if not name or len(name) > 100 or len(description) > 5000:
        abort(403)

    user_id = session["user_id"]
    
    if "image" in request.files:
        image_file = request.files["image"]
        if image_file.filename != "":
            image_data = image_file.read()

    location_id = marketplace.add_location(name, description, user_id, image_data)
    return redirect("/location/" + str(location_id))

@app.route("/edit/<int:location_id>", methods=["GET", "POST"])
@login_required
def edit(location_id):
    location = marketplace.get_location(location_id)

    if not location or location["user_id"] != session["user_id"]:
        return abort(403)

    if request.method == "GET":
        return render_template("edit.html", location=location)

    if request.method == "POST":
        description = request.form["description"]
        name = request.form["name"]
        image_data = None
        
        if "image" in request.files:
            image_file = request.files["image"]
            if image_file.filename != "":
                image_data = image_file.read()
        
        marketplace.update_location(location["id"], name, description, image_data)
        return redirect("/location/" + str(location["id"]))

@app.route("/remove/<int:location_id>", methods=["GET", "POST"])
@login_required
def remove_location(location_id):
    location = marketplace.get_location(location_id)

    if not location or location["user_id"] != session["user_id"]:
        return abort(403)

    if request.method == "GET":
        return render_template("remove.html", location=location)

    if request.method == "POST":
        if "continue" in request.form:
            marketplace.remove_location(location["id"])
        return redirect("/")

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
            abort(403)

        user_id = users.check_login(username, password)

        if user_id:
            session["username"] = username
            session["user_id"] = user_id
            return redirect("/")
        else:
            flash("VIRHE: virheellinen käyttäjätunnus tai salasana")
            return redirect("/login")

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
            flash("VIRHE: salasanat eivät ole samat")
            return redirect("/register")

        try:
            users.create_user(username, password1)
            flash("Tunnus luotu")
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("VIRHE: tunnus on jo varattu")
            return redirect("/register")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    if password1 != password2:
        flash("VIRHE: salasanat eivät ole samat")
        return redirect("/register")
    password_hash = generate_password_hash(password1)

    try:
        sql = "INSERT INTO Users (username, password_hash) VALUES (?, ?)"
        db.execute(sql, [username, password_hash])
        user_id = db.last_insert_id()
        
        # Automatically log in the user
        session["username"] = username
        session["user_id"] = user_id
    except sqlite3.IntegrityError:
        flash("VIRHE: tunnus on jo varattu")
        return redirect("/register")
    
    flash("Tunnus luotu onnistuneesti!")
    return redirect("/") 

@app.route("/new_comment", methods=["POST"])
@login_required
def new_comment():
    comment = request.form["content"]
    location_id = request.form["location_id"]

    if not comment or len(comment) > 1000:
        abort(403)

    user_id = session["user_id"]

    try:
        marketplace.add_comment(comment, user_id, location_id)
    except:
        abort(403)

    return redirect("/location/" + str(location_id))

@app.route("/remove_comment/<int:comment_id>", methods=["GET", "POST"])
@login_required
def remove_comment(comment_id):
    comment = marketplace.get_comment(comment_id)

    if not comment or comment["user_id"] != session["user_id"]:
        return abort(403)

    if request.method == "GET":
        return render_template("remove_comment.html", comment=comment)
    
    if request.method == "POST":
        comment_id = comment["id"]
        if "continue" in request.form:
            marketplace.remove_comment(comment_id)
        return redirect("/location/" + str(comment["location_id"]))

@app.route("/edit_comment/<int:comment_id>", methods=["GET", "POST"])
@login_required
def edit_comment(comment_id):
    comment = marketplace.get_comment(comment_id)

    if not comment or comment["user_id"] != session["user_id"]:
        return abort(403)

    location_id = comment["location_id"]

    if request.method == "GET":
        return render_template("edit_comment.html", comment=comment)

    if request.method == "POST":
        new_content = request.form["content"]
        if len(new_content) > 1000:
            abort(403)
        marketplace.update_comment(comment_id, new_content)
        return redirect("/location/" + str(location_id))