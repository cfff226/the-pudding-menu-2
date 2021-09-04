import os
from flask import Flask


app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", page_title="Home")