import os
import random

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session, send_from_directory, url_for
from flask_session import Session
from tempfile import mkdtemp

from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename


from helpers import login_required, get_gif, percentage, apology

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
        return redirect("/index")

@app.route("/index")
@login_required
def index():

    session["user_id"]
    my_quizes = db.execute("SELECT * FROM quizes WHERE user_id = :username",username=session["user_id"])

    participants_list = []

    for quiz in my_quizes:
        for participant in db.execute("SELECT * FROM participants WHERE  quiz_id = :quiz", quiz=quiz['quiz_id']):
            participant["quizname"] = quiz["quiz_titel"]
            participants_list.append(participant)

    participants_list.reverse()

    top_participants = sorted(participants_list, key=lambda x:x["score"])
    top_participants.reverse()

    return render_template("index.html", participants_list=percentage(participants_list), top_participants=top_participants[:5])


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


@app.route("/quizcheck/<quiz>", methods=["GET", "POST"])
def quizcheck(quiz):

    #quiz = request.args.get("quiz")

    quiz_zoek = db.execute("SELECT * FROM quizes WHERE quiz_id = :quiz_id", quiz_id = quiz)

    if quiz_zoek:
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
        print("1")
        print(request.form.get('quiz_zoek_input'))
        if 'quiz_zoek_input' in request.form:


            quiz_id = str(request.form.get("quiz_zoek_input"))

            quiz_url = "/vul_in/"+quiz_id

            return redirect(quiz_url)


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
def vul_in(quiz_id):

    quiz_data = db.execute("SELECT quiz_titel, gif, dankwoord FROM quizes WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    questions = db.execute("SELECT * FROM questions WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    answers = db.execute("SELECT * FROM answers WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    random.shuffle(answers)

    titel = quiz_data[0]["quiz_titel"]
    gif = quiz_data[0]["gif"]
    dankwoord = quiz_data[0]["dankwoord"]


    if request.method == "POST":
        if 'submit_button' in request.form:

            participant_name = request.form.get("participantnaam")
            opmerking = request.form.get("opmerking")

            db.execute("INSERT INTO participants (quiz_id, name, comment) VALUES (:quiz_id, :name, :comment)", quiz_id = quiz_id, name = participant_name, comment=opmerking)
            participant_id = db.execute("SELECT participant_id FROM participants WHERE name = :name", name = participant_name)[-1]["participant_id"]

            final_score = 0

            for question in questions:
                answer_input = request.form[str(question['question_id'])]
                for answer in answers:
                    if answer['answer_id'] == int(answer_input):
                        final_score += answer["correct"]
                db.execute("INSERT INTO responses (participant_id, answer_id) VALUES (:participant_id, :answer_id)", participant_id = participant_id, answer_id = answer_input)

            final_score = final_score / len(questions)


            db.execute("UPDATE participants SET score = :score WHERE participant_id = :participant_id",
                          score = final_score, participant_id = participant_id)

            alle_scores = db.execute("SELECT score FROM participants WHERE  quiz_id = :quiz", quiz=quiz_id)

            nieuw_score_dict = {"score":final_score, "name":participant_name}
            alle_scores.append(nieuw_score_dict)
            scores_op_volgorde = sorted(alle_scores, key=lambda x:x["score"])
            scores_op_volgorde.reverse()
            positie = scores_op_volgorde.index(nieuw_score_dict) + 1

        return render_template("eindscherm.html", gif=gif, dankwoord=dankwoord, positie=positie, score=final_score*100)


    else:
        return render_template("vul_in.html", questions = questions, titel = titel, answers = answers, quiz_id = quiz_id)


@app.route("/maak_quiz", methods=["GET", "POST"])
@login_required
def maak_quiz():
    if request.method == "POST":
        zoekwoord = request.form["zoekwoord"]
        gif = get_gif(zoekwoord)
        db.execute("INSERT INTO quizes (quiz_titel, user_id, gif, dankwoord) VALUES (:quiz_titel, :user_id, :gif, :dankwoord)",
            quiz_titel = request.form.get("quiz_titel"),
            user_id = session["user_id"], gif=gif,
            dankwoord = request.form.get("dankwoord"))

        rows = db.execute("SELECT quiz_id FROM quizes WHERE user_id = :user_id", user_id=session["user_id"])
        session["quiz_id"] = rows[-1]["quiz_id"]

        return redirect("/voeg_vraag_toe")

    else:
        return render_template("maak_quiz.html")

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/voeg_vraag_toe", methods=["GET", "POST"])
@login_required
def voeg_vraag_toe():

    if request.method == "POST":

#        if 'file' not in request.files:
 #           flash("Geen foto bijgevoegd")
  #          return redirect(request.url)
   #     file = request.files['file']
    #    if file.filename == '':
     #       flash("Geen foto geselecteerd")
      #      return redirect(request.url)
#        if not allowed_file(file.filename):
 #           flash("Dat bestandstype wordt niet ondersteund!")
  #          return redirect(request.url)
   #     if file and allowed_file(file.filename):
    #        filename = secure_filename(file.filename)
     #       file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
      #      filename = (url_for('uploaded_file', filename=filename))

        questions = request.form.get("getal_vragen")
        for i in range(1, (int(questions) + 1)):

            db.execute("INSERT INTO questions (quiz_id, question) VALUES (:quiz_id, :question)",
                        quiz_id=session["quiz_id"],
                        question=request.form.get("card" + str(i) + "_question"))

            rows = db.execute("SELECT question_id FROM questions WHERE quiz_id = :quiz_id", quiz_id=session["quiz_id"])
            session["question_id"] = rows[-1]["question_id"]

            db.execute("INSERT INTO answers (quiz_id, question_id, answer, correct) VALUES(:quiz_id, :question_id,:answer,:correct)",
                        quiz_id = session["quiz_id"],
                        question_id=session["question_id"],
                        answer=request.form.get("card" + str(i) + "_answer1"),
                        correct=True)

            getal = request.form.get("card" + str(i) + "_getal")
            for j in range(2, int(getal) + 1):

                db.execute("INSERT INTO answers (quiz_id, question_id, answer, correct) VALUES(:quiz_id, :question_id, :answer, :correct)",
                            quiz_id = session["quiz_id"],
                            question_id=session["question_id"],
                            answer=request.form.get("card" + str(i) + "_answer" + str(j)),
                            correct=False)


        if "toevoegen" in request.form:
            return redirect("/voeg_vraag_toe")

        elif "beeindigen" in request.form:
            return redirect("/mijn_quizzes")

    else:
        return render_template("voeg_vraag_toe.html")

@app.route('/UPLOAD_FOLDER/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

@app.route("/results/<quiz_id>", methods=["GET", "POST"])
@login_required
def results(quiz_id):

    quiz_name = db.execute("SELECT quiz_titel FROM quizes WHERE quiz_id = :quiz_id", quiz_id=quiz_id)[0]["quiz_titel"]

    participants_list = []

    for participant in db.execute("SELECT * FROM participants WHERE quiz_id = :quiz", quiz=quiz_id):
        participants_list.append(participant)

    participants_list.reverse()

    top_participants = sorted(participants_list, key=lambda x:x["score"])
    top_participants.reverse()


    return render_template("results.html", participants_list=participants_list, quiz_name=quiz_name, top_participants=top_participants[:5])


@app.route("/antwoord/<participant_id>", methods=["GET", "POST"])
@login_required
def antwoord(participant_id):

    quiz = db.execute("SELECT quiz_id FROM participants WHERE participant_id = :pid", pid=participant_id)[0]["quiz_id"]
    quizvragen = db.execute("SELECT * FROM questions WHERE quiz_id = :quiz", quiz=quiz)

    mpantwoorden = []
    for vraag in quizvragen:
        for mp in db.execute("SELECT * FROM answers WHERE question_id = :question", question=vraag["question_id"]):
            mpantwoorden.append(mp)

    antwoorden = db.execute("SELECT * FROM responses WHERE participant_id = :pid", pid=participant_id)


    # ieder multiplechoice antwoord heeft 1 van 4 statussen
    # 1: antwoord is fout en niet geselecteerd door de user
    # 2: antwoord is fout en geselecteerd door de user
    # 3: antwoord is goed en niet geselecteerd door de user
    # 4: antwoord is goed en geselecteerd door de user

    for antwoord in mpantwoorden:
        user_antwoord_id = 0
        for user_antwoord in antwoorden:
            if antwoord["answer_id"] == user_antwoord["answer_id"]:
                user_antwoord_id = user_antwoord["answer_id"]

        if antwoord["answer_id"] == user_antwoord_id and antwoord["correct"] == 1:
            antwoord["status"] = 4
        elif antwoord["answer_id"] == user_antwoord_id and antwoord["correct"] == 0:
            antwoord["status"] = 2
        elif antwoord["correct"] == 1:
            antwoord["status"] = 3
        else:
            antwoord["status"] = 1


    return render_template("antwoord.html", questions = quizvragen, answers = mpantwoorden)


@app.route("/gallerij", methods=["GET"])
@login_required
def gallerij():
    gebruikerquizes = db.execute("SELECT quiz_id FROM quizes WHERE user_id=:user_id", user_id=session["user_id"])
    fotolijsten = []
    for quiz in gebruikerquizes:
        fotos = db.execute("SELECT filename FROM questions WHERE quiz_id=:quiz_id", quiz_id=quiz['quiz_id'])
        fotolijsten.append(fotos)
    fotolijst = []
    for element in fotolijsten:
        for filedict in element:
            fotolijst.append(filedict['filename'])
    return render_template("gallerij.html", fotolijst=fotolijst)



def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)

# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)