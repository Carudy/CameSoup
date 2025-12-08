var server_url = "https://app.imgop.dedyn.io/game/soup";

var sending_cmd = false;


send_cmd = function(data, callback) {
    console.log('Sending command to server:', data);
    fetch(server_url + '/cmd', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => callback(data))
    .catch(error => {
        console.error('Error:', error);
    })
    .finally(() => {
        sending_cmd = false;
    });
}


document.getElementById('btn_new_game').addEventListener('click', function() {
    if (sending_cmd) {
        console.log('A command is already being sent, please wait.');
        return;
    }
    sending_cmd = true;

    const data = {
        'cmd': 'new_game'
    };

    send_cmd(data, function(response) {
        console.log('Response from server:', response);
        insert_chat_row('主持人', '新游戏已开始！问题是：' + response.soup_question);
    });
});

document.getElementById('btn_end_game').addEventListener('click', function() {
    if (sending_cmd) {
        console.log('A command is already being sent, please wait.');
        return;
    }
    sending_cmd = true;

    const data = {
        'cmd': 'end_game'
    };

    send_cmd(data, function(response) {
        console.log('Response from server:', response);
        insert_chat_row('主持人', 'Game END.');
    });
});

let insert_chat_row = function(sayer, content) {
    let chat_tab = document.getElementById('chat_tab');
    let newRow = document.createElement('tr');

    let sayerCell = document.createElement('td');
    sayerCell.className = 'sayer';
    sayerCell.textContent = sayer;
    newRow.appendChild(sayerCell);

    let contentCell = document.createElement('td');
    contentCell.className = 'cont';
    contentCell.textContent = content;
    newRow.appendChild(contentCell);

    chat_tab.appendChild(newRow);

    let chatbox = document.getElementById('chatbox');
    chatbox.scrollTop = chatbox.scrollHeight;
}


document.getElementById('input_btn').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('input_btn').click();
    }
});
document.getElementById('input_box').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        document.getElementById('input_btn').click();
    }
});


document.getElementById('input_btn').addEventListener('click', function() {
    if (sending_cmd) {
        console.log('A command is already being sent, please wait.');
        return;
    }
    sending_cmd = true;

    let input_box = document.getElementById('input_box');
    const userInput = input_box.value.trim();
    if (userInput === '') {
        console.log('Empty input, ignoring.');
        return;
    }
    input_box.value = '';

    let inputType = document.getElementById('input_ask').checked ? 'ask' : 'answer';
    console.log(`Input Type: ${inputType}, User Input: ${userInput}`);

    insert_chat_row('你', userInput);
    
    const data = {
        'cmd': inputType,
        'content': userInput
    };

    send_cmd(data, function(response) {
        console.log('Response from server:', response);
        insert_chat_row('主持人', response.msg);
    });
});


setInterval(function() {
    const element = document.getElementById('thinking');
    if (element) {
        element.textContent = sending_cmd ? '🤔...' : '😊';
    }
}, 200);


document.addEventListener('DOMContentLoaded', function() {
    
});
