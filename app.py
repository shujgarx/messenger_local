from flask import Flask, render_template, request, jsonify, make_response, redirect, url_for
import sqlite3
from hashlib import sha256

app = Flask(__name__)

def connect_db():
    return sqlite3.connect('messenger.db')

def init_db():
    with connect_db() as db:
        db.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                login TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL)''')
        db.execute('''CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_login TEXT NOT NULL,
                receiver_login TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/chat')
def chat():
    login = request.cookies.get('login')
    if not login:
        return redirect(url_for('index'))
    return render_template('chat.html', login=login)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    login = data['login']
    password = data['password']
    password_hash = sha256(password.encode()).hexdigest()
    try:
        with connect_db() as db:
            db.execute('INSERT INTO users (login, password_hash) VALUES (?, ?)', (login, password_hash))
        return jsonify({"status": "success", "message": "Пользователь успешно зарегистрирован"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Логин уже существует"})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login = data['login']
    password = data['password']
    password_hash = sha256(password.encode()).hexdigest()
    with connect_db() as db:
        user = db.execute('SELECT * FROM users WHERE login = ? AND password_hash = ?', (login, password_hash)).fetchone()
        if user:
            response = make_response(jsonify({"status": "success", "message": "Вход успешен"}))
            response.set_cookie('login', login, httponly=True)
            return response
        else:
            return jsonify({"status": "error", "message": "Неверный логин или пароль"})

@app.route('/validate_cookie', methods=['POST'])
def validate_cookie():
    data = request.get_json()
    login = data.get('login')
    if not login:
        return jsonify({"status": "error", "message": "Логин не предоставлен"}), 400
    with connect_db() as db:
        user = db.execute('SELECT * FROM users WHERE login = ?', (login,)).fetchone()
        if user:
            return jsonify({"status": "success", "message": "Куки действительна"})
        else:
            return jsonify({"status": "error", "message": "Неверный логин"}), 401

@app.route('/get_users', methods=['GET'])
def get_users():
    with connect_db() as db:
        users = db.execute('SELECT login FROM users').fetchall()
    user_list = [user[0] for user in users]
    return jsonify({"users": user_list})

@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    sender_login = data['sender_login']
    receiver_login = data['receiver_login']
    message = data['message']
    with connect_db() as db:
        db.execute('INSERT INTO messages (sender_login, receiver_login, message) VALUES (?, ?, ?)',
                   (sender_login, receiver_login, message))
    return jsonify({"status": "success", "message": "Сообщение отправлено успешно"})

@app.route('/get_messages', methods=['POST'])
def get_messages():
    data = request.get_json()
    login = data['login']
    receiver_login = data['receiver_login']
    with connect_db() as db:
        messages = db.execute('''
            SELECT sender_login, message, timestamp FROM messages 
            WHERE (sender_login = ? AND receiver_login = ?) 
               OR (sender_login = ? AND receiver_login = ?) 
            ORDER BY timestamp''', 
            (login, receiver_login, receiver_login, login)).fetchall()
    formatted_messages = [{'sender_login': msg[0], 'message': msg[1], 'timestamp': msg[2]} for msg in messages]
    return jsonify({"status": "success", "messages": formatted_messages})

@app.route('/search_users', methods=['POST'])
def search_users():
    data = request.get_json()
    query = data.get('query', '').strip().lower()
    with connect_db() as db:
        users = db.execute('SELECT login FROM users WHERE LOWER(login) LIKE ?', (f'%{query}%',)).fetchall()
    user_list = [user[0] for user in users]
    return jsonify({"users": user_list})

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
