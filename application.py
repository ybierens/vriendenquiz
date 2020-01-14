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
db = SQL("sqlite:///finance.db")


@app.route("/")
@login_required
def index():

    # extract data from the database
    my_purchases = db.execute("SELECT * FROM purchases WHERE user_id = :id_user",
                          id_user=session["user_id"])

    my_cash = db.execute("SELECT cash FROM users WHERE id = :id_user",
                          id_user=session["user_id"])[0]["cash"]

    my_sold = db.execute("SELECT company_symbol, share_amount FROM sold WHERE user_id = :id_user",
                          id_user=session["user_id"])

    # merge shares from the same company
    all_shares_dict = add_up(my_purchases)
    all_sold_dict = add_up(my_sold)

    # add the sold share to the bought shares to get the current amount
    for share in all_shares_dict:
        if share in all_sold_dict:
            all_shares_dict[share]["share_amount"] += all_sold_dict[share]["share_amount"]

    total = 0

    # update to live prices and convert to us dollar
    for share in all_shares_dict:
        live = lookup(all_shares_dict[share]["company_symbol"])["price"]
        all_shares_dict[share]["share_price"] = usd(live)
        total_per_stock = live * all_shares_dict[share]["share_amount"]
        total += total_per_stock
        all_shares_dict[share]["total_value"] = usd(total_per_stock)


    total = usd(total + my_cash)
    return render_template("index.html", my_purchases=all_shares_dict, total=total, my_cash=usd(my_cash))

@app.route("/cash", methods=["GET", "POST"])
@login_required
def cash():
    if request.method == "POST":
        amount = request.form.get("amount")
        db.execute("UPDATE users SET cash = cash + :amount WHERE id = :id_user",
                          amount=amount, id_user=session["user_id"])
        return redirect("/")

    else:
        return render_template("cash.html")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():

    """Buy shares of stock"""
    if request.method == "POST":

        amountshares = request.form.get("shares")
        syminput = request.form.get("symbol")

        # check if everthing is filled in correctly
        if not amountshares:
            return apology("must provide amount", 400)

        if not syminput:
            return apology("must provide symbol", 400)

        try:
            amountshares = int(amountshares)
        except ValueError:
            return apology("You have to buy at least 1 share", 400)

        if amountshares <= 0:
            return apology("You have to buy at least 1 share", 400)

        if not syminput:
            return apology("Enter symbol", 400)

        searchresult = lookup(syminput)

        if not searchresult:
            return apology("This symbol doesn't exist", 400)

        current_amount = db.execute("SELECT cash FROM users WHERE id = :id_user",
                          id_user=session["user_id"])

        # calculate the value of the purchase
        price_purchase = searchresult["price"] * amountshares

        if current_amount[0]["cash"] <= price_purchase:
            return apology("You don't have enough cash", 400)


        # insert and update the data
        db.execute("INSERT INTO purchases (user_id, company_name, company_symbol, share_amount, share_price) VALUES (:user_id, :company_name, :company_symbol, :share_amount, :share_price)",
                user_id=session["user_id"], company_name=searchresult["name"], company_symbol=searchresult["symbol"], share_amount=amountshares, share_price=searchresult["price"])


        db.execute("UPDATE users SET cash = cash - :new_purchase WHERE id = :id_user",
                          new_purchase = price_purchase, id_user=session["user_id"])

        return redirect("/")

    else:
        return render_template("buy.html")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username_try = request.args.get("username")
    print(username_try)
    if len(username_try) == 0:
        return jsonify(False)

    # extract the data from the database
    check = db.execute("SELECT username FROM users WHERE username = :user",
                        user=username_try)

    if len(check) > 0:
        return jsonify(False)

    else:
        return jsonify(True)




@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # extract data from the database
    my_sold = db.execute("SELECT *FROM sold WHERE user_id = :id_user",
                          id_user=session["user_id"])

    my_purchases = db.execute("SELECT * FROM purchases WHERE user_id = :id_user",
                          id_user=session["user_id"])

    my_history = my_sold + my_purchases

    # sort by time
    my_history.sort(key=lambda x: x["time_bought"])

    # convert to us dollar
    for transaction in my_history:
        transaction["share_price"] = usd(transaction["share_price"])


    return render_template("history.html", my_history=my_history)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

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


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""

    if request.method == "POST":


        # check if everthing is filled in correctly
        syminput = request.form.get("symbol")

        if not syminput:
            return apology("Enter symbol", 400)

        searchresult = lookup(syminput)

        if not searchresult:
            return apology("This symbol doesn't exist", 400)

        searchresult["price"] = usd(searchresult["price"])

        return render_template("quoted.html", searchresult = searchresult)

    else:
        return render_template("quote.html")




@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        usern = request.form.get("username")
        passw = request.form.get("password")
        passcon = request.form.get("confirmation")

        # check if everything is filled in correctly
        if not usern:
            return apology("must provide username", 400)

        elif not passw:
            return apology("must provide password", 400)

        elif not passcon:
            return apology("must confirm password", 400)

        elif passw != passcon:
            return apology("passwords don't match", 400)

        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=usern)

        if len(rows) == 1:
            return apology("this username is already taken", 400)

        # insert into database
        db.execute("INSERT INTO users (username, hash) VALUES (:username, :hashpas)",
                username=usern, hashpas=generate_password_hash(passw, method='pbkdf2:sha256', salt_length=8))


        return redirect("/")

    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "POST":

        stock_selected = request.form.get("symbol")
        stock_amount = request.form.get("shares")

        # check if everything is filled in correctly
        if not stock_selected:
            return apology("Select a stock", 400)

        if not stock_amount:
            return apology("Select a stock amount", 400)

        # check if it's a integer
        try:
            stock_amount = int(stock_amount)
        except ValueError:
            return apology("You have to buy at least 1 share", 400)


        # extract the data from the database
        my_purchases = db.execute("SELECT * FROM purchases WHERE user_id = :id_user",
                          id_user=session["user_id"])

        # merge the shares from the same company
        all_shares_dict = add_up(my_purchases)

        if stock_selected not in all_shares_dict:
            return apology("You don't own this stock", 400)

        if stock_amount > all_shares_dict[stock_selected]["share_amount"]:
            return apology("You don't own enough stock", 400)

        stock_lookup = lookup(stock_selected)
        stock_current_price = stock_lookup["price"]

        price_reduction = stock_current_price * stock_amount

        # insert into and update the database
        db.execute("INSERT INTO sold (user_id, company_name, company_symbol, share_amount, share_price) VALUES (:user_id, :company_name, :company_symbol, :share_amount, :share_price)",
                user_id=session["user_id"], company_name=stock_current_price, company_symbol=stock_selected, share_amount=stock_amount * -1, share_price=stock_current_price)

        db.execute("UPDATE users SET cash = cash + :new_sold WHERE id = :id_user",
                          new_sold = price_reduction, id_user=session["user_id"])

        return redirect("/")


    else:

        # extract the current shares owned
        my_purchases = db.execute("SELECT company_symbol, share_amount FROM purchases WHERE user_id = :id_user",
                          id_user=session["user_id"])

        my_sold = db.execute("SELECT company_symbol, share_amount FROM sold WHERE user_id = :id_user",
                          id_user=session["user_id"])

        all_shares_dict = add_up(my_purchases)
        all_sold_dict = add_up(my_sold)

        my_stocks = []

        # add the sold share to the bought shares to see if any are still owned
        for share in all_shares_dict:
            if share in all_sold_dict:
                if all_shares_dict[share]["share_amount"] + all_sold_dict[share]["share_amount"] > 0:
                    my_stocks.append(share)
            else:
                my_stocks.append(share)


        return render_template("sell.html", my_stocks=my_stocks)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
