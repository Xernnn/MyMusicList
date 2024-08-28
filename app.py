import pandas as pd
from flask import Flask, render_template, redirect, url_for, request, session, jsonify
import sqlite3
import matplotlib
matplotlib.use('Agg')  # Use the Agg backend for rendering to a file
import matplotlib.pyplot as plt
import io
import base64

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

    search_query = request.args.get('search_query', '').lower()

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

    # Apply search filter
    if search_query:
        reviewed_songs = [song for song in reviewed_songs if search_query in song['Title'].lower()]
        unreviewed_songs = [song for song in unreviewed_songs if search_query in song['Title'].lower()]

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

@app.route('/favorites')
def favorites():
    if 'logged_in' not in session or 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    # Load songs data from file
    df = pd.read_excel('./static/data/data.xlsx')
    songs = df.to_dict(orient='records')

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    favorite_songs = []

    for song in songs:
        cursor.execute('SELECT score FROM reviews WHERE user_id = ? AND song_title = ?', (user_id, song['Title']))
        result = cursor.fetchone()

        if result and result[0] in [9, 10]:
            song['Score'] = result[0]
            favorite_songs.append(song)

    conn.close()

    return render_template('favorites.html', favorite_songs=favorite_songs)

@app.route('/stats')
def stats():
    if 'logged_in' not in session or 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Fetch all the reviews for the logged-in user
    cursor.execute('SELECT song_title, score FROM reviews WHERE user_id = ?', (user_id,))
    reviews = cursor.fetchall()
    conn.close()

    # Process data for stats
    score_distribution = [0] * 10  # Scores from 1 to 10
    for review in reviews:
        score_distribution[review[1] - 1] += 1  # Adjust index since scores are 1-based

    # Prepare the bar chart
    bar_chart = create_bar_chart(score_distribution)

    return render_template('stats.html', bar_chart=bar_chart)

def create_bar_chart(score_distribution):
    labels = [str(i+1) for i in range(10)]  # Only the score numbers
    max_reviews = max(score_distribution)  # Find the maximum number of reviews
    y_max = max_reviews + 1  # Set the y-axis limit to max reviews + 1
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, score_distribution, color='#ffa500', edgecolor='white')  # Bars with white outline
    plt.xlabel('Score', color='white')
    plt.ylabel('Number of Reviews', color='white')
    plt.xticks(color='white')
    plt.yticks(color='white')

    # Set the y-axis limit
    plt.ylim(0, y_max)

    # Customize the y-ticks to not include the highest number
    y_ticks = list(range(0, max_reviews + 1))  # Remove the highest number
    plt.yticks(y_ticks, [str(tick) for tick in y_ticks], color='white')

    plt.gca().patch.set_alpha(0)  # Set the background of the plot to be transparent
    plt.gcf().set_facecolor('none')  # Set the figure background to be transparent
    plt.gca().spines['bottom'].set_color('white')  # X-axis line color
    plt.gca().spines['left'].set_color('white')    # Y-axis line color
    plt.gca().spines['top'].set_color('white')     # Top outline color
    plt.gca().spines['right'].set_color('white')   # Right outline color
    plt.gca().spines['bottom'].set_linewidth(1.5)
    plt.gca().spines['left'].set_linewidth(1.5)
    plt.gca().spines['top'].set_linewidth(1.5)
    plt.gca().spines['right'].set_linewidth(1.5)

    # Add the number of reviews on top of each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval + 0.1, int(yval), ha='center', va='bottom', color='white', fontsize=12)

    return convert_plot_to_image()

def convert_plot_to_image():
    # Convert plot to PNG image
    img = io.BytesIO()
    plt.savefig(img, format='png', transparent=True)  # Save with transparent background
    img.seek(0)
    plt.close()
    # Encode image to base64 string
    return base64.b64encode(img.getvalue()).decode()

if __name__ == '__main__':
    app.run(debug=True)
