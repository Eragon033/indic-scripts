# I got some of the framework from CS50x Finance 2020 project

import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

from random import shuffle
import math

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

# Configure session to use filesystem (instead of signed cookies)
#app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL(os.getenv("DATABASE_URL").replace("://", "ql://", 1))

@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


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
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

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

@app.route("/")
@login_required
def index():
    return render_template("index.html")

@app.route("/varnamaala")
@login_required
def varnamaala():
    return render_template("varnamaala.html")

@app.route("/history")
@login_required
def history():

    rows = db.execute("SELECT * FROM history WHERE user_id = ? ORDER BY totaltime ASC LIMIT 3", session["user_id"])

    lead = []

    letters = {
               "1": "ಕ ಖ ಗ ಘ ಙ",
               "2": "ಚ ಛ ಜ ಝ ಞ",
               "3": "ಟ ಠ ಡ ಢ ಣ",
               "4": "ತ ಥ ದ ಧ ನ",
               "5": "ಪ ಫ ಬ ಭ ಮ",
               "6": "ಯ ರ ಲ ವ",
               "7": "ಶ ಷ ಸ ಹ"
               }

    for row in rows:
        numbers = row["letters"].split(" ")
        lis = []

        num = row["totaltime"]

        total_time = calculate_time(row["totaltime"])

        for i in numbers:
            lis.append(letters[i])
        letter = ' '.join(lis)

        s = str(row["timestamp"])
        i = s.index(" ")
        timestamp = [s[:i], s[i+1 : i+9]]
        # Date
        date = timestamp[0]
        # Time
        time = timestamp[1]

        lead.append((total_time, letter, date, time))

    lead = tuple(lead)

    rows = db.execute("SELECT * FROM history WHERE user_id = ? ORDER BY timestamp DESC", session["user_id"])

    data = []

    for row in rows:
        # options
        numbers = row["letters"].split(" ")
        lis = []

        # time taken
        total_time = calculate_time(row["totaltime"])

        for i in numbers:
            lis.append(letters[i])
        letter = ' '.join(lis)

        s = str(row["timestamp"])
        i = s.index(" ")
        timestamp = [s[:i], s[i+1 : i+9]]
        # Date
        date = timestamp[0]
        # Time
        time = timestamp[1]

        data.append((total_time, letter, date, time))

    return render_template("history.html", data=data, lead=lead)

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user id
    session.clear();

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        rows = db.execute("SELECT username FROM users");
        usernames = []
        for row in rows:
            usernames.append(row["username"].lower())

        # Ensure username is unique
        if request.form.get("username").lower() in usernames:
            return apology("Username alreay exists!")

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology ("must provide password", 403)

        password = request.form.get("password")

        # Ensure a safe password was submitted
        if len(password) < 8 or not (any(i.isdigit() for i in password) and any(i.isalpha() for i in password)):
            return apology("password must follow guidelines")

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology ("must confirm password", 403)

        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 403)

        # Generate hash of password
        hash_val = generate_password_hash(request.form.get("password"))

        # Store username and hash in table
        identity = db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", request.form.get("username"), hash_val)

        # Remember which user has registered
        session["user_id"] = identity

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/password", methods=["GET", "POST"])
@login_required
def password():
    """Change Password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology ("must provide password", 403)

        password = request.form.get("password")

        # Ensure a safe password was submitted
        if len(password) < 8 or not (any(i.isdigit() for i in password) and any(i.isalpha() for i in password)):
            return apology("password must follow guidelines")

        # Ensure confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology ("must confirm password", 403)

        # Ensure password and confirmation match
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords do not match", 403)

        # Generate hash of password
        hash_val = generate_password_hash(request.form.get("password"))

        # Update password of user
        db.execute("UPDATE users SET hash = ? WHERE id = ?", hash_val, session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("password.html")


@app.route("/game", methods=["GET", "POST"])
@login_required
def game():
    """Memory Game"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":

        return render_template("pregame.html")

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        if len(request.form.getlist("Letter")) == 0:
            return apology("must choose letters")

        options = {
                   "1": ["Ka", "Ka2", "Kha", "Kha2", "Ga", "Ga2", "Gha", "Gha2", "Ada", "Ada2"],
                   "2": ["Cha", "Cha2", "Chha", "Chha2", "Ja", "Ja2", "Jha", "Jha2", "Ee", "Ee2"],
                   "3": ["Ta", "Ta2", "Tha", "Tha2", "Da", "Da2", "Dha", "Dha2", "Nna", "Nna2"],
                   "4": ["Tth", "Tth2", "Thha", "Thha2", "Dda", "Dda2", "Dhha", "Dhha2", "Na", "Na2"],
                   "5": ["Pa", "Pa2", "Pha", "Pha2", "Ba", "Ba2", "Bha", "Bha2", "Ma", "Ma2"],
                   "6": ["Ya", "Ya2", "Ra", "Ra2", "La", "La2", "Va", "Va2"],
                   "7": ["Sha", "Sha2", "Shha", "Shha2", "Sa", "Sa2", "Ha", "Ha2"]
                   }

        letters = []
        global choices
        choices = ""

        # letters
        for i in request.form.getlist("Letter"):
            choices += i + " "
            letters.extend(options[i])

        choices = choices[:-1]

        length = len(letters)

        cards = [i for i in range(length)]
        shuffle(cards)

        # return (card number, letter, color of card) for each letter
        def pair(n):
            letter = letters[n]
            card = f"card{n+1}"
            # Hindi letter
            if "2" in letter:
                color = "red"
            # Kannada letter
            else:
                color = "blue"
            return [card, letter, color]

        result = map(pair, cards)
        data = tuple(result)

        # To determine width
        num = length/2

        if num == 4:
            width = 200
        elif num == 5:
            width = 190
        elif num in range(9, 11):
            width = 135
        elif num in range(13, 16):
            width = 115
        elif num in range(18, 19):
            width = 100
        elif num in range(19, 26):
            width = 90
        elif num in range(28, 34):
            width = 75

        return render_template("/game.html", data=data, choices=choices, w=width)

# Enter memory game data to database
@app.route("/enterdata", methods=["POST"])
@login_required
def enterdata():
    time = int(request.form.get("timer"))
    global choices
    db.execute("INSERT INTO history(user_id, totaltime, timestamp, letters) VALUES(?, ?, CURRENT_TIMESTAMP, ?)", session["user_id"], time, choices)
    return redirect("/history")

# Convert time to required format
def calculate_time(num):

    if num < 60:
        total_time = f"{num} s"

    elif num < 3600:
        n = math.floor(num / 60)
        minutes = 60 * n
        sec = num - minutes
        total_time = f"{n} min {sec} s"

    elif num < 86400:
        hn = math.floow(num / 3600)
        hr = 3600 * hn
        sec = num - hr
        mn = math.floor(sec / 60)
        minutes = 60 * mn
        s = sec - minutes
        total_time = f"{hn} hr {mn} min {s} s"
    else:
        dn = math.floor(num / 86400)
        total_time = f"{dn} day(s)"

    return total_time


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)