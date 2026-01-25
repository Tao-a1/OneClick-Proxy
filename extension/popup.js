const app = document.getElementById('app');
const btn = document.getElementById('toggleBtn');
const statusText = document.querySelector('.status-text');

// 初始化获取状态
chrome.runtime.sendMessage({command: "get_status"}, (response) => {
    updateUI(response.enabled);
});

// 按钮点击事件
btn.addEventListener('click', () => {
    // 根据当前样式类判断状态，更准确
    const isCurrentlyOn = app.classList.contains('mode-on'); 
    const targetState = !isCurrentlyOn;
    
    // 立即更新 UI 提供反馈（乐观更新）
    updateUI(targetState);
    
    // 发送指令给后台
    chrome.runtime.sendMessage({command: "toggle_proxy", enable: targetState}, (response) => {
        // 如果后台返回失败，可以在这里回滚 UI，但一般不需要
    });
});

function updateUI(enabled) {
    if (enabled) {
        // 切换到开启视图
        app.classList.remove('mode-off');
        app.classList.add('mode-on');
        
        statusText.innerText = "已连接安全代理";
        btn.innerText = "断开连接";
    } else {
        // 切换到关闭视图
        app.classList.remove('mode-on');
        app.classList.add('mode-off');
        
        statusText.innerText = "代理服务未开启";
        btn.innerText = "点击开启代理";
    }
}