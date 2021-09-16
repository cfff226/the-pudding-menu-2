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
    return render_template("index.html", page_title="HOME")


@app.route('/get_recipes')
# Retrieve recipe data from mongodb
def get_recipes():
    recipe = list(mongo.db.recipes.find())
    print(recipe)
    return render_template("recipes.html", page_title="RECIPES", recipes=recipe)


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
    return render_template("register.html", page_title="REGISTER")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # Check if username exists in database
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        if existing_user:
            # Make sure hashed password matches user input
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                session["user"] = request.form.get("username").lower()
                flash("Welcome, {}".format(
                    request.form.get("username")))
                return redirect(url_for(
                    "profile", username=session["user"]))
            else:
                # Invalid password match
                flash("Incorrect Username and/or Password")
                return redirect(url_for("login", _external=True,
                                scheme='https'))

        else:
            # Username does not exist
            flash("Incorrect Username and/or Password")
            return redirect(url_for("login", _external=True, _scheme='https'))

    return render_template("login.html", page_title="LOG IN")


@app.route("/logout")
def logout():
    # Remove user from session cookies
    flash("You have been logged out")
    session.pop("user")
    return redirect(url_for("login", page_title="LOGIN PAGE"))


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # Grab the session user's Username from database
    username = mongo.db.users.find_one(
        {"username": session["user"]})["username"]

    if session["user"]:
        # Display all of users recipes
        user = mongo.db.users.find_one({"username": session['user']})
        recipe = list(mongo.db.recipes.find({"created_by": session['user']}))
        return render_template(
            "profile.html",
            username=username,
            recipes=recipe)
    else:
        return redirect(url_for("login", page_title="LOGIN"))


@app.route("/search", methods=["GET", "POST"])
def search():
    # User is able to search through Dessert list using search bar
    search_term = request.form["search"]
    print(search_term)
    recipe = list(mongo.db.recipes.find({"$text": {"$search": search_term}}))
    print(recipe)
    return render_template("recipes.html", recipes=recipe)


@app.route("/add_recipe", methods=["GET", "POST"])
def add_recipe():
    # Get users form input and send to database
    if request.method == "POST":
        dessert_ingredients = request.form.getlist("dessert_ingredients")
        print(f'INGREDIENTS: {dessert_ingredients}')
        dessert_instructions = request.form.getlist("dessert_instructions")
        print(f'INSTRUCTIONS: {dessert_instructions}')
        dessert_recipe = {
            "dessert_name": request.form.get("dessert_name"),
            "dessert_image": request.form.get("dessert_image"),
            "dessert_ingredients": dessert_ingredients,
            "dessert_instructions": dessert_instructions,
            "created_by": session["user"]
        }
        # Post users input to Mongodb
        mongo.db.recipes.insert_one(dessert_recipe)
        flash("Thanks! Your recipe has been added")
        return redirect(url_for("profile", username=session["user"]))

    return render_template("add_recipe.html")


@app.route("/edit_recipe/<recipes_id>", methods=["GET", "POST"])
def edit_recipe(recipes_id):
    # Function to edit recipes
    if request.method == "POST":
        dessert_ingredients = request.form.getlist("dessert_ingredients")
        ingredients_list = []
        for ingredients in dessert_ingredients:
            ingredients_list.append(ingredients)
        dessert_instructions = request.form.getlist("dessert_instructions")
        instructions_list = []
        for instructions in dessert_instructions:
            instructions_list.append(instructions)
        edit_recipe = {
            "dessert_name": request.form.get("dessert_name"),
            "dessert_image": request.form.get("dessert_image"),
            "dessert_ingredients": ingredients_list,
            "dessert_instructions": instructions_list,
            "created_by": session["user"]
        }

        mongo.db.recipes.update({"_id": ObjectId(recipes_id)}, edit_recipe)
        flash("Your recipe has been updated!")
        return redirect(url_for("get_recipes"))

    recipe = mongo.db.recipes.find_one({"_id": ObjectId(recipes_id)})
    return render_template("edit_recipe.html", recipes=recipe)


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP", "0,0,0,0"),
        port=int(os.environ.get("PORT", "5000")),
        debug=True)
