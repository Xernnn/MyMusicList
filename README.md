# 🎶 My Music Review App

Welcome to **My Music Review App**! This project is a simple yet powerful web application where you can review and score your favorite songs. Whether you're a music enthusiast or just someone who loves to keep track of what you've listened to, this app has got you covered.
![Glimpse of the app](https://github.com/Xernnn/MyMusicList/blob/main/static/images/mml.png?raw=true)

## 🚀 Features

- **Music Review:** Browse through your list of songs and review them with scores ranging from 1 (Appalling) to 10 (Masterpiece).
- **Search Functionality:** Quickly find songs in your list using the search bar.
- **User Authentication:** Sign up for an account and log in to keep your reviews private.

## 📂 Project Structure

- **`app.py`:** The heart of the project, handling all the server-side logic with Flask. It manages routes for viewing songs, logging in, signing up, and modifying scores.
- **`templates/`:** 
  - **`base.html`:** The skeleton for all pages. It includes a header and defines blocks that other pages can extend.
  - **`index.html`:** The main page where you can see and manage your music reviews.
  - **`login.html`:** The login form for users to access their accounts.
  - **`signup.html`:** Where new users can create an account.
- **`static/css/style.css`:** The stylesheet that makes everything look awesome, from the dark theme to the modern card design for each song.
- **`static/js/script.js`:** Handles all the front-end magic like opening modals, saving, and deleting scores.
- **`static/data/data.xlsx`:** Your data file containing all the songs and their current scores.

## 🛠️ Getting Started

### Prerequisites

- **Python 3.x** and **pip**
- Install dependencies with:
  ```
  pip install -r requirements.txt
  ```

### Running the App
1. Clone the repo:
```
git clone https://github.com/Xernnn/MyMusicList.git
cd MyMusicList
```
2. Run the app:
```
python app.py
```
3. Access it in your browser:
```
http://127.0.0.1:5000/
```

### First-Time Setup
The first time you run the app, a SQLite database (users.db) will be created automatically to store user credentials.
