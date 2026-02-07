/**
 * Admin common utilities — auth check, API helpers, sidebar, toast messages.
 * Loaded on every admin page.
 */

const ADMIN_API = (() => {
    const base = window.location.hostname === 'localhost'
        ? 'http://localhost:8000/api/admin'
        : `${window.location.protocol}//${window.location.hostname}/api/admin`;
    return base;
})();

// ==================== AUTH ====================

async function checkAuth() {
    try {
        const res = await fetch(`${ADMIN_API}/session`, { credentials: 'include' });
        if (!res.ok) {
            window.location.href = '/admin/login.html';
            return false;
        }
        return true;
    } catch {
        window.location.href = '/admin/login.html';
        return false;
    }
}

async function logout() {
    try {
        await fetch(`${ADMIN_API}/logout`, { method: 'POST', credentials: 'include' });
    } catch { /* proceed to redirect */ }
    window.location.href = '/admin/login.html';
}

// ==================== API HELPERS ====================

async function apiGet(path) {
    const res = await fetch(`${ADMIN_API}${path}`, { credentials: 'include' });
    if (res.status === 401) {
        window.location.href = '/admin/login.html';
        return null;
    }
    if (!res.ok) throw new Error(await res.text());
    return res.json();
}

async function apiPost(path, body) {
    const res = await fetch(`${ADMIN_API}${path}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(body)
    });
    if (res.status === 401) {
        window.location.href = '/admin/login.html';
        return null;
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(err.detail || 'Request failed');
    }
    return res.json();
}

async function apiPut(path, body) {
    const res = await fetch(`${ADMIN_API}${path}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(body)
    });
    if (res.status === 401) {
        window.location.href = '/admin/login.html';
        return null;
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(err.detail || 'Request failed');
    }
    return res.json();
}

async function apiPatch(path) {
    const res = await fetch(`${ADMIN_API}${path}`, {
        method: 'PATCH',
        credentials: 'include'
    });
    if (res.status === 401) {
        window.location.href = '/admin/login.html';
        return null;
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(err.detail || 'Request failed');
    }
    return res.json();
}

async function apiDelete(path) {
    const res = await fetch(`${ADMIN_API}${path}`, {
        method: 'DELETE',
        credentials: 'include'
    });
    if (res.status === 401) {
        window.location.href = '/admin/login.html';
        return null;
    }
    if (!res.ok) {
        const err = await res.json().catch(() => ({ detail: 'Request failed' }));
        throw new Error(err.detail || 'Request failed');
    }
    return res.json();
}

// ==================== SIDEBAR ====================

function initSidebar() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.sidebar-nav a').forEach(link => {
        const href = link.getAttribute('href');
        if (href === currentPage || (currentPage === 'index.html' && href === 'index.html')) {
            link.classList.add('active');
        }
    });

    const toggle = document.querySelector('.mobile-toggle');
    const sidebar = document.querySelector('.sidebar');
    if (toggle && sidebar) {
        toggle.addEventListener('click', () => sidebar.classList.toggle('open'));
        document.addEventListener('click', (e) => {
            if (sidebar.classList.contains('open') && !sidebar.contains(e.target) && e.target !== toggle) {
                sidebar.classList.remove('open');
            }
        });
    }
}

// ==================== TOAST ====================

function showToast(message, type = 'success') {
    const existing = document.querySelector('.toast');
    if (existing) existing.remove();

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.textContent = message;
    document.body.appendChild(toast);

    requestAnimationFrame(() => toast.classList.add('visible'));
    setTimeout(() => {
        toast.classList.remove('visible');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// ==================== UTILITY ====================

function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function formatDate(isoString) {
    if (!isoString) return '—';
    const d = new Date(isoString);
    return d.toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function truncate(str, len = 80) {
    if (!str) return '';
    return str.length > len ? str.substring(0, len) + '...' : str;
}

function renderPagination(container, data, loadFn) {
    container.innerHTML = '';
    if (data.pages <= 1) return;

    const prev = document.createElement('button');
    prev.textContent = 'Prev';
    prev.disabled = data.page <= 1;
    prev.addEventListener('click', () => loadFn(data.page - 1));
    container.appendChild(prev);

    const info = document.createElement('span');
    info.className = 'page-info';
    info.textContent = `Page ${data.page} of ${data.pages}`;
    container.appendChild(info);

    const next = document.createElement('button');
    next.textContent = 'Next';
    next.disabled = data.page >= data.pages;
    next.addEventListener('click', () => loadFn(data.page + 1));
    container.appendChild(next);
}
