// Configuração da API
const API_BASE_URL = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : window.location.origin;

// Elementos DOM
const chatMessages = document.getElementById('chat-messages');
const userInput = document.getElementById('user-input');
const sendButton = document.getElementById('send-button');
const toastContainer = document.getElementById('toast-container');
const welcomeScreen = document.getElementById('welcome-screen');

// Debug: verificar se os elementos foram encontrados
console.log('chatMessages:', chatMessages);
console.log('welcomeScreen:', welcomeScreen);

// Estado da aplicação
let conversationHistory = [];
let currentTheme = 'dark'; // Tema padrão
let currentChatId = null;
let chatHistory = []; // Array de conversas salvas
let sidebarCollapsed = false; // Estado da sidebar

// Inicialização
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    loadTheme();
});

function initializeApp() {
    // Carregar histórico de conversas do localStorage
    loadChatHistory();
    
    // Carregar estado da sidebar
    loadSidebarState();
    
    // Verificar se é a primeira vez que o usuário abre a IA
    const hasUsedBefore = localStorage.getItem('capbot-has-used');
    console.log('hasUsedBefore:', hasUsedBefore);
    
    // Sempre mostrar tela de boas-vindas se não há conversas salvas
    if (!hasUsedBefore || chatHistory.length === 0) {
        // Mostrar tela de boas-vindas
        console.log('Showing welcome screen');
        showWelcomeScreen();
    } else {
        console.log('Loading existing chat');
        // Carregar a última conversa
        loadChat(chatHistory[0].id);
    }
}

function loadSidebarState() {
    const saved = localStorage.getItem('capbot-sidebar-collapsed');
    if (saved === 'true') {
        sidebarCollapsed = true;
        const sidebar = document.querySelector('.sidebar');
        const expandBtn = document.getElementById('sidebar-expand-btn');
        sidebar.classList.add('collapsed');
        expandBtn.classList.add('show');
    }
}

function setupEventListeners() {
    // Envio de mensagem
    sendButton.addEventListener('click', sendMessage);
    userInput.addEventListener('keydown', handleKeyDown);
    
    // Auto-resize do input
    userInput.addEventListener('input', autoResizeInput);
}

function loadConversationHistory() {
    conversationHistory.forEach(msg => {
        addMessage(msg.role, msg.content, msg.sources, false);
    });
}

// Funções para gerenciar histórico de conversas
function generateChatTitle(messages) {
    // Pega a primeira mensagem do usuário para gerar o título
    const firstUserMessage = messages.find(msg => msg.role === 'user');
    if (firstUserMessage) {
        const title = firstUserMessage.content.substring(0, 50);
        return title.length < firstUserMessage.content.length ? title + '...' : title;
    }
    return 'Nova Conversa';
}

function startNewChat() {
    // Salvar a conversa atual se houver mensagens
    if (conversationHistory.length > 0) {
        saveCurrentChat();
    }
    
    // Limpar a conversa atual
    conversationHistory = [];
    currentChatId = null;
    chatMessages.innerHTML = '';
    
    // Adicionar mensagem de boas-vindas
    addMessage('assistant', "Olá! Eu sou a CapBot, uma inteligência artificial da Capgemini criada para fazer análises financeiras. Como posso ajudar você hoje?", null, false);
    
    // Atualizar a lista de conversas
    updateChatList();
}

function saveCurrentChat() {
    if (conversationHistory.length === 0) return;
    
    const chatId = currentChatId || Date.now().toString();
    const title = generateChatTitle(conversationHistory);
    const timestamp = new Date().toISOString();
    
    const chatData = {
        id: chatId,
        title: title,
        messages: [...conversationHistory],
        timestamp: timestamp
    };
    
    // Remover conversa existente se já existe
    chatHistory = chatHistory.filter(chat => chat.id !== chatId);
    
    // Adicionar nova conversa no início da lista
    chatHistory.unshift(chatData);
    
    // Manter apenas as últimas 20 conversas
    if (chatHistory.length > 20) {
        chatHistory = chatHistory.slice(0, 20);
    }
    
    // Salvar no localStorage
    localStorage.setItem('capbot-chat-history', JSON.stringify(chatHistory));
    
    currentChatId = chatId;
}

function loadChat(chatId) {
    const chat = chatHistory.find(c => c.id === chatId);
    if (!chat) return;
    
    // Salvar conversa atual se necessário
    if (conversationHistory.length > 0 && currentChatId !== chatId) {
        saveCurrentChat();
    }
    
    // Carregar a conversa selecionada
    currentChatId = chatId;
    conversationHistory = [...chat.messages];
    
    // Limpar e recarregar mensagens
    chatMessages.innerHTML = '';
    loadConversationHistory();
    
    // Atualizar a lista de conversas
    updateChatList();
}

function loadChatHistory() {
    const saved = localStorage.getItem('capbot-chat-history');
    if (saved) {
        try {
            chatHistory = JSON.parse(saved);
        } catch (error) {
            console.error('Erro ao carregar histórico de conversas:', error);
            chatHistory = [];
        }
    }
}

function updateChatList() {
    const chatList = document.getElementById('chat-list');
    chatList.innerHTML = '';
    
    chatHistory.forEach(chat => {
        const chatItem = document.createElement('div');
        chatItem.classList.add('chat-item');
        if (chat.id === currentChatId) {
            chatItem.classList.add('active');
        }
        
        const date = new Date(chat.timestamp).toLocaleDateString('pt-BR', {
            day: '2-digit',
            month: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        });
        
        chatItem.innerHTML = `
            <div class="chat-item-title">${chat.title}</div>
            <div class="chat-item-date">${date}</div>
            <div class="chat-item-actions">
                <button class="chat-delete-btn" onclick="deleteChat('${chat.id}', event)">×</button>
            </div>
        `;
        
        chatItem.addEventListener('click', (e) => {
            if (!e.target.classList.contains('chat-delete-btn')) {
                loadChat(chat.id);
            }
        });
        
        chatList.appendChild(chatItem);
    });
}

// Funções da tela de boas-vindas
function showWelcomeScreen() {
    console.log('showWelcomeScreen called');
    console.log('welcomeScreen element:', welcomeScreen);
    if (welcomeScreen) {
        welcomeScreen.style.display = 'flex';
        console.log('Welcome screen shown');
    } else {
        console.log('Welcome screen element not found');
    }
}

function hideWelcomeScreen() {
    if (welcomeScreen) {
        welcomeScreen.style.display = 'none';
    }
    // Marcar que o usuário já usou a IA
    localStorage.setItem('capbot-has-used', 'true');
}

function sendSuggestion(suggestionText) {
    // Esconder a tela de boas-vindas
    hideWelcomeScreen();
    
    // Iniciar uma nova conversa
    startNewChat();
    
    // Enviar a sugestão como mensagem
    userInput.value = suggestionText;
    sendMessage();
}

// Função para forçar a tela de boas-vindas (para debug)
function forceWelcomeScreen() {
    localStorage.removeItem('capbot-has-used');
    showWelcomeScreen();
}

// Função de teste para forçar exibição
function testWelcomeScreen() {
    console.log('Testing welcome screen...');
    const element = document.getElementById('welcome-screen');
    console.log('Element found:', element);
    if (element) {
        element.style.display = 'flex';
        console.log('Welcome screen forced to show');
    }
}

function deleteChat(chatId, event) {
    event.stopPropagation();
    
    if (confirm('Tem certeza que deseja excluir esta conversa?')) {
        chatHistory = chatHistory.filter(chat => chat.id !== chatId);
        localStorage.setItem('capbot-chat-history', JSON.stringify(chatHistory));
        
        // Se a conversa excluída era a atual, iniciar uma nova
        if (currentChatId === chatId) {
            startNewChat();
        } else {
            updateChatList();
        }
        
        showToast('Conversa excluída!', 'info');
    }
}

// Função para toggle da sidebar
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    const expandBtn = document.getElementById('sidebar-expand-btn');
    
    sidebarCollapsed = !sidebarCollapsed;
    
    if (sidebarCollapsed) {
        sidebar.classList.add('collapsed');
        expandBtn.classList.add('show');
    } else {
        sidebar.classList.remove('collapsed');
        expandBtn.classList.remove('show');
    }
    
    // Salvar preferência no localStorage
    localStorage.setItem('capbot-sidebar-collapsed', sidebarCollapsed.toString());
}

function addMessage(role, content, sources = null, save = true) {
    const messageContainer = document.createElement('div');
    messageContainer.classList.add('message-container', role);

    const avatar = document.createElement('div');
    avatar.classList.add('message-avatar');
    
    if (role === 'user') {
        avatar.textContent = 'Você';
    } else {
        // Usar imagem da Capgemini como avatar para IA
        avatar.innerHTML = '<img src="capgemini-icon.png.png" alt="CapBot" style="width: 100%; height: 100%; object-fit: contain; border-radius: 50%; display: block;">';
        
        // Debug: verificar se a imagem carregou
        const avatarImg = avatar.querySelector('img');
        if (avatarImg) {
            avatarImg.onload = () => {
                console.log('Avatar image loaded successfully');
                console.log('Image src:', avatarImg.src);
            };
            avatarImg.onerror = () => {
                console.log('Avatar image failed to load');
                console.log('Trying to load:', avatarImg.src);
                // Fallback para texto se a imagem não carregar
                avatar.innerHTML = 'CB';
            };
        }
    }

    const messageBubble = document.createElement('div');
    messageBubble.classList.add('message-bubble');
    
    // Adicionar "CapBot" no início das mensagens da IA
    if (role === 'assistant' || role === 'ai') {
        console.log('Adding CapBot header for role:', role);
        const capbotHeader = document.createElement('div');
        capbotHeader.classList.add('capbot-header');
        capbotHeader.textContent = 'CapBot';
        messageBubble.appendChild(capbotHeader);
    }
    
    const contentDiv = document.createElement('div');
    contentDiv.innerHTML = formatMessageContent(content, sources);
    messageBubble.appendChild(contentDiv);

    if (role === 'user') {
        messageContainer.appendChild(messageBubble);
        messageContainer.appendChild(avatar);
    } else {
        messageContainer.appendChild(avatar);
        messageContainer.appendChild(messageBubble);
    }

    chatMessages.appendChild(messageContainer);
    
    if (save) {
        conversationHistory.push({ role, content, sources });
        saveConversationHistory();
        
        // Salvar a conversa automaticamente após adicionar mensagem
        if (role === 'user' && conversationHistory.length > 1) {
            saveCurrentChat();
            updateChatList();
        }
    }
    
    scrollToBottom();
}

function formatMessageContent(content, sources) {
    let formattedContent = content.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>'); // Bold
    formattedContent = formattedContent.replace(/\*(.*?)\*/g, '<em>$1</em>'); // Italic

    if (sources && sources.length > 0) {
        formattedContent += '<p><strong>Fontes:</strong></p><ul>';
        sources.forEach(source => {
            formattedContent += `<li>${source}</li>`;
        });
        formattedContent += '</ul>';
    }
    return formattedContent;
}

function showLoading() {
    const loadingIndicator = document.createElement('div');
    loadingIndicator.classList.add('loading-indicator');
    loadingIndicator.id = 'loading-indicator';
    loadingIndicator.innerHTML = `
        <div class="loading-dots">
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
            <div class="loading-dot"></div>
        </div>
    `;
    chatMessages.appendChild(loadingIndicator);
    scrollToBottom();
}

function hideLoading() {
    const loadingIndicator = document.getElementById('loading-indicator');
    if (loadingIndicator) {
        loadingIndicator.remove();
    }
}

async function sendMessage() {
    const message = userInput.value.trim();
    if (message === '') return;

    // Esconder a tela de boas-vindas se estiver visível
    if (welcomeScreen && !welcomeScreen.classList.contains('hidden')) {
        hideWelcomeScreen();
    }

    addMessage('user', message);
    userInput.value = ''; // Limpa o input imediatamente
    autoResizeInput();

    showLoading();

    try {
        // Preparar dados
        const requestData = {
            message: message,
            conversation_history: conversationHistory.map(msg => ({
                role: msg.role,
                content: msg.content,
                timestamp: new Date().toISOString()
            }))
        };
        
        console.log('Enviando dados:', requestData);
        
        // Enviar para API
        const response = await fetch(`${API_BASE_URL}/chat`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        });
        
        console.log('Status da resposta:', response.status);
        
        if (!response.ok) {
            const errorText = await response.text();
            console.error('Erro da API:', errorText);
            throw new Error(`Erro HTTP: ${response.status} - ${errorText}`);
        }
        
        const data = await response.json();
        addMessage('assistant', data.message, data.sources);

    } catch (error) {
        console.error('Erro ao conectar com a API:', error);
        showToast('Erro ao conectar com a API. Verifique se o servidor está rodando.', 'error');
        addMessage('assistant', 'Desculpe, não consegui me conectar ao servidor. Por favor, tente novamente mais tarde.');
    } finally {
        hideLoading();
    }
}

function handleKeyDown(event) {
    if (event.key === 'Enter' && !event.shiftKey) {
        event.preventDefault();
        sendMessage();
    }
}

function autoResizeInput() {
    userInput.style.height = 'auto';
    userInput.style.height = Math.min(userInput.scrollHeight, 120) + 'px';
}

function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.classList.add('toast', type);
    toast.textContent = message;
    toastContainer.appendChild(toast);

    setTimeout(() => {
        toast.classList.add('show');
    }, 10);

    setTimeout(() => {
        toast.classList.remove('show');
        toast.addEventListener('transitionend', () => toast.remove());
    }, 3000);
}

function clearChat() {
    if (confirm('Tem certeza que deseja iniciar uma nova conversa? O histórico atual será perdido.')) {
        startNewChat();
        showToast('Conversa limpa!', 'info');
    }
}

function confirmClearAllChats() {
    if (confirm('Tem certeza que deseja limpar TODAS as conversas salvas? Esta ação é irreversível.')) {
        chatHistory = [];
        localStorage.removeItem('capbot-chat-history');
        startNewChat();
        showToast('Todos os chats foram limpos!', 'info');
    }
}

function downloadChat() {
    const chatData = {
        timestamp: new Date().toISOString(),
        messages: conversationHistory
    };
    const filename = `capbot_chat_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
    const jsonStr = JSON.stringify(chatData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    showToast('Conversa baixada com sucesso!', 'info');
}

function saveConversationHistory() {
    localStorage.setItem('capbot-conversation', JSON.stringify(conversationHistory));
}

// Sistema de Temas
function loadTheme() {
    const savedTheme = localStorage.getItem('capbot-theme');
    if (savedTheme) {
        currentTheme = savedTheme;
    }
    applyTheme(currentTheme);
    updateThemeSelection();
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    currentTheme = theme;
    localStorage.setItem('capbot-theme', theme);
}

function selectTheme(theme) {
    applyTheme(theme);
    updateThemeSelection();
    showToast(`Tema alterado para: ${getThemeName(theme)}`, 'info');
}

function updateThemeSelection() {
    document.querySelectorAll('.theme-option').forEach(option => {
        option.classList.remove('active');
        if (option.dataset.theme === currentTheme) {
            option.classList.add('active');
        }
    });
}

function getThemeName(theme) {
    const names = {
        'dark': 'Escuro',
        'light': 'Claro',
        'green': 'Verde',
        'red': 'Vermelho'
    };
    return names[theme] || theme;
}

// Modal de Configurações
function openSettings() {
    const modal = document.getElementById('settingsModal');
    modal.classList.add('show');
}

function closeSettings() {
    const modal = document.getElementById('settingsModal');
    modal.classList.remove('show');
}

// Fechar modal clicando fora
document.addEventListener('click', function(event) {
    const modal = document.getElementById('settingsModal');
    if (event.target === modal) {
        closeSettings();
    }
});

// Fechar modal com ESC
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        closeSettings();
    }
});