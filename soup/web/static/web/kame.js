// Configuration
const CONFIG = {
    SERVER_URL: 'https://app.imgop.dedyn.io/game/soup',
    POLL_INTERVAL: 100,
    UI_UPDATE_INTERVAL: 100
};

// Application state
const state = {
    gameId: -1,
    chatFrom: 0,
    currentSoup: null,
    isSending: false
};

// DOM elements cache
const elements = {
    thinking: document.getElementById('thinking'),
    soupText: document.getElementById('current_soup'),
    chatTab: document.getElementById('chat_tab'),
    chatbox: document.getElementById('chatbox'),
    inputBox: document.getElementById('input_box'),
    inputBtn: document.getElementById('input_btn'),
    playerName: document.getElementById('player_name_input'),
    inputAsk: document.getElementById('input_ask'),
    btnNewGame: document.getElementById('btn_new_game'),
    btnEndGame: document.getElementById('btn_end_game')
};

// API communication
async function sendCommand(endpoint, data) {
    try {
        const response = await fetch(`${CONFIG.SERVER_URL}${endpoint}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        
        const result = await response.json();
        
        if (result.code !== 0) {
            addChatMessage('系统', `错误：${result.msg}`);
        }
        
        return result;
    } catch (error) {
        console.error('Network error:', error);
        // addChatMessage('系统', '网络错误，请检查连接');
        return null;
    }
}

// Chat management
function addChatMessage(speaker, content) {
    const row = document.createElement('tr');
    row.innerHTML = `
        <td class="sayer">${speaker}</td>
        <td class="cont">${content}</td>
    `;
    elements.chatTab.appendChild(row);
    elements.chatbox.scrollTop = elements.chatbox.scrollHeight;
}

function clearChat() {
    elements.chatTab.innerHTML = '';
    state.chatFrom = 0;
}

// Game commands
async function executeCommand(cmd, additionalData = {}) {
    if (state.isSending) {
        console.log('Command in progress, please wait');
        return;
    }

    const data = { cmd, ...additionalData };
    const response = await sendCommand('/cmd', data);
    
    if (response) {
        if (cmd === 'new_game') {
            state.currentSoup = response.soup_question;
        } else if (cmd === 'end_game') {
            state.currentSoup = null;
        }
    }
}

async function handleUserInput() {
    if (state.isSending) {
        console.log('Please wait for AI response');
        return;
    }

    const userInput = elements.inputBox.value.trim();
    if (!userInput) return;

    elements.inputBox.value = '';

    const inputType = elements.inputAsk.checked ? 'ask' : 'answer';
    const speaker = elements.playerName.value.trim() || '匿名玩家';

    await executeCommand(inputType, {
        content: userInput,
        speaker: speaker
    });
}

// Game state polling
async function pollGameState() {
    const data = {
        cmd: 'get_info',
        game_id: state.gameId,
        chat_id: state.chatFrom
    };

    const response = await sendCommand('/update', data);
    if (!response) {
        setTimeout(pollGameState, CONFIG.POLL_INTERVAL);
        return;
    }

    // Check if game changed
    if (state.gameId !== response.game_id) {
        clearChat();
        addChatMessage('系统', '已更新至新游戏');
    }

    // Update state
    state.gameId = response.game_id;
    state.isSending = response.ai_running;
    state.currentSoup = response.current_soup || null;

    // Add new chat messages
    if (response.new_chats?.length > 0) {
        response.new_chats.forEach(chat => {
            addChatMessage(chat.sayer, chat.content);
        });
        state.chatFrom += response.new_chats.length;
    }

    setTimeout(pollGameState, CONFIG.POLL_INTERVAL);
}

// UI updates
function updateUI() {
    if (elements.thinking) {
        elements.thinking.textContent = state.isSending ? '🤔' : '☺️';
    }
    
    elements.soupText.textContent = state.currentSoup || '当前无进行中的游戏';
}

// Event listeners
function setupEventListeners() {
    // New game button
    elements.btnNewGame.addEventListener('click', () => {
        if (state.currentSoup) {
            if (!confirm("当前有进行中的游戏，确定要开始新游戏吗？其他玩家可能还在猜哦。")) return;
        }
        executeCommand('new_game');
    });

    // End game button
    elements.btnEndGame.addEventListener('click', () => {
        if (confirm("确定要结束当前游戏吗？其他玩家可能还在猜哦。")) executeCommand('end_game');
    });

    // Send button
    elements.inputBtn.addEventListener('click', handleUserInput);

    // Enter key in input box
    elements.inputBox.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleUserInput();
        }
    });
}

// Initialize application
function init() {
    setupEventListeners();
    pollGameState();
    setInterval(updateUI, CONFIG.UI_UPDATE_INTERVAL);
}

// Start when DOM is ready
document.addEventListener('DOMContentLoaded', init);