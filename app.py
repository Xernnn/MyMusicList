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
    cursor.execute('''CREATE TABLE IF NOT EXISTS reviews (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        song_title TEXT,
                        score INTEGER,
                        FOREIGN KEY(user_id) REFERENCES users(id))''')
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

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    reviewed_songs = []
    unreviewed_songs = []

    if 'logged_in' in session and 'user_id' in session:
        user_id = session['user_id']

        for song in songs:
            cursor.execute('SELECT score FROM reviews WHERE user_id = ? AND song_title = ?', (user_id, song['Title']))
            result = cursor.fetchone()

            if result:
                song['Score'] = result[0]
                reviewed_songs.append(song)
            else:
                song['Score'] = 0
                unreviewed_songs.append(song)
    else:
        for song in songs:
            song['Score'] = 0
            unreviewed_songs.append(song)

    conn.close()
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
            session['user_id'] = user[0]
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
            user = check_user(username, password)
            session['logged_in'] = True
            session['username'] = username
            session['user_id'] = user[0]
            return redirect(url_for('index'))
        else:
            return render_template('signup.html', error="Username already exists")
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/save_score', methods=['POST'])
def save_score():
    data = request.get_json()
    title = data['title']
    new_score = int(data['score'])  # Cast to integer
    user_id = session['user_id']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('SELECT id FROM reviews WHERE user_id = ? AND song_title = ?', (user_id, title))
    result = cursor.fetchone()

    if result:
        cursor.execute('UPDATE reviews SET score = ? WHERE id = ?', (new_score, result[0]))
    else:
        cursor.execute('INSERT INTO reviews (user_id, song_title, score) VALUES (?, ?, ?)', (user_id, title, new_score))

    conn.commit()
    conn.close()

    return jsonify({'success': True})

@app.route('/delete_score', methods=['POST'])
def delete_score():
    data = request.get_json()
    title = data['title']
    user_id = session['user_id']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    cursor.execute('DELETE FROM reviews WHERE user_id = ? AND song_title = ?', (user_id, title))

    conn.commit()
    conn.close()

    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)
