// Zeppelin Yayın Oyunu JavaScript

// Socket.IO bağlantısı
const socket = io();

// Game state
let gameState = {
    isRunning: false,
    players: new Map(),
    currentMultiplier: 1.0,
    gameHistory: [],
    autoPlay: false,
    viewers: 0,
    activePlayers: 0,
    recentResults: []
};

// DOM elements
const gameFeed = document.getElementById('game-feed');
const startGameBtn = document.getElementById('startGameBtn');
const autoGameBtn = document.getElementById('autoGameBtn');
const stopGameBtn = document.getElementById('stopGameBtn');
const zeppelinContainer = document.getElementById('zeppelinContainer');
const multiplierDisplay = document.getElementById('multiplierDisplay');
const recentResults = document.getElementById('recentResults');
const viewerCount = document.getElementById('viewerCount');
const activePlayerCount = document.getElementById('activePlayerCount');

// Yayın başlatma
function startBroadcast() {
    console.log('Zeppelin oyunu hazır! Test komutları:');
    console.log('- simulateFollow(): Takip simülasyonu');
    console.log('- placeBet(): Bahis simülasyonu');
    console.log('- simulateChat("!bet 100 2.5"): Chat komutu');
    
    // Başlangıç değerleri
    updateViewerCount(Math.floor(Math.random() * 50) + 10);
    updateActivePlayerCount(0);
    
    // Periyodik viewer güncellemeleri
    setInterval(() => {
        const currentViewers = parseInt(viewerCount.textContent);
        const change = Math.floor(Math.random() * 10) - 5;
        updateViewerCount(Math.max(1, currentViewers + change));
    }, 15000);
}

// Viewer sayısını güncelle
function updateViewerCount(count) {
    if (viewerCount) {
        viewerCount.textContent = count;
        gameState.viewers = count;
    }
}

// Aktif oyuncu sayısını güncelle
function updateActivePlayerCount(count) {
    if (activePlayerCount) {
        activePlayerCount.textContent = count;
        gameState.activePlayers = count;
    }
}

// Zeppelin animasyonu
function animateZeppelin(targetMultiplier, isWin) {
    const zeppelin = document.querySelector('.zeppelin');
    const flame = document.querySelector('.flame');
    const multiplierValue = document.querySelector('.multiplier-value');
    
    if (!zeppelin || !flame || !multiplierValue) return;
    
    // Uçuş animasyonu başlat
    zeppelinContainer.classList.add('flying');
    flame.style.opacity = '1';
    
    // Çarpan animasyonu
    let currentMultiplier = 1.0;
    const increment = (targetMultiplier - 1.0) / 50;
    
    const multiplierInterval = setInterval(() => {
        currentMultiplier += increment;
        multiplierValue.textContent = currentMultiplier.toFixed(2) + 'x';
        
        if (currentMultiplier >= targetMultiplier) {
            clearInterval(multiplierInterval);
            multiplierValue.textContent = targetMultiplier.toFixed(2) + 'x';
            
            // Sonuç animasyonu
            setTimeout(() => {
                if (isWin) {
                    zeppelinContainer.classList.add('flying');
                    showWinEffect();
                } else {
                    zeppelinContainer.classList.add('crashed');
                    showCrashEffect();
                }
                
                // Reset animasyonu
                setTimeout(() => {
                    resetZeppelin();
                }, 3000);
            }, 500);
        }
    }, 100);
}

// Kazanma efekti
function showWinEffect() {
    const multiplierValue = document.querySelector('.multiplier-value');
    if (multiplierValue) {
        multiplierValue.style.color = '#00ff88';
        multiplierValue.style.textShadow = '0 0 30px #00ff88, 0 0 60px #00ff88';
    }
}

// Çarpışma efekti
function showCrashEffect() {
    const multiplierValue = document.querySelector('.multiplier-value');
    if (multiplierValue) {
        multiplierValue.style.color = '#ff3366';
        multiplierValue.style.textShadow = '0 0 30px #ff3366, 0 0 60px #ff3366';
    }
}

// Zeppelin'i sıfırla
function resetZeppelin() {
    const multiplierValue = document.querySelector('.multiplier-value');
    
    zeppelinContainer.classList.remove('flying', 'crashed');
    zeppelinContainer.style.transform = '';
    
    if (multiplierValue) {
        multiplierValue.textContent = '1.00x';
        multiplierValue.style.color = '#ffd700';
        multiplierValue.style.textShadow = '0 0 20px #ffd700, 0 0 40px #ffd700, 0 0 60px #ffd700';
    }
}

// Son sonuçları güncelle
function updateRecentResults(multiplier, isWin) {
    gameState.recentResults.unshift({ multiplier, isWin });
    
    if (gameState.recentResults.length > 10) {
        gameState.recentResults.pop();
    }
    
    if (recentResults) {
        recentResults.innerHTML = '';
        gameState.recentResults.forEach(result => {
            const chip = document.createElement('div');
            chip.className = `recent-result-chip ${result.isWin ? 'win' : 'lose'}`;
            chip.textContent = result.multiplier.toFixed(2) + 'x';
            recentResults.appendChild(chip);
        });
    }
}

// Canlı feed'e mesaj ekle
function addMessage(content, type = 'info', isRaw = false) {
    if (!gameFeed) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `game-result-enhanced ${type}`;
    
    if (isRaw) {
        messageDiv.innerHTML = content;
    } else {
        messageDiv.innerHTML = `
            <div class="d-flex align-items-center">
                <i class="bi bi-info-circle me-2"></i>
                <span>${content}</span>
            </div>
        `;
    }
    
    gameFeed.insertBefore(messageDiv, gameFeed.firstChild);
    
    // Maksimum 50 mesaj tut
    while (gameFeed.children.length > 50) {
        gameFeed.removeChild(gameFeed.lastChild);
    }
    
    // Smooth scroll
    gameFeed.scrollTop = 0;
}

// Socket.IO event listeners
socket.on('connect', function() {
    console.log('Sunucuya bağlandı');
    addMessage('Sunucuya bağlanıldı', 'success');
});

socket.on('disconnect', function() {
    console.log('Sunucuyla bağlantı kesildi');
    addMessage('Sunucuyla bağlantı kesildi', 'danger');
});

// Kullanıcı kaydı
socket.on('user_registered', function(data) {
    const badgeClass = data.balance > 0 ? 'success' : 'secondary';
    addMessage(`
        <div class="d-flex align-items-center">
            <i class="bi bi-person-plus me-2"></i>
            <div>
                <strong>${data.username}</strong> oyuna katıldı!
                <br><small class="text-muted">${data.message}</small>
            </div>
            <span class="badge bg-${badgeClass} ms-auto">${data.balance} puan</span>
        </div>
    `, 'info', true);
    
    // Aktif oyuncu sayısını güncelle
    updateActivePlayerCount(gameState.activePlayers + 1);
});

// Oyun sonucu
socket.on('game_result', function(data) {
    const resultClass = data.won ? 'success' : 'danger';
    const icon = data.won ? 'bi-trophy' : 'bi-x-circle';
    const multiplierText = data.actual_multiplier.toFixed(2) + 'x';
    
    let resultHtml = `
        <div class="d-flex align-items-center mb-2">
            <i class="bi ${icon} me-2 text-${resultClass}"></i>
            <strong>${data.username}</strong>
            <span class="badge bg-secondary ms-2">${data.bet_amount} puan</span>
            <span class="badge bg-info ms-1">${data.target_multiplier}x hedef</span>
            <span class="badge bg-${resultClass} ms-auto">${multiplierText}</span>
        </div>
        <div class="small">
            ${data.message}
        </div>
    `;
    
    addMessage(resultHtml, resultClass, true);
    
    // Zeppelin animasyonu
    animateZeppelin(data.actual_multiplier, data.won);
    
    // Son sonuçlara ekle
    updateRecentResults(data.actual_multiplier, data.won);
    
    // Büyük kazanç efekti
    if (data.won && data.winnings > 1000) {
        showBigWinAnimation(data.username, data.winnings);
    }
});

// Büyük kazanç animasyonu
function showBigWinAnimation(username, winnings) {
    const overlay = document.createElement('div');
    overlay.className = 'big-win-overlay';
    overlay.innerHTML = `
        <div class="big-win-content">
            <div class="big-win-icon">🏆</div>
            <div class="big-win-text">BÜYÜK KAZANÇ!</div>
            <div class="big-win-user">${username}</div>
            <div class="big-win-amount">${winnings} puan</div>
        </div>
    `;
    
    document.body.appendChild(overlay);
    
    setTimeout(() => {
        overlay.classList.add('show');
    }, 100);
    
    setTimeout(() => {
        overlay.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(overlay);
        }, 500);
    }, 3000);
}

// Hata mesajları
socket.on('bet_error', function(data) {
    addMessage(`
        <div class="d-flex align-items-center">
            <i class="bi bi-exclamation-triangle me-2"></i>
            ${data.message}
        </div>
    `, 'warning', true);
});

socket.on('chat_error', function(data) {
    addMessage(`
        <div class="d-flex align-items-center">
            <i class="bi bi-exclamation-triangle me-2"></i>
            ${data.message}
        </div>
    `, 'warning', true);
});

// Oyun kontrolleri
if (startGameBtn) {
    startGameBtn.addEventListener('click', function() {
        if (!gameState.isRunning) {
            gameState.isRunning = true;
            startGameBtn.disabled = true;
            stopGameBtn.disabled = false;
            
            // Simülasyon oyunu başlat
            simulateGame();
        }
    });
}

if (autoGameBtn) {
    autoGameBtn.addEventListener('click', function() {
        gameState.autoPlay = !gameState.autoPlay;
        
        if (gameState.autoPlay) {
            autoGameBtn.textContent = 'Otomatik AÇIK';
            autoGameBtn.classList.remove('btn-warning');
            autoGameBtn.classList.add('btn-success');
            
            // Otomatik oyun başlat
            autoPlayInterval = setInterval(() => {
                if (!gameState.isRunning) {
                    simulateGame();
                }
            }, 8000);
        } else {
            autoGameBtn.textContent = 'Otomatik';
            autoGameBtn.classList.remove('btn-success');
            autoGameBtn.classList.add('btn-warning');
            
            if (autoPlayInterval) {
                clearInterval(autoPlayInterval);
            }
        }
    });
}

if (stopGameBtn) {
    stopGameBtn.addEventListener('click', function() {
        gameState.isRunning = false;
        startGameBtn.disabled = false;
        stopGameBtn.disabled = true;
        
        resetZeppelin();
        
        if (autoPlayInterval) {
            clearInterval(autoPlayInterval);
        }
    });
}

// Simülasyon oyunu
function simulateGame() {
    if (gameState.isRunning) return;
    
    gameState.isRunning = true;
    
    // Rastgele çarpan oluştur
    const random = Math.random();
    let multiplier;
    
    if (random < 0.65) { // %65 kaybetme şansı
        multiplier = Math.random() * 2 + 1; // 1.0 - 3.0x
    } else { // %35 kazanma şansı
        multiplier = Math.random() * 10 + 3; // 3.0 - 13.0x
    }
    
    const isWin = random >= 0.65;
    
    // Zeppelin animasyonu
    animateZeppelin(multiplier, isWin);
    
    // Son sonuçlara ekle
    updateRecentResults(multiplier, isWin);
    
    // Oyun mesajı
    addMessage(`
        <div class="d-flex align-items-center">
            <i class="bi bi-rocket-takeoff me-2"></i>
            <strong>Oyun ${isWin ? 'Kazandı' : 'Kaybetti'}</strong>
            <span class="badge bg-${isWin ? 'success' : 'danger'} ms-auto">${multiplier.toFixed(2)}x</span>
        </div>
    `, isWin ? 'success' : 'danger', true);
    
    // Oyun bitir
    setTimeout(() => {
        gameState.isRunning = false;
        startGameBtn.disabled = false;
        stopGameBtn.disabled = true;
    }, 4000);
}

// Test fonksiyonları
function simulateFollow() {
    const usernames = ['gamer123', 'proplayer', 'streamer_fan', 'zeppelin_king', 'lucky_winner'];
    const username = usernames[Math.floor(Math.random() * usernames.length)] + Math.floor(Math.random() * 1000);
    const subscriberCount = Math.floor(Math.random() * 300) + 50;
    
    socket.emit('test_follow', {
        username: username,
        subscriber_count: subscriberCount
    });
}

function placeBet() {
    const usernames = ['test_user', 'demo_player', 'beta_tester'];
    const username = usernames[Math.floor(Math.random() * usernames.length)];
    const amount = Math.floor(Math.random() * 500) + 50;
    const multiplier = (Math.random() * 10 + 1.5).toFixed(1);
    
    socket.emit('test_bet', {
        username: username,
        amount: amount,
        multiplier: parseFloat(multiplier)
    });
}

function simulateChat(message) {
    const username = 'test_user';
    socket.emit('test_chat', {
        username: username,
        message: message
    });
}

// Sayfa yüklendiğinde başlat
document.addEventListener('DOMContentLoaded', function() {
    setTimeout(startBroadcast, 1000);
});

// Global fonksiyonlar
window.simulateFollow = simulateFollow;
window.placeBet = placeBet;
window.simulateChat = simulateChat;