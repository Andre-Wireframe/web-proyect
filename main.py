from flask import Flask, request, render_template, jsonify, url_for, redirect, flash
from flask_login import login_required, LoginManager, login_user, logout_user, current_user, UserMixin
from flask_mysqldb import MySQL
import bcrypt
import os
from google import genai

BASE_DIR = os.path.dirname(__file__)

app = Flask(__name__)
app.secret_key = os.environ.get("flask_secret_key")

login_manager = LoginManager(app)
login_manager.login_message = "Por favor inicie sesión primero"
login_manager.login_view = "login.html"

app.config["MYSQL_HOST"] = "localhost"
app.config["MYSQL_USER"] = "root"
app.config["MYSQL_PASSWORD"] = os.environ.get("mysql_key")
app.config["MYSQL_DB"] = "web_proyect"

mysql = MySQL(app)

genai.Client(api_key=os.environ.get("gemini_API_key"))

class User(UserMixin):
    def __init__(self, id, username):
        self.id = id
        self.username = username

@login_manager.user_loader
def user_loader(id):
    cursor = mysql.connection.cursor()

    cursor.execute("SELECT nombre FROM users WHERE id = %s", (id,))
    user_data = cursor.fetchone()

    cursor.close()

    if user_data:
        return User(id, user_data[1])
    else:
        return None

@app.route("/", methods=["GET"])
def index():
    context = {
        "services" : 0
    }

    return render_template("index.html", **context)

@app.route("/login/", methods=["GET", "POST"])
def login():
    cursor = mysql.connection.cursor()

    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        cursor.execute("SELECT * FROM users WHERE name = %s", (username,))
        user = cursor.fetchone()

        if not user:
            flash("error", "error")
            return redirect(url_for("login"))

        if bcrypt.checkpw(password.encode("utf-8"), user[2].encode("utf-8")):
            login_user(User(user[0], user[1]))

            flash("exito", "exito")
            return redirect(url_for("index"))

        else:
            flash("error", "error")
            return redirect(url_for("login"))

    return render_template("login.html")

@app.route("/files/", methods=["GET", "POST"])
def files():
    cursor = mysql.connection.cursor()

    if request.args:
        cursor.execute("""
            SELECT
                us.name,
                fl.id,
                fl.name,
                fl.route
            FROM files fl
            LEFT JOIN users us ON fl.user = us.id
            WHERE fl.visivility != false
            AND fl.name LIKE %s;
        """)

    else:
        cursor.execute("""
            SELECT
                us.name,
                fl.id,
                fl.name,
                fl.route
            FROM files fl
            LEFT JOIN users us ON fl.user = us.id
            WHERE fl.visivility != false;
        """)

    response = cursor.fetchall()

    context = {
        "files" : response,
        "n_files" : len(response)
    }

    if request.method == "POST":
        file = request.files.get("file")

        route = os.path.join(BASE_DIR, "uploads", file.filename)

        file.save(route)

    return render_template("files.html", **context)

app.run(host="0.0.0.0", port=3030, debug=True)