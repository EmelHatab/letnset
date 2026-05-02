import sqlite3, time, math, secrets, markupsafe
from functools import wraps
from flask import Flask
from flask import redirect, render_template, request, session, Response, url_for, g, flash, abort
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

import config, db, users, marketplace

app = Flask(__name__)
app.secret_key = config.secret_key

def check_csrf():
    if request.form["csrf_token"] != session["csrf_token"]:
        abort(403)

@app.template_filter()
def show_lines(content):
    content = str(markupsafe.escape(content))
    content = content.replace("\n", "<br />")
    return markupsafe.Markup(content)

@app.before_request
def before_request():
    g.start_time = time.time()

@app.after_request
def after_request(response):
    elapsed_time = time.time() - g.start_time
    print(f"Request took {elapsed_time:.2f} seconds")
    return response

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
@app.route("/<int:page>")
def index(page=1):
    location_count = marketplace.location_count()
    page_count =  math.ceil(location_count / config.page_size)
    page_count = max(page_count, 1)

    if page < 1: 
        return redirect("/")
    if page > page_count:
        return redirect("/" + str(page_count))
    
    return render_template("index.html",
                            page=page,
                            page_count=page_count,
                            locations=marketplace.get_locations(page, config.page_size),
                            tags=marketplace.get_tags())

@app.route("/search")
@app.route("/search/<int:page>")
def search(page=1):
    query = request.args.get("query")
    location_count = marketplace.search_location_count(query)
    page_count = math.ceil(location_count / config.page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect(url_for("search", query=query))
    if page > page_count:
        return redirect(url_for("search", page=page_count, query=query))

    locations = marketplace.search_locations(query, page, config.page_size)
    return render_template("search.html", results=locations, query=query, page=page, page_count=page_count)

@app.route("/location/<int:location_id>")
def show_location(location_id):
    location = marketplace.get_location(location_id)
    if not location:
        return abort(404)

    comments = marketplace.get_comments(location_id)
    return render_template("location.html", location=location, comments=comments, tags=marketplace.get_location_tags(location_id))

@app.route("/location/<int:location_id>/image")
def get_location_image(location_id):
    location = marketplace.get_location(location_id)
    if location and location["image"]:
        return Response(location["image"], mimetype="image/jpeg")
    abort(404)

@app.route("/new_location", methods=["POST"])
@login_required
def new_location():
    check_csrf()
    name = request.form["name"]
    description = request.form["description"]
    tags = request.form.getlist("tags")
    image_data = None

    if not name or len(name) > 100 or len(description) > 5000:
        abort(403)

    user_id = session["user_id"]
    
    if "image" in request.files:
        image_file = request.files["image"]
        if image_file.filename != "":
            image_data = image_file.read()

    location_id = marketplace.add_location(name, description, user_id, image_data)
    for tag_id in tags:
        marketplace.add_location_tag(location_id, tag_id)
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
            session["csrf_token"] = secrets.token_hex(16)
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
            flash("Käyttäjätunnus luotu onnistuneesti!", "success")
            return redirect("/login")
        except sqlite3.IntegrityError:
            flash("VIRHE: tunnus on jo varattu")
            return redirect("/register")

@app.route("/create", methods=["POST"])
def create():
    username = request.form["username"]
    password1 = request.form["password1"]
    password2 = request.form["password2"]
    image_data = None

    if password1 != password2:
        flash("VIRHE: salasanat eivät ole samat")
        return redirect("/register")
    password_hash = generate_password_hash(password1)

    if "image" in request.files:
        image_file = request.files["image"]
        if image_file.filename != "":
            image_data = image_file.read()

    try:
        sql = "INSERT INTO Users (username, password_hash, image) VALUES (?, ?, ?)"
        db.execute(sql, [username, password_hash, image_data])
        user_id = db.last_insert_id()
        
        # Automatically log in the user
        session["username"] = username
        session["user_id"] = user_id
        session["csrf_token"] = secrets.token_hex(16)
    except sqlite3.IntegrityError:
        flash("VIRHE: tunnus on jo varattu")
        return redirect("/register")
    
    flash("Käyttäjätunnus luotu onnistuneesti!", "success")
    return redirect("/") 

@app.route("/new_comment", methods=["POST"])
@login_required
def new_comment():
    check_csrf()
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

@app.route("/profile/<username>")
def profile(username):
    user = users.get_user_by_username(username)
    if not user:
        return abort(404)

    return render_template("profile.html", user=user)

@app.route("/profile/<username>/locations")
@app.route("/profile/<username>/locations/<int:page>")
def profile_locations(username, page=1):
    user = users.get_user_by_username(username)
    if not user:
        return abort(404)

    location_count = marketplace.location_count_by_user_id(user["id"])
    page_count = math.ceil(location_count / config.page_size)
    page_count = max(page_count, 1)

    if page < 1:
        return redirect(url_for("profile_locations", username=username))
    if page > page_count:
        return redirect(url_for("profile_locations", username=username, page=page_count))
    
    locations = marketplace.get_locations_by_user_id(user["id"], page, config.page_size)

    return render_template("profile_locations.html", user=user, locations=locations, page=page, page_count=page_count)

@app.route("/profile/<username>/comments")
def profile_comments(username): 
    user = users.get_user_by_username(username)
    if not user:
        return abort(404)

    comments = marketplace.get_comments_by_user_id(user["id"])
    return render_template("profile_comments.html", user=user, comments=comments)

@app.route("/profile/<username>/edit", methods=["GET", "POST"])
@login_required
def edit_profile(username):
    if session["username"] != username:
        return abort(403)

    user = users.get_user_by_username(username)
    if not user:
        return abort(404)

    if request.method == "GET":
        return render_template("profile_edit.html", user=user)

    if request.method == "POST":
        username = request.form["username"]
        if username == "":
            username = None
        password = request.form["password"]
        if password == "":
            password = None
        image_data = None
        
        if "image" in request.files:
            image_file = request.files["image"]
            if image_file.filename != "":
                image_data = image_file.read()
        
        users.update_user_profile(user["id"], new_username=username, new_password=password, new_image_data=image_data)
        flash("Profiili päivitetty onnistuneesti!", "success")
        return redirect("/profile/" + username)

@app.route("/profile/<username>/image")
def profile_image(username):
    user = users.get_user_by_username(username)
    if user and user["image"]:
        return Response(user["image"], mimetype="image/jpeg")
    abort(404)

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
        check_csrf()
        new_content = request.form["content"]
        if len(new_content) > 1000:
            abort(403)
        marketplace.update_comment(comment_id, new_content)
        return redirect("/location/" + str(location_id))

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)