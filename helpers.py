import requests
import urllib.parse
import os

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

def add_up(my_stocks):
    added_up_dict = {}
    for stock in my_stocks:
        company_sym = stock["company_symbol"]
        if company_sym in added_up_dict:
            added_up_dict[company_sym]["share_amount"] += stock["share_amount"]
        else:
            added_up_dict[company_sym] = stock

    return added_up_dict


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        response = requests.get(f"https://cloud-sse.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}")
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None

def get_gif(zoekwoord):
    try:
        endpoint = (f"http://api.giphy.com/v1/gifs/search?api_key=aZlzaSFlPht6xjDQHEmQyfGpH7d758cp&q={zoekwoord}&start=0&size=1")
        if not zoekwoord:
            endpoint = "http://api.giphy.com/v1/gifs/random?api_key=aZlzaSFlPht6xjDQHEmQyfGpH7d758cp&start=0&size=1"
        response = requests.get(endpoint)
        giphy = response.json()
        if not zoekwoord:
            gif = giphy['data']['fixed_width_small_url']
        else:
            gif = giphy['data'][0]['images']['fixed_width_small']['url']
        return gif
    except requests.RequestException:
        return "https://media.giphy.com/media/VbnUQpnihPSIgIXuZv/giphy-downsized.gif"


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
