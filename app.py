import os
import sqlite3
import time
from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your_secret_key'
UPLOAD_FOLDER = 'uploads'  # Папка для сохранения файлов
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf', 'docx'}  # Разрешенные форматы файлов

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Проверка расширения файла
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Создание или подключение к базе данных SQLite
def get_db_connection():
    conn = sqlite3.connect('database.db')  
    conn.row_factory = sqlite3.Row
    return conn

# Создание таблиц
def init_db():
    conn = get_db_connection()
    cur = conn.cursor()
    
    # Создание таблицы пользователей
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        login TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Создание таблицы сообщений
    cur.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        sender_login TEXT NOT NULL,
        receiver_login TEXT NOT NULL,
        message TEXT,
        file_path TEXT,
        timestamp INTEGER NOT NULL
    )
    ''')
    
    conn.commit()
    conn.close()


@app.route('/')
def login_page():
    return render_template('login.html')

# Маршрут для чата
@app.route('/chat')
def chat():
    if 'user' in session:
        return render_template('chat.html', login=session['user'])
    return redirect(url_for('login_page'))

# Регистрация нового пользователя
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    login = data['login']
    password = data['password']
    
    if not login or not password:
        return jsonify({'status': 'error', 'message': 'Пожалуйста, введите логин и пароль.'})

    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute('INSERT INTO users (login, password) VALUES (?, ?)', (login, password))
        conn.commit()
    except sqlite3.IntegrityError:
        return jsonify({'status': 'error', 'message': 'Пользователь уже существует.'})
    finally:
        conn.close()
    
    session['user'] = login
    return jsonify({'status': 'success', 'message': 'Успешная регистрация.'})

# Логин пользователя
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    login = data['login']
    password = data['password']
    
    if not login or not password:
        return jsonify({'status': 'error', 'message': 'Пожалуйста, введите логин и пароль.'})

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT * FROM users WHERE login = ? AND password = ?', (login, password))
    user = cur.fetchone()
    conn.close()
    
    if user:
        session['user'] = login
        return jsonify({'status': 'success', 'message': 'Вход выполнен успешно.'})
    else:
        return jsonify({'status': 'error', 'message': 'Неверные данные для входа.'})

# Вход через куки
@app.route('/validate_cookie', methods=['POST'])
def validate_cookie():
    data = request.json
    login = data['login']
    
    if 'user' in session and session['user'] == login:
        return jsonify({'status': 'success'})
    else:
        return jsonify({'status': 'error', 'message': 'Неверная куки.'})

# Поиск пользователей
@app.route('/search_users', methods=['POST'])
def search_users():
    data = request.json
    query = data['query'].lower()

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT login FROM users WHERE LOWER(login) LIKE ?', (f'%{query}%',))
    users = cur.fetchall()
    conn.close()

    return jsonify({'users': [user['login'] for user in users]})

def get_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT login FROM users')
    users = cur.fetchall()
    conn.close()

    return jsonify({'users': [user['login'] for user in users]})

# Получение сообщений
@app.route('/get_messages', methods=['POST'])
def get_messages():
    data = request.json
    login = data['login']
    receiver_login = data['receiver_login']
    
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('''SELECT * FROM messages 
                   WHERE (sender_login = ? AND receiver_login = ?) 
                   OR (sender_login = ? AND receiver_login = ?)''', 
                (login, receiver_login, receiver_login, login))
    messages = cur.fetchall()
    conn.close()
    
    return jsonify({'messages': [dict(msg) for msg in messages]})

# Отправка сообщения с прикреплением файла
@app.route('/send_message', methods=['POST'])
def send_message():
    sender_login = request.form.get('sender_login')
    receiver_login = request.form.get('receiver_login')
    message = request.form.get('message')
    
    # Обработка файла
    file = request.files.get('file')
    file_path = None
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

    # Проверка на наличие сообщения или файла
    if not message and not file_path:
        return jsonify({'status': 'error', 'message': 'Сообщение или файл должны быть прикреплены.'})
    
    # Вставка сообщения в базу данных
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('INSERT INTO messages (sender_login, receiver_login, message, file_path, timestamp) VALUES (?, ?, ?, ?, ?)', 
                (sender_login, receiver_login, message or '', file_path, int(time.time())))
    conn.commit()
    conn.close()
    
    return jsonify({'status': 'success'})


# Инициализация базы данных и запуск приложения
if __name__ == '__main__':
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Создаем папку для загрузки файлов, если она не существует
    init_db()  # Создание таблиц при первом запуске
    app.run(debug=True)
