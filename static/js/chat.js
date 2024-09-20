document.addEventListener('DOMContentLoaded', () => {
    const messageInput = document.getElementById('message');
    messageInput.addEventListener('keydown', function(event) {
        if (event.key === 'Enter') {
            event.preventDefault();  // Отключаем стандартное поведение клавиши Enter
            sendMessage();  // Отправляем сообщение
        }
    });
});

function sendMessage() {
    const message = document.getElementById('message').value.trim();
    const fileInput = document.getElementById('file-input');
    const file = fileInput.files[0];

    if (message === '' && !file) {
        alert('Пожалуйста, введите сообщение или прикрепите файл.');
        return;
    }

    const formData = new FormData();
    formData.append('message', message);
    if (file) {
        formData.append('file', file);
    }
    formData.append('sender_login', currentUser);
    formData.append('receiver_login', selectedUser);

    fetch('/send_message', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            loadMessages();
            document.getElementById('message').value = '';  // Очищаем поле ввода
            fileInput.value = '';  // Очищаем файл
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка при отправке сообщения:', error);
    });
}

function searchUsers() {
    const query = document.getElementById('search').value.trim().toLowerCase();
    const usersDiv = document.getElementById('users');
    usersDiv.innerHTML = '';  // Очищаем список пользователей

    if (query.length < 2) {
        // Если строка поиска слишком короткая, загружаем всех пользователей
        loadUsers();
        return;
    }

    fetch('/search_users', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ query })
    })
    .then(response => response.json())
    .then(data => {
        if (data.users.length > 0) {
            data.users.forEach(user => {
                const userDiv = document.createElement('div');
                userDiv.textContent = user;
                userDiv.onclick = () => selectUser(user);  // Добавляем клик для выбора пользователя
                usersDiv.appendChild(userDiv);
            });
        } else {
            usersDiv.innerHTML = '<div>Пользователи не найдены</div>';
        }
    })
    .catch(error => {
        console.error('Ошибка поиска пользователей:', error);
    });
}

function loadUsers() {
    fetch('/get_users', { method: 'GET' })
    .then(response => response.json())
    .then(data => {
        const usersDiv = document.getElementById('users');
        usersDiv.innerHTML = '';  // Очищаем список пользователей
        data.users.forEach(user => {
            const userDiv = document.createElement('div');
            userDiv.textContent = user;
            userDiv.onclick = () => selectUser(user);  // Добавляем клик для выбора пользователя
            usersDiv.appendChild(userDiv);
        });
    })
    .catch(error => {
        console.error('Ошибка загрузки пользователей:', error);
    });
}
