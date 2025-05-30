// 全局变量
let socket;
let sessionId = null;
let waitingForInterruptResponse = false;
let messageQueue = [];
let isProcessing = false;
let currentBotMessage = null; // 新增：当前正在构建的机器人消息元素
let activeBubbles = []; // 跟踪活跃的泡泡
let activeStars = []; // 跟踪活跃的星星
let starAnimationFrame = null; // 存储星星动画的requestAnimationFrame ID
let meteorsEnabled = false; // 禁用流星效果，防止闪烁

// DOM 元素
const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const chatMessages = document.getElementById('chat-messages');
const affirmationList = document.getElementById('affirmation-list');
const meditationList = document.getElementById('meditation-list');
const confirmModal = document.getElementById('confirm-modal');
const modalQuestion = document.getElementById('modal-question');
const confirmYesBtn = document.getElementById('confirm-yes');
const confirmNoBtn = document.getElementById('confirm-no');
const progressModal = document.getElementById('progress-modal');
const progressMessage = document.getElementById('progress-message');
const progressBar = document.getElementById('progress-bar');
const bubblesContainer = document.querySelector('.bubbles-container');

// 新增：冥想音频专用进度弹窗和进度条
const meditationProgressModal = document.getElementById('meditation-progress-modal');
const meditationProgressBar = document.getElementById('meditation-progress-bar');
const meditationProgressMessage = document.getElementById('meditation-progress-message');

// 将toggleCollapse函数设为全局可访问
window.toggleCollapse = function(titleBar) {
    const content = titleBar.nextElementSibling;
    content.classList.toggle('collapsed');
    
    const toggleIcon = titleBar.querySelector('.toggle-icon');
    if (content.classList.contains('collapsed')) {
        toggleIcon.textContent = '▶';
    } else {
        toggleIcon.textContent = '▼';
    }
};

// 初始化
document.addEventListener('DOMContentLoaded', () => {
    // 添加页面加载淡入效果
    document.body.classList.add('page-loaded');
    
    initWebSocket();
    initEventListeners();
    
    // 生成欢迎消息
    appendBotMessage('欢迎使用 I-AM 心灵伴侣！我能帮您缓解压力、提供肯定语或引导冥想。请告诉我您的需求。');
    
    // 初始化梦幻泡泡效果 - 使用较少的泡泡
    createBubbles();
    
    // 使用requestAnimationFrame更新星星效果，而不是setInterval
    updateStars();
});

// 使用requestAnimationFrame更新星星效果
function updateStars() {
    // 限制更新频率 - 每5秒才真正更新一次
    const now = Date.now();
    if (!updateStars.lastUpdate || now - updateStars.lastUpdate > 5000) {
        updateStars.lastUpdate = now;
        
        const stars = document.querySelectorAll('.star');
        stars.forEach(star => {
            // 使用CSS变量而不是直接修改样式
            const newSize = Math.random() * 3 + 1;
            const newOpacity = Math.random() * 0.5 + 0.2;
            
            star.style.setProperty('--star-size', `${newSize}px`);
            star.style.setProperty('--star-opacity', newOpacity);
        });
    }
    
    // 继续动画循环
    starAnimationFrame = requestAnimationFrame(updateStars);
}

// 创建梦幻泡泡效果 - 优化版本
function createBubbles() {
    // 清空容器和跟踪数组
    bubblesContainer.innerHTML = '';
    activeBubbles = [];
    activeStars = [];
    
    // 减少泡泡数量
    const bubbleCount = 10; // 泡泡数量减半
    
    for (let i = 0; i < bubbleCount; i++) {
        const bubble = document.createElement('div');
        bubble.classList.add('bubble');
        
        // 随机设置泡泡的大小
        const size = Math.random() * 40 + 20; // 稍微减小泡泡尺寸范围
        bubble.style.width = `${size}px`;
        bubble.style.height = `${size}px`;
        
        // 随机设置泡泡的水平位置
        const left = Math.random() * 100;
        bubble.style.left = `${left}%`;
        
        // 随机设置泡泡的透明度 - 降低整体透明度
        const opacity = Math.random() * 0.2 + 0.05; // 降低透明度
        bubble.style.opacity = opacity;
        
        // 增加动画时间，减少动画频率
        const duration = Math.random() * 30 + 20; // 增加动画时间
        bubble.style.animationDuration = `${duration}s`;
        
        // 错开动画开始时间
        const delay = Math.random() * 15;
        bubble.style.animationDelay = `${delay}s`;
        
        // 随机选择泡泡的颜色
        const colors = [
            'rgba(153, 246, 228, 0.1)', // teal - 降低透明度
            'rgba(216, 180, 254, 0.1)', // purple - 降低透明度
            'rgba(249, 168, 212, 0.1)'  // pink - 降低透明度
        ];
        const colorIndex = Math.floor(Math.random() * colors.length);
        bubble.style.background = colors[colorIndex];
        
        // 使用will-change提示浏览器这个元素会频繁动画
        bubble.style.willChange = 'transform, opacity';
        
        bubblesContainer.appendChild(bubble);
        activeBubbles.push(bubble);
    }
    
    // 添加一些星星，但数量减少
    const starCount = 15; // 减少星星数量
    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.classList.add('star');
        
        // 随机设置星星的位置
        const top = Math.random() * 100;
        const left = Math.random() * 100;
        star.style.top = `${top}%`;
        star.style.left = `${left}%`;
        
        // 随机设置星星的大小，使用CSS变量
        const size = Math.random() * 2 + 1; // 减小星星尺寸
        star.style.setProperty('--star-size', `${size}px`);
        star.style.width = `${size}px`;
        star.style.height = `${size}px`;
        
        // 增加动画周期，减少频率
        const delay = Math.random() * 5;
        star.style.animationDelay = `${delay}s`;
        
        const duration = Math.random() * 4 + 3;
        star.style.animationDuration = `${duration}s`;
        
        // 使用will-change提示
        star.style.willChange = 'transform, opacity';
        
        bubblesContainer.appendChild(star);
        activeStars.push(star);
    }
}

// 创建飘落的星星 - 修改为更少的星星
function createFallingStars() {
    // 该函数已整合到createMeteor中，不再单独调用
}

// 初始化 WebSocket 连接
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/chat`;
    
    socket = new WebSocket(wsUrl);
    
    socket.onopen = () => {
        console.log('WebSocket 连接已建立');
    };
    
    socket.onmessage = (event) => {
        const data = JSON.parse(event.data);
        handleSocketMessage(data);
    };
    
    socket.onclose = () => {
        console.log('WebSocket 连接已关闭');
        // 可以添加自动重连逻辑
        setTimeout(initWebSocket, 2000);
    };
    
    socket.onerror = (error) => {
        console.error('WebSocket 错误:', error);
    };
}

// 初始化事件监听器
function initEventListeners() {
    // 发送按钮点击事件
    sendButton.addEventListener('click', sendMessage);
    
    // 输入框回车发送
    messageInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
    
    // 确认弹窗按钮
    confirmYesBtn.addEventListener('click', () => {
        handleInterruptResponse('yes');
    });
    
    confirmNoBtn.addEventListener('click', () => {
        handleInterruptResponse('no');
    });
    
    // 初始化示例卡片点击事件
    initExampleCards();
    
    // 禁用点击页面触发流星效果，避免闪烁问题
    // 如果未来需要重新启用，取消下面的注释
    /*
    let lastMeteorTime = 0;
    document.addEventListener('click', (e) => {
        const now = Date.now();
        // 至少间隔1秒才能创建新流星
        if (meteorsEnabled && now - lastMeteorTime > 1000) {
            lastMeteorTime = now;
            createMeteor(e.clientX, e.clientY);
        }
    });
    */
    
    // 输入框效果
    const userInput = document.getElementById('user-input');
    userInput.addEventListener('focus', () => {
        userInput.classList.add('input-focus');
    });
    
    userInput.addEventListener('blur', () => {
        userInput.classList.remove('input-focus');
    });
    
    // 优化输入时的光晕效果 - 使用防抖
    let inputDebounceTimer;
    userInput.addEventListener('input', () => {
        clearTimeout(inputDebounceTimer);
        
        inputDebounceTimer = setTimeout(() => {
            if (!userInput.classList.contains('input-active') && userInput.value.trim() !== '') {
                userInput.classList.add('input-active');
                
                // 创建光晕效果，但不要在每次输入时都创建
                if (!document.querySelector('.input-glow')) {
                    createInputGlow();
                }
            } else if (userInput.value.trim() === '') {
                userInput.classList.remove('input-active');
            }
        }, 300); // 300ms延迟
    });
}

// 初始化示例卡片
function initExampleCards() {
    const example1 = document.getElementById('example-1');
    const example2 = document.getElementById('example-2');
    const examplesContainer = document.getElementById('examples-container');
    
    if (example1) {
        example1.addEventListener('click', () => {
            const exampleText = "我最近因为考试特别焦虑，马上要考试了，请生成一段有关考试的冥想音频。";
            messageInput.value = exampleText;
            messageInput.focus();
            
            // 添加点击动画
            example1.classList.add('clicked');
            setTimeout(() => example1.classList.remove('clicked'), 300);
            
            // 可选：直接发送消息
            // sendMessage();
            
            // 隐藏示例卡片
            hideExamples();
        });
    }
    
    if (example2) {
        example2.addEventListener('click', () => {
            const exampleText = "我要给喜欢的女生表白了，很紧张，请生成一段肯定语，让我有信心。";
            messageInput.value = exampleText;
            messageInput.focus();
            
            // 添加点击动画
            example2.classList.add('clicked');
            setTimeout(() => example2.classList.remove('clicked'), 300);
            
            // 可选：直接发送消息
            // sendMessage();
            
            // 隐藏示例卡片
            hideExamples();
        });
    }
}

// 隐藏示例卡片
function hideExamples() {
    const examplesContainer = document.getElementById('examples-container');
    if (examplesContainer) {
        examplesContainer.classList.add('fade-out');
        setTimeout(() => {
            examplesContainer.style.display = 'none';
        }, 500);
    }
}

// 发送消息
function sendMessage() {
    const message = messageInput.value.trim();
    if (!message) return;
    
    // 清空输入框
    messageInput.value = '';
    
    // 显示用户消息
    appendUserMessage(message);
    
    // 显示机器人正在输入指示器
    showTypingIndicator();
    
    // 结束之前未完成的消息（如果有）
    if (currentBotMessage) {
        currentBotMessage = null;
    }
    
    // 发送消息到服务器
    if (waitingForInterruptResponse) {
        // 如果在等待中断响应，使用 resume_chat
        socket.send(JSON.stringify({
            message: message,
            session_id: sessionId
        }));
        waitingForInterruptResponse = false;
    } else {
        // 普通聊天消息
        sessionId = sessionId || generateSessionId();
        socket.send(JSON.stringify({
            message: message,
            session_id: sessionId
        }));
    }
}

// 处理从服务器接收的消息
function handleSocketMessage(data) {
    removeTypingIndicator();
    console.log('[WS] 收到消息:', data);
    switch (data.type) {
        case 'message':
            updateBotMessage(data.content);
            hideProgressModal();
            hideMeditationProgressModal();
            break;
        case 'interrupt':
            currentBotMessage = null;
            handleInterrupt(data);
            break;
        case 'progress':
            if (data.stage && data.stage === '音频生成进度') {
                hideProgressModal(); // 只显示冥想弹窗
                showMeditationProgressModal(data.stage);
                if (typeof data.percent === 'number') {
                    meditationProgressBar.style.width = data.percent + '%';
                }
            } else {
                hideMeditationProgressModal(); // 只显示肯定语弹窗
                showProgressModal(data.stage);
                // 肯定语等用假进度条
            }
            break;
        case 'affirmation':
            console.log('[肯定语] 收到肯定语:', data.content);
            appendBotMessage('我已为您生成肯定语，您可以在右侧查看。');
            addAffirmation(data.content);
            hideProgressModal();
            break;
        case 'audio':
            appendBotMessage('冥想音频已生成，您可以在右侧播放。');
            addMeditationAudio(data.url);
            hideMeditationProgressModal();
            break;
        default:
            console.log('收到未知类型的消息:', data);
    }
}

// 更新机器人消息（用于流式输出）
function updateBotMessage(content) {
    // 如果没有当前正在构建的消息，创建一个新的
    if (!currentBotMessage) {
        currentBotMessage = document.createElement('div');
        currentBotMessage.classList.add('message', 'bot-message');
        chatMessages.appendChild(currentBotMessage);
    }
    
    // 添加新的内容
    const formattedContent = content
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
    
    // 更新内容
    currentBotMessage.innerHTML += formattedContent;
    
    // 滚动到底部
    scrollToBottom();
}

// 处理中断类型的消息
function handleInterrupt(data) {
    waitingForInterruptResponse = true;
    
    // 显示确认弹窗
    modalQuestion.textContent = data.question || '是否继续？';
    confirmModal.style.display = 'flex';
}

// 处理中断响应
function handleInterruptResponse(response) {
    // 隐藏确认弹窗
    confirmModal.style.display = 'none';
    
    // 如果用户同意，显示进度条
    if (response === 'yes') {
        showProgressModal('正在处理...');
        
        // 进度条动画
        startProgressAnimation();
    }
    
    // 发送响应到服务器
    socket.send(JSON.stringify({
        message: response,
        session_id: sessionId
    }));
}

// 添加用户消息到聊天区域
function appendUserMessage(message) {
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', 'user-message');
    messageElement.textContent = message;
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

// 添加机器人消息到聊天区域（用于非流式完整消息）
function appendBotMessage(message) {
    // 结束当前流式消息（如果有）
    currentBotMessage = null;
    
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', 'bot-message');
    
    // 支持简单的Markdown格式（加粗、斜体等）
    const formattedMessage = message
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
    
    messageElement.innerHTML = formattedMessage;
    chatMessages.appendChild(messageElement);
    scrollToBottom();
}

// 显示机器人正在输入指示器
function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.classList.add('typing-indicator');
    indicator.id = 'typing-indicator';
    
    for (let i = 0; i < 3; i++) {
        const dot = document.createElement('span');
        indicator.appendChild(dot);
    }
    
    chatMessages.appendChild(indicator);
    scrollToBottom();
}

// 移除正在输入指示器
function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// 添加肯定语到肯定语列表
function addAffirmation(affirmationText) {
    console.log('[肯定语] 渲染肯定语:', affirmationText);
    // 处理可能的多行肯定语
    const affirmations = affirmationText.split('\n').filter(text => text.trim());
    
    // 创建日期时间标记
    const currentDate = new Date();
    const dateString = currentDate.toLocaleDateString('zh-CN');
    const timeString = currentDate.toLocaleTimeString('zh-CN');
    
    // 创建HTML结构
    const affirmationHTML = `
        <div class="affirmation-group">
            <div class="affirmation-title-bar" onclick="toggleCollapse(this)">
                <span class="affirmation-title">肯定语 - ${dateString} ${timeString}</span>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="affirmation-content">
                ${affirmations.map(text => `<p class="affirmation-text">${text}</p>`).join('')}
            </div>
        </div>
    `;
    
    // 插入到列表顶部
    affirmationList.insertAdjacentHTML('afterbegin', affirmationHTML);
}

// 添加冥想音频到冥想列表
function addMeditationAudio(audioUrl) {
    const currentDate = new Date();
    const dateString = currentDate.toLocaleDateString('zh-CN');
    const timeString = currentDate.toLocaleTimeString('zh-CN');
    
    // 创建HTML结构
    const meditationHTML = `
        <div class="meditation-group">
            <div class="meditation-title-bar" onclick="toggleCollapse(this)">
                <span class="meditation-title">冥想 - ${dateString} ${timeString}</span>
                <span class="toggle-icon">▼</span>
            </div>
            <div class="meditation-content">
                <audio class="audio-player" controls src="${audioUrl}"></audio>
            </div>
        </div>
    `;
    
    // 插入到列表顶部
    meditationList.insertAdjacentHTML('afterbegin', meditationHTML);
}

// 显示进度弹窗
function showProgressModal(message) {
    progressMessage.textContent = message || '处理中...';
    progressModal.style.display = 'flex';
    progressBar.style.width = '0%';
}

// 隐藏进度弹窗
function hideProgressModal() {
    progressModal.style.display = 'none';
}

// 开始进度条动画
function startProgressAnimation() {
    progressBar.style.width = '0%';
    
    let width = 0;
    const interval = setInterval(() => {
        if (width >= 90) {
            clearInterval(interval);
        } else {
            width += 1;
            progressBar.style.width = width + '%';
        }
    }, 100);
}

// 滚动到底部
function scrollToBottom() {
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// 生成会话ID
function generateSessionId() {
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
        const r = Math.random() * 16 | 0;
        const v = c === 'x' ? r : (r & 0x3 | 0x8);
        return v.toString(16);
    });
}

// 创建流星效果 - 修复闪烁问题
function createMeteor(x, y) {
    // 限制同时存在的流星数量
    const existingMeteors = document.querySelectorAll('.meteor');
    if (existingMeteors.length >= 3) return; // 最多同时3个流星
    
    const meteor = document.createElement('div');
    meteor.classList.add('meteor');
    
    // 设置起始位置（点击位置）
    meteor.style.left = `${x}px`;
    meteor.style.top = `${y}px`;
    
    // 随机角度和距离
    const angle = Math.random() * 60 + 210; // 朝左下方向
    const distance = Math.random() * 150 + 50; // 减少距离，避免过大范围的闪烁
    const duration = Math.random() * 0.6 + 0.3; // 减少持续时间
    
    // 计算终点位置
    const endX = distance * Math.cos(angle * Math.PI / 180);
    const endY = distance * Math.sin(angle * Math.PI / 180);
    
    // 直接设置为CSS变量
    meteor.style.setProperty('--end-x', `${endX}px`);
    meteor.style.setProperty('--end-y', `${endY}px`);
    meteor.style.setProperty('--duration', `${duration}s`);
    
    // 添加到body中
    document.body.appendChild(meteor);
    
    // 动画结束后移除流星
    setTimeout(() => {
        meteor.remove();
    }, duration * 1000);
}

// 创建输入框光晕效果 - 优化版本
function createInputGlow() {
    // 删除现有的光晕
    const existingGlow = document.querySelector('.input-glow');
    if (existingGlow) existingGlow.remove();
    
    const inputContainer = document.querySelector('.input-container');
    const glow = document.createElement('div');
    glow.classList.add('input-glow');
    
    // 随机颜色但透明度降低
    const colors = [
        'rgba(153, 246, 228, 0.4)', // 降低透明度
        'rgba(216, 180, 254, 0.4)', // 降低透明度
        'rgba(249, 168, 212, 0.4)'  // 降低透明度
    ];
    const color = colors[Math.floor(Math.random() * colors.length)];
    
    glow.style.background = `radial-gradient(circle at center, ${color} 0%, transparent 70%)`;
    glow.style.willChange = 'opacity, transform';
    
    inputContainer.appendChild(glow);
    
    // 动画完成后移除
    setTimeout(() => {
        glow.classList.add('fade-out');
        setTimeout(() => {
            glow.remove();
        }, 500);
    }, 1500);
}

function showMeditationProgressModal(message) {
    meditationProgressMessage.textContent = message || '音频生成进度';
    if (meditationProgressModal.style.display !== 'flex') {
        meditationProgressBar.style.width = '0%';
    }
    meditationProgressModal.style.display = 'flex';
}
function hideMeditationProgressModal() {
    meditationProgressModal.style.display = 'none';
} 