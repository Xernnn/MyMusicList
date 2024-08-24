import pandas as pd
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL UNIQUE,
                        password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

# Helper function to check user credentials
def check_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

# Helper function to add a new user
def add_user(username, password):
    try:
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, password))
        conn.commit()
        conn.close()
        return True
    except sqlite3.IntegrityError:
        return False
    
@app.route('/')
def index():
    df = pd.read_excel('./static/data/data.xlsx')
    songs = df.to_dict(orient='records')

    search_query = request.args.get('search_query', '')

    if search_query:
        reviewed_songs = [song for song in songs if song['Score'] > 0 and search_query.lower() in song['Title'].lower()]
        unreviewed_songs = [song for song in songs if song['Score'] == 0 and search_query.lower() in song['Title'].lower()]
    else:
        reviewed_songs = [song for song in songs if song['Score'] > 0]
        unreviewed_songs = [song for song in songs if song['Score'] == 0]

    return render_template('index.html', reviewed_songs=reviewed_songs, unreviewed_songs=unreviewed_songs)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = check_user(username, password)
        if user:
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if add_user(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('signup.html', error="Username already exists")
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json()
    title = data['title']
    new_score = int(data['score'])  # Cast to integer

    # Load the Excel file
    df = pd.read_excel('./static/data/data.xlsx')

    # Update the score in the DataFrame
    df.loc[df['Title'] == title, 'Score'] = new_score

    # Save the updated DataFrame back to the Excel file
    df.to_excel('./static/data/data.xlsx', index=False)

    return jsonify({'success': True})

@app.route('/delete_score', methods=['POST'])
def delete_score():
    data = request.get_json()
    title = data['title']

    df = pd.read_excel('./static/data/data.xlsx')

    # Ensure the 'Score' column is treated as integers
    df['Score'] = df['Score'].astype(int)

    # Set the score back to 0
    df.loc[df['Title'] == title, 'Score'] = 0

    # Save the updated DataFrame back to the Excel file
    df.to_excel('./static/data/data.xlsx', index=False)

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)




