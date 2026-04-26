const API_BASE = '';

async function apiGet(path) {
    const res = await fetch(API_BASE + path);
    return res.json();
}

async function apiPost(path, data = {}) {
    const res = await fetch(API_BASE + path, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });
    return res.json();
}

function enterGame() {
    window.location.href = '/loading';
}

function startLoading() {
    const bar = document.getElementById('loadingBar');
    const text = document.getElementById('loadingText');
    const hint = document.getElementById('loadingHint');

    const hints = [
        '正在整理复习资料...',
        '正在计算平时分...',
        '正在检查精神状态...',
        '正在加载室友 AI...',
        '正在生成考试题目...',
        '正在泡图书馆...'
    ];

    let progress = 0;
    let hintIndex = 0;

    function update() {
        progress += Math.random() * 15 + 5;
        if (progress > 100) progress = 100;

        bar.style.width = progress + '%';
        text.textContent = Math.floor(progress) + '%';

        if (progress > 30 && hintIndex === 0) {
            hintIndex = 1;
            hint.textContent = hints[1];
        } else if (progress > 50 && hintIndex === 1) {
            hintIndex = 2;
            hint.textContent = hints[2];
        } else if (progress > 70 && hintIndex === 2) {
            hintIndex = 3;
            hint.textContent = hints[3];
        } else if (progress > 85 && hintIndex === 3) {
            hintIndex = 4;
            hint.textContent = hints[4];
        }

        if (progress >= 100) {
            hint.textContent = '准备就绪！';
            setTimeout(() => {
                startGameAndRedirect();
            }, 500);
        } else {
            setTimeout(update, 200 + Math.random() * 300);
        }
    }

    update();
}

async function startGameAndRedirect() {
    await apiPost('/api/start');
    window.location.href = '/main';
}

async function initMainPage() {
    const state = await apiGet('/api/state');
    if (state.game_over) {
        window.location.href = '/ending';
        return;
    }

    updateMainPage(state);
}

function updateMainPage(state) {
    const phaseNames = {
        'warmup': '期末预热',
        'sprint': '期末冲刺',
        'exam': '期末考试'
    };

    const phaseBadge = document.getElementById('phaseBadge');
    const dayNum = document.getElementById('dayNum');

    if (phaseBadge) phaseBadge.textContent = phaseNames[state.phase] || state.phase;
    if (dayNum) dayNum.textContent = state.day;

    if (state.stats_unlocked) {
        const statsPanel = document.getElementById('statsPanel');
        if (statsPanel) {
            statsPanel.classList.remove('hidden');
            statsPanel.classList.add('show');
        }

        updateStatBar('mental', state.mental, '#e8a0bf');
        updateStatBar('energy', state.energy, '#a0c4e8');
        updateStatBar('review', state.review, '#b8e0a0');
        updateStatBar('score', state.score, '#f0d0a0');
    }

    document.querySelectorAll('.time-btn').forEach(btn => {
        btn.classList.remove('active');
    });
}

function updateStatBar(name, value, color) {
    const bar = document.getElementById(name + 'Bar');
    const val = document.getElementById(name + 'Value');
    if (bar) {
        bar.style.width = value + '%';
        bar.style.background = color;
    }
    if (val) val.textContent = value;
}

async function selectTime(timeSlot) {
    const state = await apiGet('/api/state');
    if (state.game_over) {
        window.location.href = '/ending';
        return;
    }

    if (state.time_slot !== timeSlot) {
        return;
    }

    window.location.href = '/event';
}

function backToMain() {
    window.location.href = '/main';
}

async function initEventPage() {
    const event = await apiGet('/api/event');
    if (event.error) {
        window.location.href = '/main';
        return;
    }

    const timeNames = {
        'morning': '早晨',
        'noon': '中午',
        'afternoon': '傍晚',
        'evening': '深夜'
    };

    const state = await apiGet('/api/state');

    const timeBadge = document.getElementById('eventTimeBadge');
    if (timeBadge) timeBadge.textContent = timeNames[state.time_slot] || state.time_slot;

    const title = document.getElementById('eventTitle');
    const story = document.getElementById('eventStory');
    const choices = document.getElementById('eventChoices');

    if (title) title.textContent = event.title || '事件';
    if (story) story.textContent = event.story || '';

    if (choices) {
        choices.innerHTML = '';
        event.choices.forEach((choice, idx) => {
            const btn = document.createElement('button');
            btn.className = 'choice-btn';
            btn.innerHTML = `
                <span class="choice-text">${choice.text}</span>
                <span class="choice-desc">${choice.desc || ''}</span>
            `;
            btn.onclick = () => makeChoice(idx);
            choices.appendChild(btn);
        });
    }
}

async function makeChoice(choiceIdx) {
    const result = await apiPost('/api/choice', { choice_idx: choiceIdx });

    if (result.error) {
        alert(result.error);
        return;
    }

    if (result.game_over) {
        window.location.href = '/ending';
        return;
    }

    window.location.href = '/main';
}

async function initEndingPage() {
    const ending = await apiGet('/api/ending');
    const state = await apiGet('/api/state');

    if (ending.error) {
        window.location.href = '/main';
        return;
    }

    const title = document.getElementById('endingTitle');
    const desc = document.getElementById('endingDesc');

    if (title) title.textContent = ending.name || '未知结局';
    if (desc) desc.textContent = ending.desc || '';

    const icons = {
        'god': '👑',
        'lucky': '🍀',
        'normal': '🎓',
        'makeup': '📖',
        'dropout': '⚠️',
        'hospital': '🏥'
    };

    const icon = document.getElementById('endingIcon');
    if (icon) icon.textContent = icons[ending.key] || '🎓';

    const endReview = document.getElementById('endReview');
    const endMental = document.getElementById('endMental');
    const endEnergy = document.getElementById('endEnergy');
    const endScore = document.getElementById('endScore');

    if (endReview) endReview.textContent = state.review;
    if (endMental) endMental.textContent = state.mental;
    if (endEnergy) endEnergy.textContent = state.energy;
    if (endScore) endScore.textContent = state.score;
}

async function restartGame() {
    await apiPost('/api/start');
    window.location.href = '/';
}
