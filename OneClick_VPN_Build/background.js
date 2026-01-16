
// =========================================================
//  OneClick VPN - API Auth Mode (v19)
//  策略：API 登录 -> IP 白名单 -> 免密代理
// =========================================================

// 1. 服务端配置
const SERVER_HOST = "vpn.lytide.asia";
const SERVER_PORT = 8083;
const API_URL = `https://${SERVER_HOST}:${SERVER_PORT}/api/login`;

// 账号密码 (用于 API 登录)
const CREDENTIALS = {
    username: "User_3639e5",
    password: "Pwd_de2d1accd75ac23b"
};

// 2. 代理配置 (注意：不需要 authCredentials，因为服务器已经把我们 IP 白名单了)
const PROXY_CONFIG = {
    mode: "fixed_servers",
    rules: {
        singleProxy: {
            scheme: "https",
            host: SERVER_HOST,
            port: SERVER_PORT
        },
        bypassList: ["localhost", "127.0.0.1", "::1", "baidu.com", SERVER_HOST] 
    }
};

const DIRECT_CONFIG = { mode: "direct" };

// 3. 登录函数 (核心)
async function performLogin() {
    try {
        console.log("Attempting API login...");
        const response = await fetch(API_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(CREDENTIALS)
        });

        if (!response.ok) {
            throw new Error(`Server returned ${response.status}`);
        }

        const data = await response.json();
        if (data.success) {
            console.log("Login successful! IP whitelisted:", data.ip);
            return true;
        } else {
            console.error("Login failed:", data.error);
            return false;
        }
    } catch (error) {
        console.error("Network error during login:", error);
        return false;
    }
}

// 4. 开关逻辑
async function enableProxy() {
    // 设置加载中图标（可选）
    chrome.action.setBadgeText({text: "..."});
    
    // 1. 先尝试登录
    const success = await performLogin();
    
    if (success) {
        // 2. 登录成功，开启代理
        chrome.proxy.settings.set({value: PROXY_CONFIG, scope: "regular"}, () => {
            console.log("Proxy Enabled (Whitelisted)");
            chrome.storage.local.set({ enabled: true });
            updateIcon(true);
        });
        return true;
    } else {
        // 3. 登录失败，回滚
        chrome.action.setBadgeText({text: "ERR"});
        chrome.action.setBadgeBackgroundColor({color: "#F44336"});
        chrome.storage.local.set({ enabled: false });
        return false;
    }
}

function disableProxy() {
    chrome.proxy.settings.set({value: DIRECT_CONFIG, scope: "regular"}, () => {
        console.log("Proxy Disabled");
        chrome.storage.local.set({ enabled: false });
        updateIcon(false);
    });
}

// 5. 消息处理
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.command === "toggle_proxy") {
        if (message.enable) {
            // 异步操作，需要 return true 保持通道
            enableProxy().then(result => {
                sendResponse({status: result ? "success" : "error"});
            });
            return true; 
        } else {
            disableProxy();
            sendResponse({status: "success"});
        }
    } else if (message.command === "get_status") {
        chrome.storage.local.get(['enabled'], (result) => {
            sendResponse({enabled: !!result.enabled});
        });
        return true;
    }
});

function updateIcon(enabled) {
    const text = enabled ? "ON" : "OFF";
    const color = enabled ? "#4CAF50" : "#999999";
    chrome.action.setBadgeText({text: text});
    chrome.action.setBadgeBackgroundColor({color: color});
}

// 启动重置
chrome.runtime.onStartup.addListener(() => {
    disableProxy();
});
chrome.runtime.onInstalled.addListener(() => {
    disableProxy();
});
