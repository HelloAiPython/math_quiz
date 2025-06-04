// 主JavaScript文件

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