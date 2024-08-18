import pandas as pd
from flask import Flask, render_template, redirect, url_for, request, session, jsonify

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

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

    if 'logged_in' in session:
        return render_template('index.html', reviewed_songs=reviewed_songs, unreviewed_songs=unreviewed_songs)
    else:
        return render_template('index.html', reviewed_songs=reviewed_songs, unreviewed_songs=unreviewed_songs)

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    return redirect(url_for('index'))

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




