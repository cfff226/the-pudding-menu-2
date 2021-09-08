import os
from flask import (
    Flask, flash, render_template,
    redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route('/index')
def index():
    return render_template("index.html", page_title="Home")


@app.route('/get_recipes')
# Retrieve recipe data from mongodb
def get_recipes():
    recipe = list(mongo.db.recipes.find())
    print(recipe)
    return render_template("recipes.html", page_title="Recipes", recipes=recipe)


@ app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check if username exists in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            flash("Username already exists")
            return redirect(url_for("register"))

        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        mongo.db.users.insert_one(register)

        # put the new user into 'session' cookie
        session["user"] = request.form.get("username").lower()
        flash("Registration successful!")
        return redirect(url_for("profile", username=session["user"]))
    return render_template("register.html", page_title="Register")



@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html", page_title="Login")


@app.route("/logout")
def logout():
    # Remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login", page_title="Login Page"))


@app.route("/profile", methods=["GET", "POST"])
def profile():
    return render_template("profile.html", page_title="Profile")


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0,0,0,0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
