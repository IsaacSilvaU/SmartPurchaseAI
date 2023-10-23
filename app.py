import sqlite3
from flask import Flask, g, redirect, render_template, request, session, jsonify
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required
from analysisAI import detect_objects
import base64
from datetime import datetime

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Connect to the database
def dict_factory(cursor, row):
    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}

def get_db():
    db = sqlite3.connect("Data.bd")
    db.row_factory = dict_factory
    return db

@app.teardown_appcontext
def close_db(e=None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response
###

@app.route("/")
@login_required
def index():
    return render_template('index.html')

@app.route('/analyze_image', methods=['POST'])
def analyze_image():
    image_file = request.files.get('image')

    if not image_file:
        return apology("Image not captured", 500)
    
    img_path = "temp.jpg"
    image_file.save(img_path)

    detected_objects, processed_image = detect_objects(img_path)

    if isinstance(detected_objects, str):  # Verifica si detected_objects es un string
        return jsonify({"error": "No object has been detected, try again"}), 500
    
    if detected_objects is None:
        return jsonify({"error": "No object has been detected, try again"}), 500
                        
    if processed_image == False :
        return jsonify({"error": "Image not captured"}), 500
    
    with open(processed_image, "rb") as image_file:
        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

    return jsonify({
        "image": encoded_image,
        "detected_objects": detected_objects.to_dict(orient="records"),
    })

@app.route('/save_products', methods=['POST'])
def save_products():
    data = request.json

    # Verifica si hay productos para guardar en la base de datos
    if not 'products' in data:
        return apology("No products provided", 500)

    products = data['products']

    db = get_db()

    user_id = session["user_id"]

    for product in products:
        db.execute("""
            INSERT INTO purchases (user_id, product_name, price, image_path) 
            VALUES (?, ?, ?, ?)
        """, (user_id, product['name'], product['price'], "image_path_si_lo_tienes"))

    db.commit()
    return jsonify({"success": True})

@app.route("/history")
@login_required
def history():
    """Show history of purchases"""
    cur = get_db().execute(
        "SELECT product_name, price, purchase_date FROM purchases WHERE user_id = ? ORDER BY purchase_date DESC",
        (session["user_id"],)
    )
    purchases = cur.fetchall()
    
    # Agrupar compras por mes y año
    grouped_purchases = {}
    for purchase in purchases:
        key = datetime.strptime(purchase['purchase_date'], '%Y-%m-%d %H:%M:%S').strftime('%Y-%m')
        if key not in grouped_purchases:
            grouped_purchases[key] = []
        grouped_purchases[key].append(purchase)
        
    return render_template("history.html", grouped_purchases=grouped_purchases)


#### USER #####
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
        cursor = get_db().execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        )
        rows = cursor.fetchall()
        cursor.close()

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
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


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # If user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password", 400)

        # Ensure password confirmation matches
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords don't match", 400)

        # Check if the username already exists
        cursor = get_db().execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        )
        rows = cursor.fetchall()
        cursor.close()

        if len(rows) > 0:
            return apology("Username already exists", 400)

        # Hash the user's password
        hash = generate_password_hash(request.form.get("password"))

        # Insert the new user into users, storing the hash of the user's password
        query = "INSERT INTO users (username, hash) VALUES (:username, :hash)"
        values = {
            "username": request.form.get("username"),
            "hash": hash
        }

        connection = get_db()
        cursor = connection.execute(query, values)
        user_id = cursor.lastrowid

        connection.commit()

        # Ensure registration was successful
        if not user_id:
            return apology("Username already exists", 400)

        # Remember which user has logged in
        session["user_id"] = user_id

        # Redirect user to home page
        return redirect("/")
    # If user reached route via GET (as by visiting the page via a link or redirect)
    else:
        return render_template("register.html")


@app.route("/reset", methods=["GET", "POST"])
def reset_password():
    """Reset user's password"""
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide new password", 400)

        # Ensure password confirmation matches
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords don't match", 400)

        # Check if the username exists
        rows = get_db().execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )
        if len(rows) != 1:
            return apology("Username doesn't exist", 400)

        # Hash the user's new password
        hash = generate_password_hash(request.form.get("password"))

        # Update the user's password
        result = get_db().execute(
            "UPDATE users SET hash = :hash WHERE username = :username",
            username=request.form.get("username"),
            hash=hash,
        )

        # Redirect user to login page
        return redirect("/login")
    else:
        return render_template("reset.html")