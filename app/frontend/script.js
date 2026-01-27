const chatContainer = document.getElementById('chat-container');
const chatForm = document.getElementById('chat-form');
const userInput = document.getElementById('user-input');
const sendBtn = document.getElementById('send-btn');

const positionsTable = document.getElementById('positions-table');
const recentResults = document.getElementById('recent-results');
const tableLoader = document.getElementById('table-loader');
const resultsLoader = document.getElementById('results-loader');

const API_CHAT_URL = '/agent/chat';
const API_DASHBOARD_URL = '/api/dashboard';

// Historial local para mantener el contexto
let messageHistory = [];

// --- Funciones del Dashboard ---

async function loadDashboardData() {
    try {
        const response = await fetch(API_DASHBOARD_URL);
        const data = await response.json();

        if (data.error) throw new Error(data.error);

        renderPositions(data.top_posiciones);
        renderResults(data.ultimos_resultados);

    } catch (error) {
        console.error('Error cargando dashboard:', error);
        positionsTable.innerHTML = '<p class="error-sm">Error al cargar datos</p>';
        recentResults.innerHTML = '<p class="error-sm">Error al cargar resultados</p>';
    } finally {
        tableLoader.style.display = 'none';
        resultsLoader.style.display = 'none';
    }
}

function renderPositions(positions) {
    let html = `
        <table class="mini-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Equipo</th>
                    <th style="text-align:right">Pts</th>
                </tr>
            </thead>
            <tbody>
    `;

    positions.forEach(pos => {
        html += `
            <tr>
                <td class="pos-num">${pos.posicion}</td>
                <td>${pos.nombre}</td>
                <td class="team-pts">${pos.puntos}</td>
            </tr>
        `;
    });

    html += '</tbody></table>';
    positionsTable.innerHTML = html;
}

function renderResults(results) {
    let html = '';
    results.forEach(res => {
        html += `
            <div class="result-item">
                <span class="team-name">${res.local}</span>
                <span class="score">${res.goles_local} - ${res.goles_visita}</span>
                <span class="team-name" style="text-align:right">${res.visita}</span>
            </div>
        `;
    });
    recentResults.innerHTML = html;
}

// --- Funciones del Chat ---

function addMessage(text, sender, source = null, addToHistory = true) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('message', sender);

    let content = `<div>${text}</div>`;
    if (source) {
        let sourceLabel = 'Conocimiento (RAG)';
        if (source === 'database_sql') sourceLabel = 'Base de Datos (SQL)';
        if (source === 'mantenimiento') sourceLabel = 'Aviso del Sistema';

        content += `<span class="source-tag">${sourceLabel}</span>`;
    }

    messageDiv.innerHTML = content;
    chatContainer.appendChild(messageDiv);
    chatContainer.scrollTop = chatContainer.scrollHeight;

    if (addToHistory && (sender === 'user' || sender === 'ai')) {
        messageHistory.push({
            role: sender === 'user' ? 'user' : 'assistant',
            content: text
        });

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

    addMessage(question, 'user');
    userInput.value = '';
    userInput.disabled = true;
    sendBtn.disabled = true;

    const loadingMsg = showLoading();

    try {
        const response = await fetch(API_CHAT_URL, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                question: question,
                history: messageHistory.slice(0, -1)
            }),
        });

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(`Error ${response.status}: ${errorText}`);
        }

        const data = await response.json();
        loadingMsg.remove();
        addMessage(data.answer, 'ai', data.source);

    } catch (error) {
        loadingMsg.remove();
        console.error('Error:', error);
        addMessage(`❌ Error: ${error.message}`, 'ai');
    } finally {
        userInput.disabled = false;
        sendBtn.disabled = false;
        userInput.focus();
    }
});

// Inicializar Dashboard
document.addEventListener('DOMContentLoaded', loadDashboardData);
