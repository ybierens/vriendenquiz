import requests
import urllib.parse
import os
import random

from flask import redirect, render_template, request, session
from functools import wraps


# de pagina die gelaad wordt als er iets fout gaat
def apology(message, code=400):
    def escape(s):
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code

# de route voor als je naar een pagina wilt gaan waarvoor je ingelogd moet zijn
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


# functie waarmee een gif wordt opgehaald
def get_gif(zoekwoord):
    try:
        randomnummer = random.randint(1,25)
        if zoekwoord:
            endpoint = (f"http://api.giphy.com/v1/gifs/search?api_key=aZlzaSFlPht6xjDQHEmQyfGpH7d758cp&q={zoekwoord}&limit=25&start=0&size=1")
            response = requests.get(endpoint)
            giphy = response.json()
            if len(giphy['data']) < 25:
                return "https://media.giphy.com/media/VbnUQpnihPSIgIXuZv/giphy-downsized.gif"
            else:
                gif = giphy['data'][randomnummer]['images']['fixed_width_small']['url']
                return gif
        if not zoekwoord:
            return "https://media.giphy.com/media/VbnUQpnihPSIgIXuZv/giphy-downsized.gif"
    except requests.RequestException:
        return "https://media.giphy.com/media/VbnUQpnihPSIgIXuZv/giphy-downsized.gif"


# zet een commagetal om naar een percentage
def percentage(answer_list):
    for answer in answer_list:
        answer["score"] = str(answer["score"] * 100) + "%"

    return answer_list
