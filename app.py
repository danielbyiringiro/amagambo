from flask import Flask, flash, render_template, request, session, redirect
from flask_session import Session
from helper import *
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
    """Register user"""
    
    if request.method == "POST":

        loginPost()
           
    else:

        return render_template("signin.html")


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

        registerPost()

    else:

        return render_template("signup.html")


@app.route("/", methods=["GET", "POST"])
@login_required
def home():
    if request.method == "GET":
        
        homeGet()
    
    if request.method == "POST":

        homePost()


@app.route("/admin")
@login_required
@admin_required
def admin():
    
    details = admin_details()
    return render_template("admin.html", details = details)
