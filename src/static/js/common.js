const API_BASE = "";

// SHA-256 hash a password string and return hex digest
async function hashPassword(password) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password);
    const hashBuffer = await crypto.subtle.digest("SHA-256", data);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    return hashArray.map(b => b.toString(16).padStart(2, "0")).join("");
}

// Store session token in localStorage
function getToken() {
    return localStorage.getItem("session_token") || "";
}

function setToken(token) {
    localStorage.setItem("session_token", token);
}

function clearToken() {
    localStorage.removeItem("session_token");
}

function getUsername() {
    return localStorage.getItem("username") || "";
}

function setUsername(username) {
    localStorage.setItem("username", username);
}

function clearUsername() {
    localStorage.removeItem("username");
}

// API helper - returns parsed JSON or throws
async function apiGet(endpoint, params = {}) {
    const url = new URL(API_BASE + endpoint, window.location.origin);
    if (!params.token && getToken()) params.token = getToken();
    for (const [k, v] of Object.entries(params)) {
        url.searchParams.set(k, v);
    }
    const resp = await fetch(url);
    const text = await resp.text();
    if (resp.ok) {
        try { return JSON.parse(text); }
        catch { return text; }
    }
    if (text.includes("session not found") || text.includes("invalid token")) {
        logout();
    }
    throw new Error(text);
}

// Check if user is logged in, redirect to login if not or session expired
async function requireAuth() {
    if (!getToken()) {
        window.location.href = "/static/login.html";
        return false;
    }
    try {
        const resp = await fetch(`/api/auth_check?token=${encodeURIComponent(getToken())}`);
        if (!resp.ok) {
            logout();
            return false;
        }
    } catch {
        logout();
        return false;
    }
    return true;
}

// Logout
function logout() {
    clearToken();
    clearUsername();
    window.location.href = "/static/login.html";
}

// Format currency
function formatAmount(amount) {
    return parseFloat(amount).toFixed(2);
}

// Format date
function formatDate(dateStr) {
    if (!dateStr) return "";
    return new Date(dateStr).toLocaleDateString();
}

function toISODate(dateStr) {
    if (!dateStr) return "";
    const d = new Date(dateStr);
    return d.toISOString().split("T")[0];
}

// Escape HTML
function escapeHtml(str) {
    const div = document.createElement("div");
    div.textContent = str;
    return div.innerHTML;
}
