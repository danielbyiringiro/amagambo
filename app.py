from flask import Flask, flash, render_template, request, session, redirect
from flask_session import Session
from helper import *
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash
from cs50 import SQL

app = Flask(__name__)

db = SQL("sqlite:///amagambo.db")

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

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
        if not request.form.get("password"):
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
        flash("Log In")
        return render_template("register.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "GET":
        board = boardDefault()
        keyboard = keyBoard()
        color_board = boardDefault()

        return render_template("board.html", board=board, letter = letter, keyboard = keyboard, color_board = color_board)
    
    if request.method == "POST":
        selected_letter = request.form.get("selected_letter")
        board = request.form.get("board")
        color_board = request.form.get("color_board")

        board = eval(board)
        color_board = eval(color_board)

        i, j = position(board)
        
        if selected_letter == "DELETE":

            if i > 0 and j == 0:
                if color_board[i-1][5] ==  "":
                    board[i-1][5] = ""

            else:
                board[i][j-1] = ""
    
        elif selected_letter == "ENTER":

            if (i > 0 and j == 0):
                
                guess = "".join(board[i-1]) if i is not None else "".join(board[-1])
                message, response = checkFunction(guess)

                if response == True:
                    color_board[i-1] = ["GREEN"] * 6   
                    flash(message)
                    generate_image(color_board, 1, i)
                    return render_template("display.html")
                
                elif len(message) == 6:
                    
                    color_board[i-1] = [x for x in message]

                    if i == 7 and j == 0:
                        word = word_day()
                        flash(f"You ran out of guesses, today's word is {word.upper()}")
                        generate_image(color_board, 1, "X")
                        return render_template("display.html")
                    
                    else:
                    
                        return render_template("board.html", board=board, letter = letter, keyboard = keyBoard(), color_board = color_board)
            
                else:

                    flash("Word not in list")
                    return render_template("board.html", board=board, letter = letter, keyboard = keyBoard(), color_board = color_board)
    
            
            else:
                flash("Not enough letters")
                return render_template("board.html", board=board, letter = letter, keyboard = keyBoard(), color_board = color_board)

        else:
            if i > 0 and j == 0 and color_board[i-1][5] != '':
                board[i][j] = selected_letter
            elif not (i > 0 and j == 0):
                board[i][j] = selected_letter
        
        return render_template("board.html", board=board, letter = letter, keyboard = keyBoard(), color_board = color_board)


@app.route("/admin")
@login_required
@admin_required
def admin():
    
    return render_template("admin.html")