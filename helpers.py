import requests
import urllib.parse
import os
import random

from flask import redirect, render_template, request, session
from functools import wraps



def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/1.0/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function



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




def percentage(answer_list):
    for answer in answer_list:
        answer["score"] = str(answer["score"] * 100) + "%"

    return answer_list
