from flask import Flask, request, jsonify, render_template, redirect, url_for, flash
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Necessary for flash messages; set to a secure random key in production

# Database connection function
def get_db_connection():
    try:
        conn = mysql.connector.connect(
            host='localhost',
            database='musicommerce_db',
            user='root',
            password=''
        )
        if conn.is_connected():
            print("Database connected successfully.")
        return conn
    except Error as e:
        print(f"Error while connecting to MySQL: {e}")
        return None

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        conn = get_db_connection()
        if conn is None:
            flash("Database connection error")
            return redirect(url_for('login'))
        
        try:
            email = request.form.get('email')
            password = request.form.get('password')

            # Validate required fields
            if not email or not password:
                flash("Both email and password are required")
                return redirect(url_for('login'))

            cursor = conn.cursor()

            # Fetch the user data
            query = "SELECT password, role FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            if user and user[0] == password:  # Compare plain text passwords directly
                role = user[1]
                if role == 'admin':
                    return redirect(url_for('admin_page'))
                elif role == 'superadmin':
                    return redirect(url_for('superadmin_page'))
                elif role == 'user':
                    return redirect(url_for('user_page'))
                else:
                    flash("Unknown role encountered")
            else:
                flash("Invalid email or password")

            return redirect(url_for('login'))
        except Error as e:
            print(f"Login error: {e}")
            flash("An internal database error occurred")
        finally:
            if conn:
                conn.close()

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        conn = get_db_connection()
        if conn is None:
            flash("Failed to connect to the database")
            return redirect(url_for('register'))

        try:
            email = request.form.get('email')
            password = request.form.get('password')
            role = 'user'  # Default role is 'user'

            # Validate required fields
            if not email or not password:
                flash("Email and password are required")
                return redirect(url_for('register'))

            cursor = conn.cursor()

            # Insert the user into the 'users' table
            query = "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)"
            cursor.execute(query, (email, password, role))
            conn.commit()
            flash("User registered successfully!")
            return redirect(url_for('login'))
        except Error as e:
            print(f"Error while inserting user data: {e}")
            flash("Failed to register user")
        finally:
            if conn:
                conn.close()

    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
