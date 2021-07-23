# -----------------------------------------------------------------------------------------------------------------------
import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

from random import shuffle

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
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///languages.db")

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
# -----------------------------------------------------------------------------------------------------------------------

@app.route("/")
@login_required
def index():
    return render_template("index.html")

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

        # Ensure username is valid
        for i in request.form.get("username"):
            if i in "'<>;,=&+":
                return apology("'<>;,=&+ not allowed in username")
                break

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

        #password = request.form.get("password")

        # Ensure a safe password was submitted
        #if len(password) < 8 or not (any(i.isdigit() for i in password) and any(i.isalpha() for i in password)):
        #    return apology("password must follow guidelines")

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

        #password = request.form.get("password")

        # Ensure a safe password was submitted
        #if len(password) < 8 or not (any(i.isdigit() for i in password) and any(i.isalpha() for i in password)):
        #    return apology("password must follow guidelines")

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


@app.route("/pregame", methods=["GET", "POST"])
@login_required
def game():
    """Memory Game"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":

        #options = [5, 10, 15, 20, 25, 29, 33]

        return render_template("pregame.html")#, numbers=options)

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        #if not request.form.get("number"):
         #   return apology("must provide a number")

        if len(request.form.getlist("Letter")) == 0:
            return apology("must choose letters")

        #options = [5, 10, 15, 20, 25, 29, 33]

        #num = int(request.form.get("number")) * 2

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

        choices = ""

        for i in request.form.getlist("Letter"):
            choices += i + " "
            letters.extend(options[i])

        length = len(letters)

        cards = [i for i in range(length)]
        shuffle(cards)

        def pair(n):
            letter = letters[n]
            card = f"card{n+1}"
            return [card, letter]

        result = map(pair, cards)
        data = tuple(result)

        #numbers = [4, 5, 10, 15, 20, 25, 29, 33]
        #index = numbers.index(length/2)
        #width = [190, 190, 135, 115, 105, 90, 75, 75][index]

        num = length/2

        if num == 4:
            width = 200
        elif num == 5:
            width = 190
        elif num in range(9, 11):
            width = 135
        elif num in range(13, 16):
            width = 115
        elif num in range(16, 19):
            width = 100
        elif num in range(19, 28):
            width = 90
        elif num == 28:
            widt
        elif num in range(29, 34):
            width = 75

        return render_template("/game.html", data=data, choices=choices[:-1], w=width)

        '''letters = letters[:num]

        numbers = [i for i in range(num)]
        shuffle(numbers)

        def pair(n):
            letter = letters[n]
            card = f"card{n+1}"
            return [card, letter]

        result = map(pair, numbers)
        data = tuple(result)

        index = options.index(int(request.form.get("number")))
        width = [190, 135, 115, 105, 90, 75, 75][index]

        return render_template("/game.html", data=data, length=num, w=width)'''

# -----------------------------------------------------------------------------------------------------------------------
def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
# -----------------------------------------------------------------------------------------------------------------------