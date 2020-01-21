import os
import random

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp

from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


from helpers import apology, login_required, lookup, usd, add_up

UPLOAD_FOLDER = 'UPLOAD_FOLDER'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])


# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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


@app.route("/logincheck", methods=["GET"])
def logincheck():
    username = request.args.get("username")
    password = request.args.get("password")

    get_hash = db.execute("SELECT * FROM users WHERE username = :username", username = username)

    if not get_hash:
        return jsonify(False)

    if check_password_hash(get_hash[0]['password'], password) == True:
        return jsonify(True)
    else:
        return jsonify(False)


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


@app.route("/mijn_quizzes")
@login_required
def mijn_quizzes():
    """ Brengt de gebruiker naar pagina met al zijn gemaakte quizzes """

    quizes = db.execute("SELECT * FROM quizes WHERE user_id = :user_id", user_id = session['user_id'])

    return render_template("mijn_quizzes.html", quizes = quizes)


@app.route("/verwijder_quiz")
@login_required
def verwijder_quiz():

    quiz_id = request.args.get("quiz_id")

    db.execute("DELETE FROM quizes WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    db.execute("DELETE FROM questions WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    db.execute("DELETE FROM answers WHERE quiz_id = :quiz_id", quiz_id = quiz_id)

    return redirect("/mijn_quizzes")

@app.route("/vul_in/<quiz_id>", methods=["GET", "POST"])
@login_required
def vul_in(quiz_id):

    titel = db.execute("SELECT quiz_titel FROM quizes WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    questions = db.execute("SELECT * FROM questions WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    answers = db.execute("SELECT * FROM answers WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    random.shuffle(answers)


    if request.method == "POST":
        if 'submit_button' in request.form:

            participant_name = request.form.get("participantnaam")

            db.execute("INSERT INTO participants (quiz_id, name) VALUES (:quiz_id, :name)", quiz_id = quiz_id, name = participant_name)
            participant_id = db.execute("SELECT participant_id FROM participants WHERE name = :name", name = participant_name)[-1]["participant_id"]

            final_score = 0


            print(answers)
            for question in questions:
                answer_input = request.form[str(question['question_id'])]
                for answer in answers:
                    if answer['answer_id'] == int(answer_input):
                        final_score += answer["correct"]
                db.execute("INSERT INTO responses (participant_id, answer_id) VALUES (:participant_id, :answer_id)", participant_id = participant_id, answer_id = answer_input)

            final_score = final_score / len(questions)

            db.execute("UPDATE participants SET score = :score WHERE participant_id = :participant_id",
                          score = final_score, participant_id = participant_id)

        # return redirect("/index")
        return redirect("/index")


    else:
        return render_template("vul_in.html", questions = questions, titel = titel[0]['quiz_titel'], answers = answers, quiz_id = quiz_id)


@app.route("/maak_quiz", methods=["GET", "POST"])
def maak_quiz():
    if request.method == "POST":
        db.execute("INSERT INTO quizes (quiz_titel, user_id) VALUES (:quiz_titel, :user_id)",
            quiz_titel = request.form.get("quiz_titel"),
            user_id = session["user_id"])

        rows = db.execute("SELECT quiz_id FROM quizes WHERE user_id = :user_id", user_id=session["user_id"])
        session["quiz_id"] = rows[-1]["quiz_id"]

        return redirect("/voeg_vraag_toe")

    else:
        return render_template("maak_quiz.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/voeg_vraag_toe", methods=["GET", "POST"])
def voeg_vraag_toe():

    if request.method == "POST":

        if 'file' not in request.files:
            flash("Geen foto bijgevoegd")
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash("Geen foto geselecteerd")
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        db.execute("INSERT INTO questions (quiz_id, question, filename) VALUES (:quiz_id,:question,:filename)",
                    quiz_id=session["quiz_id"],
                    question=request.form.get("question"), filename=os.path.join(app.config['UPLOAD_FOLDER'], filename))

        rows = db.execute("SELECT question_id FROM questions WHERE quiz_id = :quiz_id", quiz_id=session["quiz_id"])
        session["question_id"] = rows[-1]["question_id"]

        db.execute("INSERT INTO answers (quiz_id, question_id, answer, correct) VALUES(:quiz_id, :question_id,:answer,:correct)",
                    quiz_id = session["quiz_id"],
                    question_id=session["question_id"],
                    answer=request.form.get("answer1"),
                    correct=True)

        for i in range(2,5):

            db.execute("INSERT INTO answers (quiz_id, question_id, answer, correct) VALUES(:quiz_id, :question_id, :answer, :correct)",
                        quiz_id = session["quiz_id"],
                        question_id=session["question_id"],
                        answer=request.form.get("answer" + str(i)),
                        correct=False)

        if "toevoegen" in request.form:
            return redirect("/voeg_vraag_toe")

        elif "beeindigen" in request.form:
            return redirect("/mijn_quizzes")

    else:
        return render_template("voeg_vraag_toe.html")

def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)