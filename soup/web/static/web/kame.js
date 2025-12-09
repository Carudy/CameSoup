var server_url = "https://app.imgop.dedyn.io/game/soup";

var game_id = -1;
var sending_cmd = false;
var current_soup = null;
var thinking_emoji = document.getElementById('thinking');
var soup_text = document.getElementById('current_soup');
var current_chat_id = 0;
var chat_tab = document.getElementById('chat_tab');


send_cmd = function(target, data, callback) {
    fetch(server_url + target, {
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
    });
}


document.getElementById('btn_new_game').addEventListener('click', function() {
    if (sending_cmd) {
        console.log('A command is already being sent, please wait.');
        return;
    }
    const data = {
        'cmd': 'new_game'
    };

    sending_cmd = true;
    send_cmd('/cmd', data, function(response) {
        console.log('Response from server:', response);
        current_soup = response.soup_question;
        sending_cmd = false;
    });
});

document.getElementById('btn_end_game').addEventListener('click', function() {
    if (sending_cmd) {
        console.log('A command is already being sent, please wait.');
        return;
    }
    const data = {
        'cmd': 'end_game'
    };

    sending_cmd = true;
    send_cmd('/cmd', data, function(response) {
        console.log('Response from server:', response);
        current_soup = null;
        sending_cmd = false;
    });
});

let insert_chat_row = function(sayer, content) {
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

    let user_id = document.getElementById('player_name_input').value;
    if (user_id.trim() === '') {
        user_id = '匿名玩家';
    }
    console.log(`User ID: ${user_id}`);
    const data = {
        'cmd': inputType,
        'content': userInput,
        'speaker': user_id,
    };

    send_cmd('/cmd', data, function(response) {
        console.log('Response from server:', response);
        insert_chat_row('主持人', response.msg);
        sending_cmd = false;
    });
});



get_game_state = function() {
    const data = {
        'cmd': 'get_info',
        'game_id': game_id,
        'chat_id': current_chat_id,
    };
    send_cmd('/update', data, function(res) {
        if (game_id != res.game_id) {
            current_chat_id = 0;
            chat_tab.innerHTML = '';
            insert_chat_row('系统', '已更新至新游戏。');
        }

        game_id = res.game_id;
        current_soup = res.current_soup || null;
        if (res.new_chats.length > 0) {
            res.new_chats.forEach(function(chat) {
                insert_chat_row(chat.sayer, chat.content);
            });
            current_chat_id += res.new_chats.length;
        }
        setTimeout(get_game_state, 250)
    })
}


setInterval(function() {
    if (thinking_emoji) {
        thinking_emoji.textContent = sending_cmd ? '🤔' : '😊';
    }
    soup_text.textContent = current_soup ? current_soup : '当前无进行中的游戏';
}, 200);


document.addEventListener('DOMContentLoaded', function() {
    get_game_state();
});
