# -----------------------------------------------------------------------------------------------------------------------
import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

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


@app.route("/pregame")
@login_required
def game():
    """Memory Game"""

    # User reached route via GET (as by clicking a link or via redirect)
    if request.method == "GET":

        numbers = [x for x in range(5, 20, 5)]
        return render_template("pregame.html", numbers=numbers)

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("number"):
            return apology("must provide a number")

        number = int(request.form.get("number")) * 2
        letters = ["Ka", "Ka2", "Kh", "Kh2", "Ga", "Ga2", "Gh", "Gh2", "Ad", "Ad2"]

        cards = ["card{}".format(x) for x in range(1, number)]

        return render_template("/game.html", letters=letters[:number], cards=cards)

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