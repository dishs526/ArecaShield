from flask import Flask,session, flash, render_template, redirect, jsonify, request
from werkzeug.security import generate_password_hash, check_password_hash
import re
import sqlite3
import subprocess
import webbrowser
import socket
import threading
import json
import os
from datetime import datetime
from weather import WeatherService
from chatbot_logic import ArecanutChatbot  # Import your chatbot logic



# === Helper ===

app = Flask(__name__)
app.secret_key = '42ce66aa019ed0b0b0189ddd3de7819c'

weather_service = WeatherService()
chatbot = ArecanutChatbot()  # Initialize chatbot

# Function to check if a port is open (if Streamlit is running)
def is_streamlit_running(port=8501):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', port))
    sock.close()
    return result == 0
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn
def is_valid_name(name):
    return re.match(r"^[A-Za-z\s]+$", name)  # Allows letters and spaces only

def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def is_valid_password(password):
    return re.match(r"^(?=.*[A-Z])(?=.*[!@#$%^&*])[A-Za-z\d!@#$%^&*]{8,}$", password)

# === Register ===
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']
        
        if not is_valid_name(name):
           flash('❌ Name must contain letters only.', 'register')
           return redirect('/register')

        if not is_valid_email(email):
            flash('❌ Invalid email format', 'register')
            return redirect('/register')
        if not is_valid_password(password):
            flash('❌ Password must be 8+ characters with 1 uppercase & 1 special character', 'register')
            return redirect('/register')

        hashed = generate_password_hash(password)
        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO farmers (name, email, password) VALUES (?, ?, ?)", (name, email, hashed))
            conn.commit()
            flash("✅ Registered! Please login.", "success")
            return redirect('/login')
        except sqlite3.IntegrityError:
            flash("❌ Email already registered!", "register")
            return redirect('/register')
        finally:
            conn.close()

    return render_template('register.html')

# === Login ===
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute("SELECT * FROM farmers WHERE email = ?", (email,)).fetchone()
        conn.close()

        if not user:
            flash("❌ Email not found. Please register first.", "login")
            return redirect('/login')
        if not check_password_hash(user['password'], password):
            flash("❌ Wrong password. Try again.", "login")
            return redirect('/login')

        session['user_id'] = user['id']
        session['user_name'] = user['name']
        return redirect('/')  # Redirect to your homepage

    return render_template('login.html')

# === Forgot Password ===
@app.route('/forgot', methods=['GET', 'POST'])
def forgot():
    if request.method == 'POST':
        email = request.form['email']
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM farmers WHERE email = ?", (email,)).fetchone()
        conn.close()

        if not user:
            flash("❌ Email not registered.", "danger")
            return redirect('/forgot')

        session['reset_email'] = email
        return redirect('/reset')

    return render_template('forgot.html')

# === Reset Password ===
@app.route('/reset', methods=['GET', 'POST'])
def reset():
    if 'reset_email' not in session:
        return redirect('/forgot')

    if request.method == 'POST':
        new_password = request.form['password']
        if not is_valid_password(new_password):
            flash('❌ Password must meet complexity rules.', 'danger')
            return redirect('/reset')

        hashed = generate_password_hash(new_password)
        conn = get_db_connection()
        conn.execute("UPDATE farmers SET password = ? WHERE email = ?", (hashed, session['reset_email']))
        conn.commit()
        conn.close()

        session.pop('reset_email', None)
        flash("✅ Password reset successful! Please login.", "success")
        return redirect('/login')

    return render_template('reset.html')

# === Logout ===
@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect('/login')


# Route for home page
@app.route('/')
def home():
     if 'user_id' not in session:
        return redirect('/login')
     return render_template('index.html', name=session['user_name'])
 

# Route to launch streamlit app
@app.route('/arecanut-detection')
def launch_detection():
    if not is_streamlit_running():
        # Launch Streamlit app.py in background thread
        def run_streamlit():
            # Ensure 'app.py' is the correct name of your Streamlit application file
            subprocess.Popen(["streamlit", "run", "app.py"])
        threading.Thread(target=run_streamlit).start()

    # Open in new browser tab.
    # Make sure your Streamlit app is accessible at this URL when launched.
    webbrowser.open_new_tab("http://localhost:8501")
    return redirect('/')

@app.route('/weather')
def weather():
    return render_template('weather.html')

@app.route('/api/weather', methods=['POST'])
def get_weather_data():
    try:
        data = request.get_json()
        city = data.get('city', '').strip()
        state = data.get('state', '').strip()
        country = data.get('country', '').strip()

        # Validate input
        if not any([city, state, country]):
            return jsonify({'error': 'Please provide at least one location field'}), 400

        # Get weather data using the weather service
        result_data = weather_service.get_weather_data(city, state, country)
        return jsonify(result_data)

    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except ConnectionError as e:
        return jsonify({'error': str(e)}), 503
    except TimeoutError as e:
        return jsonify({'error': str(e)}), 408
    except Exception as e:
        return jsonify({'error': f'An error occurred: {str(e)}'}), 500

# Chatbot route
@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')

# API endpoint for chatbot interactions
@app.route('/api/chatbot', methods=['POST'])
def chat():
    user_message = request.json.get('message')

    if not user_message:
        # Direct English string for error message
        return jsonify({"response": "Please provide a message."}), 400

    # Call get_bot_response without the language parameter
    response = chatbot.get_bot_response(user_message)
    return jsonify({"response": response})
@app.route('/live-weather')
def live_weather():
    return render_template('locweather.html')


if __name__ == '__main__':
    app.run(debug=True)