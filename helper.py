from PIL import Image
from copy import deepcopy
from PIL import Image, ImageDraw, ImageFont
from flask import redirect, session
from functools import wraps
from cs50 import SQL

db = SQL("sqlite:///amagambo.db")

def word_day():
    return "follow"


color_dic = {"GREEN": "#528d4e", "RED":"#ea433b","YELLOW": "#b49f39",'':None}

def generate_image(board, day, score, gap_size=5, tile_gap=2):
    colorboard = deepcopy(board)
    for i in range(len(board)):
        for j in range(len(board[i])):
            colorboard[i][j] = color_dic[board[i][j]]

    new_colorboard = []
    for row in colorboard:
        if all([x is not None for x in row]):
            new_colorboard.append(row)

    colorboard = new_colorboard

    # Define the size of each color square in the image
    square_size = 30 # Adjust the size according to your requirements

    # Calculate the dimensions of the colorboard image including gaps and the title bar
    num_rows = len(colorboard)
    num_cols = len(colorboard[0])

    #gap_offset = gap_size * (num_rows - 1)  # Total gap size for each row/column
    title_bar_height = 40

    # Calculate the required image width and height to accommodate all tiles
    image_width = max(num_cols * (square_size + gap_size) - gap_size + tile_gap, square_size) + 2
    image_height = num_rows * square_size + gap_size * (num_rows - 1) + title_bar_height + 2

    # Create a new image with the calculated dimensions
    image = Image.new('RGB', (image_width, image_height), color=(0, 0, 0))  # Set background color to black

    draw = ImageDraw.Draw(image)
    title_font = ImageFont.truetype("Arial.ttf", 18)  # Use an available system font and adjust the size if needed
    #score_font = ImageFont.truetype("DejaVuSans.ttf", 14)  # Use an available system font and adjust the size if needed

    title_text = f"Amagambo {day} - {score}/7"
    title_size = get_text_dimensions(title_text, font=title_font)

    title_x = (image_width - title_size[0]) // 2
    draw.text((title_x, 10), title_text, font=title_font, fill=(255, 255, 255))

    # Iterate through the colorboard and fill in each color square in the image with gaps
    for row in range(num_rows):
        for col in range(num_cols):
            color = colorboard[row][col]
            x1 = col * (square_size + gap_size) + tile_gap
            y1 = row * (square_size + gap_size) + title_bar_height
            x2 = x1 + square_size
            y2 = y1 + square_size
            image.paste(color, (x1, y1, x2, y2))

    # Save the image to a file (e.g., PNG)
   
    image.save("static/colorboard.png", format='PNG')
    
    

def print_board(board):
    for i in board:
        print(i)

def get_text_dimensions(text_string, font):
    # https://stackoverflow.com/a/46220683/9263761
    ascent, descent = font.getmetrics()

    text_width = font.getmask(text_string).getbbox()[2]
    text_height = font.getmask(text_string).getbbox()[3] + descent

    return (text_width, text_height)

def boardDefault():
    board = [
        ['', '', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['']
    ]
    return board

def letter(attempt_val, letter_position, board, color_board):
    
    letter = board[attempt_val][letter_position]
    color = color_board[attempt_val][letter_position]

    if color == "GREEN":
        return f"<div class='letter' id='correct'>{letter}</div>"
    elif color == "YELLOW":
        return f"<div class='letter' id='almost'>{letter}</div>"
    elif color == "RED":
        return f"<div class='letter' id='error'>{letter}</div>"
    else:
        return f"<div class='letter'>{letter}</div>"


def letterDone(attempt_val, letter_position, color_board):

    board = boardDefault()
    letter = board[attempt_val][letter_position]
    color = color_board[attempt_val][letter_position]
    
    if color == "GREEN":
        return f"<div class='letter' attempt = {attempt_val} pos = {letter_position} id='correct'>{letter}</div>"
    elif color == "YELLOW":
        return f"<div class='letter' id='almost'>{letter}</div>"
    elif color == "RED":
        return f"<div class='letter' id='error'>{letter}</div>"
    else:
        return f"<div class='letter'>{letter}</div>"

    

def keyBoard():

    keyboard = {

        "key1" : ["Q","W","E","R", "T", "Y", "U", "I", "O", "P"],
        "key2" : ["A","S","D","F", "G", "H", "J", "K", "L"],
        "key3" : ["ENTER","Z","X","C","V", "B", "N", "M","DELETE"]

    }

    return keyboard

def position(board):
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == "":
                return i, j
    
    return None, None

def checkFunction(guess):
    word = word_day()
    guess = guess.lower()
    WORDS = ["purple","gentle","wisdom","follow"]

    if guess not in WORDS:
        
        message = "Word not in list"
        isWin = False

        return message, isWin
    
    colors = []
    for i in range(len(guess)):
        if guess[i] == word[i]:
            colors.append("GREEN")
        elif guess[i] != word[i] and guess[i] in word:
            colors.append("YELLOW")
        else:
            colors.append("RED")
    
    if all([x == "GREEN" for x in colors]):

        isWin = True
        message = "Congratulation you guessed the word"

        return message, isWin
    
    else:

        isWin = False

        return colors,isWin


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function

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
