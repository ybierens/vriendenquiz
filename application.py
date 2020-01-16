# application.py

# Computer Science 50
# Yannick Bierens
# Website where you can buy and sell stock.



import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd, add_up

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///quiz.db")


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "GET":
        return render_template("home.html")

@app.route("/index")
@login_required
def index():
    return apology("persoonlijke homepage")


@app.route("/check", methods=["GET"])
def check():
    username = request.args.get("username")

    # check all usernames in db, when new username already exists return false
    names = db.execute("SELECT username FROM users")
    for name in names:
        if username == name['username']:
            return jsonify(False)

    # when not duplicate and at least 1 character return true
    return jsonify(True)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
   return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        # Redirect user to home page
        return redirect("/index")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # insert into database
        db.execute("INSERT INTO users (username, password) VALUES (:username, :password)",
                    username = request.form.get("username"), password = generate_password_hash(request.form.get("password"), method = 'pbkdf2:sha256', salt_length=8))

        get_id = db.execute("SELECT user_id FROM users WHERE username = :username", username = request.form.get("username"))
        session["user_id"] = get_id[0]['user_id']

        return redirect("/index")

    else:
        return render_template("register.html")

@app.route("/mijn_quizzes", methods=["GET", "POST"])
def mijn_quizzes():
    """ Brengt de gebruiker naar pagina met al zijn gemaakte quizzes """
    if request.method == "GET":
        return render_template("mijn_quizzes.html")


def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)