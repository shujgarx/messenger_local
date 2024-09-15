from flask import Flask, render_template, request, jsonify, make_response
import sqlite3
from hashlib import sha256

app = Flask(__name__)

# Подключение к базе данных
def connect_db():
    return sqlite3.connect('messenger.db')

# Создание таблиц пользователей и сообщений
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

# Главная страница — рендеринг сайта site.html
@app.route('/')
def index():
    return render_template('site.html')

# Регистрация нового пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    login = data['login']
    password = data['password']
    password_hash = sha256(password.encode()).hexdigest()

    try:
        with connect_db() as db:
            db.execute('INSERT INTO users (login, password_hash) VALUES (?, ?)', (login, password_hash))
        return jsonify({"status": "success", "message": "User registered successfully"})
    except sqlite3.IntegrityError:
        return jsonify({"status": "error", "message": "Login already exists"})

# Вход пользователя
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    login = data['login']
    password = data['password']
    password_hash = sha256(password.encode()).hexdigest()

    with connect_db() as db:
        user = db.execute('SELECT * FROM users WHERE login = ? AND password_hash = ?', (login, password_hash)).fetchone()
        if user:
            # Создание ответа с установкой куки
            response = make_response(jsonify({"status": "success", "message": "Login successful"}))
            response.set_cookie('login', login)
            return response
        else:
            return jsonify({"status": "error", "message": "Invalid login or password"})

# Получение списка пользователей
@app.route('/get_users', methods=['GET'])
def get_users():
    with connect_db() as db:
        users = db.execute('SELECT login FROM users').fetchall()
    user_list = [user[0] for user in users]
    return jsonify({"users": user_list})

# Отправка сообщения
@app.route('/send_message', methods=['POST'])
def send_message():
    data = request.get_json()
    sender_login = data['sender_login']
    receiver_login = data['receiver_login']
    message = data['message']

    with connect_db() as db:
        db.execute('INSERT INTO messages (sender_login, receiver_login, message) VALUES (?, ?, ?)',
                   (sender_login, receiver_login, message))
    return jsonify({"status": "success", "message": "Message sent successfully"})

# Получение сообщений между двумя пользователями
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

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
