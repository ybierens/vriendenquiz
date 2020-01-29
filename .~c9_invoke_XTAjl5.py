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


# maak applicatie
app = Flask(__name__)

# zorg ervoor dat templates automatisch herladen
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# zorg ervoor dat antwoorden niet worden gecashed
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# zorg ervoor dat session filesystem gebruikt (in plaats van signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# zorg ervoor dat de CS50 library SQLite database gebruikt
db = SQL("sqlite:///quiz.db")



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# deze route stuurt een foto vanaf de directory
@app.route('/UPLOAD_FOLDER/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)



# deze route redirect je naar login als je de server start
@app.route("/", methods=["GET", "POST"])
def home():
    return redirect("/index")



#################
#               #
#  GEREFACTORD  #
#               #
#################

# check of een gebruikersnaam beschikbaar is
@app.route("/check", methods=["GET"])
def check():

    gebruikersnaam = request.args.get("username")

    # zoek in database of er al een gebruiker is met die gebruikersnaam
    gebruikers = db.execute("SELECT user_id FROM users WHERE username = :gebruikersnaam", gebruikersnaam = gebruikersnaam)

    # return False als er al een gebruiker is met die gebruikersnaam
    if gebruikers:
        return jsonify(False)

    return jsonify(True)



#################
#               #
#  GEREFACTORD  #
#               #
#################

# check of iemand kan inloggen met wat is ingevuld
@app.route("/logincheck", methods=["GET"])
def logincheck():

    gebruikersnaam = request.args.get("gebruikersnaam")
    wachtwoord= request.args.get("wachtwoord")

    # haal gebruikersnaamgegevens uit de database
    gebruikersnaam_db = db.execute("SELECT * FROM users WHERE username = :gebruikersnaam", gebruikersnaam = gebruikersnaam)

    # return false als de gebruikersnaam niet in de database zit
    if not gebruikersnaam_db:
        return jsonify(False)

    # return true als het wachtwoord klopt
    if check_password_hash(gebruikersnaam_db[0]['password'], wachtwoord) == True:
        return jsonify(True)

    else:
        return jsonify(False)



#################
#               #
#  GEREFACTORD  #
#               #
#################

# de login route, checkt of je mag inloggen met de ingevulde informatie
@app.route("/login", methods=["GET", "POST"])
def login():

    # vergeet user_id
    session.clear()

    if request.method == "POST":

        # check of er een code is ingevuld om te zoeken naar een quiz
        if 'quiz_zoek_input' in request.form:

            quiz_id = str(request.form.get("quiz_zoek_input"))

            # maak de url van die quiz
            quiz_url = "/vul_in/"+quiz_id

            return redirect(quiz_url)


        # anders wil je gebruiker inloggen
        gebruikersnaam = request.form.get("gebruikersnaam")
        wachtwoord = request.form.get("wachtwoord")

        # haal gebruikersnaamgegevens uit database
        gebruiker_db = db.execute("SELECT * FROM users WHERE username = :gebruikersnaam", gebruikersnaam=gebruikersnaam)

        # check dat het wachtwoord klopt
        if gebruiker_db is False or not check_password_hash(gebruiker_db[0]["password"], wachtwoord):
            return apology("verkeerde gebruikersnaam en/of wachtwoord", 403)

        # sla op welke user is ingelogd
        session["user_id"] = gebruiker_db[0]["user_id"]

        # Redirect user to home page
        return redirect("/index")

    # render het login scherm
    else:
        return render_template("login.html")



#################
#               #
#  GEREFACTORD  #
#               #
#################

# log uit route
@app.route("/logout")
def logout():

    # vergeet user_id
    session.clear()

    return redirect("/index")



#################
#               #
#  GEREFACTORD  #
#               #
#################

# registreer route, checkt of een gebruikersnaam al in gebruik is, en zet het in de database
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # haal wachtwoord uit form en hash het
        wachtwoord_hash = generate_password_hash(request.form.get("wachtwoord"), method = 'pbkdf2:sha256', salt_length=8)
        gebruikersnaam = request.form.get("gebruikersnaam")

        # check of de gebruikersnaam al in gebruik is
        if db.execute("SELECT user_id FROM users WHERE username = :gebruikersnaam", gebruikersnaam = gebruikersnaam) is True:
            return apology("deze gebruikersnaam wordt al gebruikt", 403)

        # zet gebruiker in database
        db.execute("INSERT INTO users (username, password) VALUES (:gebruikersnaam, :wachtwoord)",
            gebruikersnaam = gebruikersnaam, wachtwoord = wachtwoord_hash)

        # haal het toegewezen user_id op
        user_id = db.execute("SELECT user_id FROM users WHERE username = :gebruikersnaam", gebruikersnaam = gebruikersnaam)

        # sla user_id op in session voor later gebruik
        session["user_id"] = user_id[0]['user_id']

        return redirect("/index")

    else:
        return render_template("register.html")



#################
#               #
#  GEREFACTORD  #
#               #
#################

# de homepage route als je bent ingelogd, laat de top 5 participanten en alle participanten zien
@app.route("/index")
@login_required
def index():

    mijn_quizes = db.execute("SELECT * FROM quizes WHERE user_id = :username",username=session["user_id"])

    participanten_lijst = []

    # haal voor alle quizes van de ingelogde user de participanten op en voeg de quiznaam toe
    for quiz in mijn_quizes:
        for participant in db.execute("SELECT * FROM participants WHERE  quiz_id = :quiz", quiz=quiz['quiz_id']):
            participant["quizname"] = quiz["quiz_titel"]
            participanten_lijst.append(participant)

    participanten_lijst.reverse()

    # haal de top 5 scores uit alle participanten
    top_participanten = sorted(participanten_lijst, key=lambda x:x["score"])
    top_participanten.reverse()

    return render_template("index.html", participanten_lijst=percentage(participanten_lijst), top_participanten=top_participanten[:5])



#################
#               #
#  GEREFACTORD  #
#               #
#################

# route die checkt of de quiz waarnaar gezocht wordt bestaat
@app.route("/quizcheck/<quiz>", methods=["GET", "POST"])
def quizcheck(quiz):

    # check of de quiz in onze database zit
    quiz_db = db.execute("SELECT * FROM quizes WHERE quiz_id = :quiz_id", quiz_id = quiz)


    if quiz_db:
        return jsonify(True)

    else:
        return jsonify(False)




#################
#               #
#  GEREFACTORD  #
#               #
#################

# route die alle aangemaakte quizzen van de gebruiker ophaalt
@app.route("/mijn_quizzes")
@login_required
def mijn_quizzes():

    # haal alle quizzen van de gebruiker op uit de database
    quizes = db.execute("SELECT * FROM quizes WHERE user_id = :user_id", user_id = session['user_id'])

    return render_template("mijn_quizzes.html", quizes = quizes)



#################
#               #
#  GEREFACTORD  #
#               #
#################

# route die een quiz verwijdert
@app.route("/verwijder_quiz")
@login_required
def verwijder_quiz():

    # haal quiz_id op van de quiz die verwijderd gaat worden
    quiz_id = request.args.get("quiz_id")

    # verwijder alle ingevulde antwoorden voor alle participanten van de quiz
    for participant_id in db.execute("SELECT participant_id FROM participants WHERE quiz_id = :quiz_id", quiz_id = quiz_id):
        db.execute("DELETE FROM responses WHERE participant_id = :participant_id", participant_id = participant_id["participant_id"])

    # verwijder alle participanten, vragen, antwoorden en de quiz zelf
    db.execute("DELETE FROM participants WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    db.execute("DELETE FROM questions WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    db.execute("DELETE FROM answers WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    db.execute("DELETE FROM quizes WHERE quiz_id = :quiz_id", quiz_id = quiz_id)

    return redirect("/mijn_quizzes")



#################
#               #
#  GEREFACTORD  #
#               #
#################

# route die alle vragen van een quiz laat zien, en alle data opslaat als die quiz is ingevuld
@app.route("/vul_in/<quiz_id>", methods=["GET", "POST"])
def vul_in(quiz_id):

    # haal alle data van de quiz op
    quiz_data = db.execute("SELECT quiz_titel, gif, dankwoord FROM quizes WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    vragen = db.execute("SELECT * FROM questions WHERE quiz_id = :quiz_id", quiz_id = quiz_id)
    antwoorden = db.execute("SELECT * FROM answers WHERE quiz_id = :quiz_id", quiz_id = quiz_id)


    # doe de antwoorden in random volgorde
    random.shuffle(antwoorden)

    titel = quiz_data[0]["quiz_titel"]
    gif = quiz_data[0]["gif"]
    dankwoord = quiz_data[0]["dankwoord"]


    if request.method == "POST":

        # haal de ingevulde naam en opmerking op
        participant_name = request.form.get("participantnaam")
        opmerking = request.form.get("opmerking")

        # zet de participant in de database
        db.execute("INSERT INTO participants (quiz_id, name, comment) VALUES (:quiz_id, :naam, :opmerking)",
        quiz_id = quiz_id, naam = participant_name, opmerking=opmerking)

        # haal het toegewezen participant_id op
        participant_id = db.execute("SELECT participant_id FROM participants WHERE name = :naam AND quiz_id = :quiz_id",
            naam = participant_name, quiz_id = quiz_id)[0]["participant_id"]

        # zet de ingevulde antwoorden in de database, en bereken de score
        eindscore = 0

        for vraag in vragen:
            antwoord_input = request.form[str(vraag['question_id'])]
            for antwoord in antwoorden:
                if antwoord['answer_id'] == int(antwoord_input):
                    eindscore += antwoord["correct"]

            db.execute("INSERT INTO responses (participant_id, answer_id) VALUES (:participant_id, :answer_id)",
                participant_id = participant_id, answer_id = antwoord_input)


        eindscore = eindscore / len(vragen)


        # zet de score in de database bij de participant
        db.execute("UPDATE participants SET score = :score WHERE participant_id = :participant_id",
            score = eindscore, participant_id = participant_id)


        # haal de score van de andere participanten van deze quiz op
        alle_scores = db.execute("SELECT score FROM participants WHERE  quiz_id = :quiz", quiz=quiz_id)

        # voeg een dictionary met de score van de participant toe aan een lijst van alle scores
        nieuw_score_dict = {"score":eindscore, "name":participant_name}
        alle_scores.append(nieuw_score_dict)

        # sorteer de lijst op score
        scores_op_volgorde = sorted(alle_scores, key=lambda x:x["score"])
        scores_op_volgorde.reverse()

        # bereken de positie van de huidige participant
        positie = scores_op_volgorde.index(nieuw_score_dict) + 1

        return render_template("eindscherm.html", gif=gif, dankwoord=dankwoord, positie=positie, score=eindscore*100, participant_id=participant_id)


    else:
        return render_template("vul_in.html", vragen = vragen, titel = titel, antwoorden = antwoorden, quiz_id = quiz_id,
                                aantal_vragen = len(vragen), eerste_id = vragen[0]['question_id'])



#################
#               #
#  GEREFACTORD  #
#               #
#################

# de route waarin je een quiz maakt voordat je de vragen gaat toevoegen
@app.route("/maak_quiz", methods=["GET", "POST"])
@login_required
def maak_quiz():
    if request.method == "POST":

        # haal de data op
        dankwoord = request.form.get("dankwoord")
        quiz_titel = request.form.get("quiz_titel")
        user_id = session["user_id"]
        gif = get_gif(request.form["zoekwoord"])


        # zet de quiz data in de database
        db.execute("INSERT INTO quizes (quiz_titel, user_id, gif, dankwoord) VALUES (:quiz_titel, :user_id, :gif, :dankwoord)",
            quiz_titel = quiz_titel, user_id = user_id, gif=gif, dankwoord = dankwoord)

        # haal quiz_id op
        quiz_id = db.execute("SELECT quiz_id FROM quizes WHERE user_id = :user_id", user_id = user_id)

        # voeg het quiz_id toe aan session
        session["quiz_id"] = quiz_id[-1]["quiz_id"]

        return redirect("/voeg_vraag_toe")

    else:
        return render_template("maak_quiz.html")



@app.route("/voeg_vraag_toe", methods=["GET", "POST"])
@login_required
def voeg_vraag_toe():

    if request.method == "POST":

        questions = request.form.get("getal_vragen")
        for i in range(1, (int(questions) + 1)):

            file = request.files["card" + str(i) + "_file"]
            if not allowed_file(file.filename):
                flash("Dat bestandstype wordt niet ondersteund!")
                return redirect(request.url)

            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filename = (url_for('uploaded_file', filename=filename))

            db.execute("INSERT INTO questions (quiz_id, question, filename) VALUES (:quiz_id, :question, :filename)",
                        quiz_id=session["quiz_id"],
                        question=request.form.get("card" + str(i) + "_question"),
                        filename=filename)

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



#################
#               #
#  GEREFACTORD  #
#               #
#################

# de route die alle participanten van een quiz laat zien
@app.route("/results/<quiz_id>", methods=["GET", "POST"])
@login_required
def results(quiz_id):

    # haal de naam van de quiz en de participanten op
    quiz_naam = db.execute("SELECT quiz_titel FROM quizes WHERE quiz_id = :quiz_id", quiz_id=quiz_id)[0]["quiz_titel"]
    participanten_lijst = db.execute("SELECT * FROM participants WHERE quiz_id = :quiz_id", quiz_id=quiz_id)

    print(participanten_lijst)
    # draai de participantenlijst om zodat de meest recenten bovenaan komen
    participanten_lijst.reverse()

    # maak een lijst met de participanten op volgorde van de score
    top_participanten = sorted(participanten_lijst, key=lambda x:x["score"])
    top_participanten.reverse()


    return render_template("results.html", participanten_lijst=participanten_lijst, quiz_naam=quiz_naam, top_participanten=top_participanten[:5])



#################
#               #
#  GEREFACTORD  #
#               #
#################

# de route die laat zien wat een participant heeft ingevuld bij een quiz
@app.route("/antwoord/<participant_id>", methods=["GET", "POST"])
@login_required
def antwoord(participant_id):
    # haal de quiz data en de ingevulde antwoorden van de participant op
    quiz = db.execute("SELECT quiz_id FROM participants WHERE participant_id = :pid", pid=participant_id)[0]["quiz_id"]
    quizvragen = db.execute("SELECT * FROM questions WHERE quiz_id = :quiz", quiz=quiz)
    antwoorden = db.execute("SELECT * FROM responses WHERE participant_id = :pid", pid=participant_id)

    # haal alle multiple choice (mp) antwoorden op
    mp_antwoorden = []
    for vraag in quizvragen:
        for mp in db.execute("SELECT * FROM answers WHERE question_id = :question", question=vraag["question_id"]):
            mp_antwoorden.append(mp)


    # ieder multiplechoice antwoord heeft 1 van 4 statussen
    # 1: antwoord is fout en niet geselecteerd door de user
    # 2: antwoord is fout en geselecteerd door de user
    # 3: antwoord is goed en niet geselecteerd door de user
    # 4: antwoord is goed en geselecteerd door de user

    for mp_antwoord in mp_antwoorden:
        for user_antwoord in antwoorden:
            if mp_antwoord["answer_id"] == user_antwoord["answer_id"]:
                user_antwoord_id = user_antwoord["answer_id"]

        # voeg de status aan het antwoord toe
        if mp_antwoord["answer_id"] == user_antwoord_id and mp_antwoord["correct"] == 1:
            mp_antwoord["status"] = 4
        elif mp_antwoord["answer_id"] == user_antwoord_id and mp_antwoord["correct"] == 0:
            mp_antwoord["status"] = 2
        elif mp_antwoord["correct"] == 1:
            mp_antwoord["status"] = 3
        else:
            mp_antwoord["status"] = 1


    return render_template("antwoord.html", quizvragen = quizvragen, antwoorden = mp_antwoorden)



#################
#               #
#  GEREFACTORD  #
#               #
#################

# de route die alle foto's in je quizzen laat zien
@app.route("/gallerij", methods=["GET"])
@login_required
def gallerij():

    # haal de quizzen van de gebruiker op
    gebruikerquizes = db.execute("SELECT quiz_id FROM quizes WHERE user_id=:user_id", user_id=session["user_id"])

    # voeg alle fotos van alle quizen toe aan fotolijsten
    fotolijsten = []

    for quiz in gebruikerquizes:
        for filedict in db.execute("SELECT filename FROM questions WHERE quiz_id=:quiz_id", quiz_id=quiz['quiz_id']):
            fotolijsten.append(filedict['filename'])

    return render_template("gallerij.html", fotolijsten = fotolijsten)



#################
#               #
#  GEREFACTORD  #
#               #
#################

# de route die de pagina waarop je je gegevens kan aanpassen laat zien
@app.route("/mijn_account", methods=["GET", "POST"])
def mijn_account():

    # haal de gebruikersnaam van de gebruiker op
    gebruiker = db.execute("SELECT username FROM users WHERE user_id=:user_id", user_id=session['user_id'])[0]["username"]

    return render_template("mijn_account.html", gebruiker=gebruiker)



#################
#               #
#  GEREFACTORD  #
#               #
#################

# de route waarin je je gebruikersnaam kan aanpassen
@app.route("/verander_gebruikersnaam", methods=["GET", "POST"])
def verander_gebruikersnaam():
    if request.method == "POST":

        # haal de nieuwe gebruikersnaam op
        nieuw = request.form.get("nieuw")

        db.execute("UPDATE users SET username = :username WHERE user_id = :user_id", username = nieuw, user_id = session["user_id"])

        return redirect("/mijn_account")

    else:
        return render_template("verander_gebruikersnaam.html")



#################
#               #
#  GEREFACTORD  #
#               #
#################

# de route waarin je je wachtwoord kan aanpassen
@app.route("/verander_wachtwoord", methods=["GET", "POST"])
def verander_wachtwoord():
    if request.method == "POST":

        # haal het nieuw wachtwoord op
        nieuw = request.form.get("nieuw")

        # hash het nieuw wachtwoord
        gehasht = generate_password_hash(nieuw, method = 'pbkdf2:sha256', salt_length=8)

        db.execute("UPDATE users SET password = :password WHERE user_id = :user_id", password=gehasht, user_id = session["user_id"])

        return redirect("/mijn_account")

    else:
        return render_template("verander_wachtwoord.html")


# handelt de errors af
def errorhandler(e):
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)



# luister voor errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)