from flask import Flask, request, render_template, jsonify, url_for, redirect
from flask_login import login_required, LoginManager, login_user, logout_user, current_user, UserMixin
from flask_mysqldb import MySQL
from flask_pymongo import PyMongo
import bcrypt
import os
from google import genai
from bson import ObjectId, binary

BASE_DIR = os.path.dirname(__file__)

app = Flask(__name__)
app.secret_key = os.environ.get("flask_secret_key")

login_manager = LoginManager(app)
login_manager.login_message = "Por favor inicie sesión primero"
login_manager.login_view = "login.html"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = os.environ.get("mysql_key")
app.config["MYSQL_DB"] = "web-proyect"

mysql = MySQL(app)
mongodb = PyMongo(app, "mongodb://localhost:27017/web-proyect")

genai.Client(api_key=os.environ.get("gemini_API_key"))

class User(UserMixin):
    def __init__(self, id, username, password):
        self.id = id
        self.username = username
        self.password = password

@login_manager.user_loader
def user_loader(id):
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT nombre FROM users WHERE id = %s", id)
    user_data = cursor.fetchone()

    cursor.close()

    if user_data:
        return User(id, user_data[1])
    else:
        return None

@app.route("/upload_pdf/", methos=["GET", "POST"])
def upload_pdf():
    file = request.files.get("pdf")

    route = os.path.join(BASE_DIR, "uploads", file.name)

    file.save(route)

app.run(host="0.0.0.0", port=3030, debug=True)