// 主JavaScript文件

// 注册Service Worker
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/static/sw.js')
            .then(function(registration) {
                console.log('SW registered: ', registration);
            })
            .catch(function(registrationError) {
                console.log('SW registration failed: ', registrationError);
            });
    });
}

// 页面加载完成后执行
document.addEventListener('DOMContentLoaded', function() {
    // 自动隐藏提示消息
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (alert.classList.contains('show')) {
                alert.classList.remove('show');
                alert.classList.add('fade');
                setTimeout(function() {
                    alert.remove();
                }, 150);
            }
        }, 5000);
    });
    
    // 为所有表单添加提交时的加载状态
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function() {
            const submitBtn = form.querySelector('input[type="submit"], button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                const originalText = submitBtn.value || submitBtn.textContent;
                submitBtn.innerHTML = '<span class="loading"></span> 处理中...';
                
                // 如果5秒后还没有响应，恢复按钮状态
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 5000);
            }
        });
    });
});

// 工具函数：格式化时间
function formatTime(seconds) {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return minutes > 0 ? `${minutes}分${remainingSeconds}秒` : `${remainingSeconds}秒`;
}

// 工具函数：显示通知
function showNotification(message, type = 'info') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    const container = document.querySelector('.container');
    container.insertBefore(alertDiv, container.firstChild);
    
    // 自动隐藏
    setTimeout(function() {
        alertDiv.classList.remove('show');
        setTimeout(function() {
            alertDiv.remove();
        }, 150);
    }, 3000);
}

// 键盘快捷键支持
document.addEventListener('keydown', function(e) {
    // Ctrl+Enter 快速提交表单
    if (e.ctrlKey && e.key === 'Enter') {
        const form = document.querySelector('form');
        if (form) {
            form.submit();
        }
    }
    
    // ESC 键返回上一页
    if (e.key === 'Escape') {
        if (window.history.length > 1) {
            window.history.back();
        }
    }
});

// 数字输入框只允许输入数字
document.addEventListener('input', function(e) {
    if (e.target.type === 'number') {
        // 移除非数字字符（除了负号）
        e.target.value = e.target.value.replace(/[^-0-9]/g, '');
    }
});

// 页面性能监控
window.addEventListener('load', function() {
    const loadTime = performance.now();
    if (loadTime > 3000) {
        console.warn('页面加载时间较长:', loadTime + 'ms');
    }
});

// 练习页面增强功能
if (window.location.pathname === '/quiz') {
    // 自动聚焦答案输入框
    const answerInput = document.querySelector('input[name="answer"]');
    if (answerInput) {
        answerInput.focus();
        
        // 回车键提交
        answerInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                const form = answerInput.closest('form');
                if (form) {
                    form.submit();
                }
            }
        });
    }
    
    // 实时进度更新
    setInterval(updateQuizProgress, 1000);
}

function updateQuizProgress() {
    fetch('/api/quiz/progress')
        .then(response => response.json())
        .then(data => {
            if (data.error) return;
            
            // 更新时间显示
            const timeElement = document.querySelector('#quiz-time');
            if (timeElement) {
                timeElement.textContent = formatTime(data.total_time);
            }
            
            // 更新进度条
            const progressBar = document.querySelector('.progress-bar');
            if (progressBar) {
                const progress = (data.current_question / data.total_questions) * 100;
                progressBar.style.width = progress + '%';
                progressBar.setAttribute('aria-valuenow', progress);
            }
        })
        .catch(error => {
            console.error('Error updating progress:', error);
        });
}

// 音效支持
class SoundManager {
    constructor() {
        this.enabled = localStorage.getItem('soundEnabled') !== 'false';
        this.audioContext = null;
        this.initAudioContext();
    }
    
    initAudioContext() {
        try {
            this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
        } catch (e) {
            console.warn('Audio not supported');
        }
    }
    
    playCorrect() {
        if (!this.enabled || !this.audioContext) return;
        this.playTone(800, 0.1, 'sine');
    }
    
    playIncorrect() {
        if (!this.enabled || !this.audioContext) return;
        this.playTone(300, 0.2, 'sawtooth');
    }
    
    playTone(frequency, duration, type = 'sine') {
        const oscillator = this.audioContext.createOscillator();
        const gainNode = this.audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(this.audioContext.destination);
        
        oscillator.frequency.value = frequency;
        oscillator.type = type;
        
        gainNode.gain.setValueAtTime(0.3, this.audioContext.currentTime);
        gainNode.gain.exponentialRampToValueAtTime(0.01, this.audioContext.currentTime + duration);
        
        oscillator.start(this.audioContext.currentTime);
        oscillator.stop(this.audioContext.currentTime + duration);
    }
    
    toggle() {
        this.enabled = !this.enabled;
        localStorage.setItem('soundEnabled', this.enabled);
        return this.enabled;
    }
}

// 全局音效管理器
window.soundManager = new SoundManager();

// 暗色主题支持
class ThemeManager {
    constructor() {
        this.theme = localStorage.getItem('theme') || 'light';
        this.applyTheme();
    }
    
    applyTheme() {
        document.documentElement.setAttribute('data-theme', this.theme);
        const themeToggle = document.querySelector('#theme-toggle');
        if (themeToggle) {
            themeToggle.checked = this.theme === 'dark';
        }
    }
    
    toggle() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        localStorage.setItem('theme', this.theme);
        this.applyTheme();
        return this.theme;
    }
}

// 全局主题管理器
window.themeManager = new ThemeManager();

// 离线检测
window.addEventListener('online', function() {
    showNotification('网络连接已恢复', 'success');
});

window.addEventListener('offline', function() {
    showNotification('网络连接已断开，部分功能可能不可用', 'warning');
});

// 数据预加载
function preloadData() {
    // 预加载排行榜数据
    if (window.location.pathname === '/leaderboard') {
        fetch('/api/leaderboard').catch(() => {});
    }
}

// 页面可见性API
document.addEventListener('visibilitychange', function() {
    if (document.hidden) {
        // 页面隐藏时暂停计时器等
        console.log('Page hidden');
    } else {
        // 页面显示时恢复
        console.log('Page visible');
        preloadData();
    }
});