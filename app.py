from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required

# Configure application
app = Flask(__name__)

# Custom filter


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///amagambo.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def check_guess(word, guess):
    if len(guess) != len(word):
        return 'Invalid guess! The guess should be a word with 6 letters.'

    colors = []
    for i in range(len(word)):
        if guess[i] == word[i]:
            colors.append('greenbox')  # Character is in the right position
        elif guess[i] in word:
            colors.append('bluebox')  # Character is in the word but wrong position
        else:
            colors.append('redbox')  # Character is not in the word

    return colors

@app.route('/', methods=['GET', 'POST'])
def home():
    word = 'helloo'  # Replace with your word

    if request.method == 'POST':
        guess = request.form.getlist('guess[]')
        colors = check_guess(word, guess)
    else:
        guess = [''] * 6
        colors = [''] * 6

    return render_template('index.html', guess=guess, colors=colors)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    return None


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("email"):
            flash("Empty email")
            return redirect("/login")

        # Ensure password was submitted
        elif not request.form.get("password"):
            flash("Empty password")
            return redirect("/login")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE email = ?", request.form.get("email"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            flash("Username or password is wrong")
            return redirect("/login")

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

@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    
    if request.method == "POST":
        
        # get email
        email = request.form.get("email")
        if not email: #if email is empty
            flash("Email not provided")
            return redirect("/register")
        
        # check if email already exists
        exists = search(email)
        
        if not exists:
            flash("Email already exists")
            return redirect("/register")
        
        # get password and the password confirmation
        password = request.form.get("password")
        password_confirm = request.form.get("password_confirm")

        # meets security standards
        response = validate(password)
        if  response == True:
            if password != password_confirm:
                flash("Passwords do not match")
                return redirect("/")
            
            hash = generate_password_hash(password)
            db.execute("INSERT INTO users(email,hash,password) VALUES(?,?,?)", email,hash,password)
            rows = db.execute("SELECT id FROM users where email = ?", email)
            id = rows[0]["id"]
            session["user_id"] = id
            
            # redirect to home page
            flash("Registered")
            return redirect("/")
        
        else:
            # flash response from validate password
            flash(response)
            return redirect("/register")
           
    else:
        return render_template("register.html")


def search(email):
    """Searches if current email is in database"""
    rows = db.execute("SELECT * FROM users WHERE email = ?", email)
    #returns a boolean
    return len(rows) == 0
    
def validate(password):
    """Validates if password meets security policy"""

    #check length
    if len(password) < 8:
        return "Password has to be at least 8 characters"
    
    #check if password contains a digit
    if not any([x for x in password if x.isdigit()]):
        return "Password has to contain at least a single digit"
    
    #check for letters:
    if not any([x for x in password if x.islower() or x.isupper()]):
        return "Password has to contain at least a single letter"
    
    #passed all checks
    return True
