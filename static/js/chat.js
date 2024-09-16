let selectedUser = '';
let existingChats = [];

document.addEventListener('DOMContentLoaded', () => {
    loadUsers();
});

function loadUsers() {
    fetch('/get_users', {
        method: 'GET'
    })
    .then(response => response.json())
    .then(data => {
        const usersDiv = document.getElementById('users');
        usersDiv.innerHTML = '';
        existingChats.forEach(chat => {
            const chatDiv = document.createElement('div');
            chatDiv.textContent = chat;
            chatDiv.onclick = () => selectUser(chat);
            usersDiv.appendChild(chatDiv);
        });
        data.users.forEach(user => {
            if (user !== currentUser) {
                const userDiv = document.createElement('div');
                userDiv.textContent = user;
                userDiv.onclick = () => selectUser(user);
                usersDiv.appendChild(userDiv);
            }
        });
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

function selectUser(user) {
    selectedUser = user;
    if (!existingChats.includes(user)) {
        existingChats.unshift(user);
    }
    loadMessages();
}

function loadMessages() {
    fetch('/get_messages', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ login: currentUser, receiver_login: selectedUser })
    })
    .then(response => response.json())
    .then(data => {
        const messagesDiv = document.getElementById('messages');
        messagesDiv.innerHTML = '';
        if (data.messages) {
            data.messages.forEach(msg => {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('message');
                if (msg.sender_login === currentUser) {
                    messageDiv.classList.add('sent');
                } else {
                    messageDiv.classList.add('received');
                }
                messageDiv.textContent = `${msg.sender_login}: ${msg.message}`;
                messagesDiv.appendChild(messageDiv);
            });
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

function sendMessage() {
    const message = document.getElementById('message').value.trim();
    if (message === '' || selectedUser === '') {
        alert('Пожалуйста, выберите пользователя и введите сообщение.');
        return;
    }
    fetch('/send_message', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ sender_login: currentUser, receiver_login: selectedUser, message })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            loadMessages();
            document.getElementById('message').value = '';
        } else {
            alert(data.message);
        }
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

function searchUsers() {
    const query = document.getElementById('search').value.toLowerCase();
    const usersDiv = document.getElementById('users');
    const overlay = document.getElementById('search-overlay');

    if (query.length < 2) {
        overlay.classList.remove('active');
        usersDiv.innerHTML = '';
        existingChats.forEach(chat => {
            const chatDiv = document.createElement('div');
            chatDiv.textContent = chat;
            chatDiv.onclick = () => selectUser(chat);
            usersDiv.appendChild(chatDiv);
        });
        return;
    }

    fetch('/search_users', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ query })
    })
    .then(response => response.json())
    .then(data => {
        usersDiv.innerHTML = '';
        existingChats.forEach(chat => {
            const chatDiv = document.createElement('div');
            chatDiv.textContent = chat;
            chatDiv.onclick = () => selectUser(chat);
            usersDiv.appendChild(chatDiv);
        });
        data.users.forEach(user => {
            if (user !== currentUser && !existingChats.includes(user)) {
                const userDiv = document.createElement('div');
                userDiv.textContent = user;
                userDiv.onclick = () => selectUser(user);
                usersDiv.appendChild(userDiv);
            }
        });
        overlay.classList.add('active');
    })
    .catch(error => {
        console.error('Ошибка:', error);
    });
}

function showOverlay() {
    const overlay = document.getElementById('search-overlay');
    overlay.classList.add('active');
    setTimeout(() => {
        overlay.classList.remove('active');
    }, 1000);
}
