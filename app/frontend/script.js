const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

const API_URL = 'http://127.0.0.1:8000/agent/chat';

// Historial local para mantener el contexto
let messageHistory = [];

function addMessage(text, sender, source = null, addToHistory = true) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    let content = `<div>${text}</div>`;
    if (source) {
        const sourceLabel = source === 'database_sql' ? 'Base de Datos (SQL)' : 'Conocimiento (RAG)';
        content += `<span class="source-tag">${sourceLabel}</span>`;
    }

    messageDiv.innerHTML = content;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    // Guardar en el historial
    if (addToHistory && (sender === 'user' || sender === 'ai')) {
        messageHistory.push({
            role: sender === 'user' ? 'user' : 'assistant',
            content: text
        });

        // Mantener solo los últimos 10 mensajes para no sobrecargar el prompt
        if (messageHistory.length > 10) {
            messageHistory.shift();
        }
    }
}

function showLoading() {
    const loadingDiv = document.createElement('div');
    loadingDiv.classList.add('message', 'ai', 'loading-msg');
    loadingDiv.innerHTML = `
        <div class="loading">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
    `;
    chatContainer.appendChild(loadingDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;
    return loadingDiv;
}

chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    const question = userInput.value.trim();
    if (!question) return;

    // Agregar mensaje del usuario
    addMessage(question, 'user');
    userInput.value = '';

    // Deshabilitar input
    userInput.disabled = true;
    sendBtn.disabled = true;

    // Mostrar loading
    const loadingMsg = showLoading();

    try {
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                history: messageHistory.slice(0, -1) // Enviamos el historial sin la pregunta actual que acabamos de agregar
            }),
        });

        const data = await response.json();

        // Quitar loading y agregar respuesta
        loadingMsg.remove();
        addMessage(data.answer, 'ai', data.source);

    } catch (error) {
        loadingMsg.remove();
        addMessage('Lo siento, hubo un error al conectar con el servidor. Asegúrate de que el backend esté corriendo.', 'ai');
        console.error('Error:', error);
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
});
