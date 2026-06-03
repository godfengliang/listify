// Listify - Full frontend with auth, generation, and history

// ─── Init ───
document.addEventListener('DOMContentLoaded', () => {
    checkAuth();
    setupForms();
    setupTabs();
});

function setupForms() {
    document.getElementById('login-form').addEventListener('submit', handleLogin);
    document.getElementById('register-form').addEventListener('submit', handleRegister);
    document.getElementById('listing-form').addEventListener('submit', handleGenerate);
}

function setupTabs() {
    document.querySelectorAll('.tab').forEach(tab => {
        tab.addEventListener('click', () => {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            tab.classList.add('active');
            document.getElementById('tab-' + tab.dataset.platform).classList.add('active');
        });
    });
}

// ─── Auth ───
function showAuthTab(tab) {
    document.querySelectorAll('.auth-tab').forEach(t => t.classList.remove('active'));
    document.querySelectorAll('.auth-form').forEach(f => f.classList.add('hidden'));
    if (tab === 'login') {
        document.querySelectorAll('.auth-tab')[0].classList.add('active');
        document.getElementById('login-form').classList.remove('hidden');
    } else {
        document.querySelectorAll('.auth-tab')[1].classList.add('active');
        document.getElementById('register-form').classList.remove('hidden');
    }
}

async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('login-email').value;
    const password = document.getElementById('login-password').value;
    const res = await api('/api/login', 'POST', { email, password });
    if (res.ok) checkAuth();
    else alert(res.data?.detail || '登录失败');
}

async function handleRegister(e) {
    e.preventDefault();
    const name = document.getElementById('reg-name').value;
    const email = document.getElementById('reg-email').value;
    const password = document.getElementById('reg-password').value;
    const res = await api('/api/register', 'POST', { email, password, name });
    if (res.ok) checkAuth();
    else alert(res.data?.detail || '注册失败');
}

async function logout() {
    await api('/api/logout', 'POST');
    location.reload();
}

async function checkAuth() {
    const res = await api('/api/me', 'GET');
    if (res.ok) {
        const user = res.data;
        document.getElementById('auth-section').classList.add('hidden');
        document.getElementById('main-section').classList.remove('hidden');
        document.getElementById('user-info').textContent = `${user.email} (${user.plan === 'free' ? '免费版 · 剩余 ' + user.free_generations_left + ' 次' : 'Pro ♾️'})`;
        document.getElementById('generations-left').textContent =
            user.plan === 'free' ? `剩余免费次数：${user.free_generations_left}` : 'Pro 无限生成';
    } else {
        document.getElementById('auth-section').classList.remove('hidden');
        document.getElementById('main-section').classList.add('hidden');
    }
}

// ─── Generate ───
async function handleGenerate(e) {
    e.preventDefault();
    const btn = document.getElementById('generate-btn');
    const data = {
        product_name: document.getElementById('product_name').value.trim(),
        product_specs: document.getElementById('product_specs').value.trim(),
        target_audience: document.getElementById('target_audience').value.trim(),
        key_selling_points: document.getElementById('key_selling_points').value.trim(),
        language: document.getElementById('language').value,
    };

    btn.disabled = true;
    btn.textContent = '⏳ 生成中...';
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('paywall').classList.add('hidden');
    document.getElementById('history-section').classList.add('hidden');
    hideError();

    const res = await api('/api/generate', 'POST', data);

    if (res.ok) {
        renderResults(res.data);
        document.getElementById('results').classList.remove('hidden');
        // Update remaining count
        if (res.data._meta) {
            const left = res.data._meta.generations_left;
            document.getElementById('generations-left').textContent =
                res.data._meta.plan === 'free' ? `剩余免费次数：${left}` : 'Pro 无限生成';
        }
    } else if (res.status === 403) {
        document.getElementById('paywall').classList.remove('hidden');
    } else {
        showError(res.data?.detail || '生成失败');
    }

    btn.disabled = false;
    btn.textContent = '⚡ 一键生成全平台 Listing';
    document.getElementById('loading').classList.add('hidden');
}

// ─── History ───
async function showHistory() {
    const res = await api('/api/listings', 'GET');
    if (!res.ok) return;

    const section = document.getElementById('history-section');
    const list = document.getElementById('history-list');
    document.getElementById('results').classList.add('hidden');
    document.getElementById('paywall').classList.add('hidden');

    if (res.data.length === 0) {
        list.innerHTML = '<p style="color:var(--text-light)">还没有生成记录</p>';
    } else {
        list.innerHTML = res.data.map(item => `
            <div class="history-item" onclick="loadListing(${item.id})">
                <span>${item.product_name}</span>
                <span style="color:var(--text-light);font-size:12px">${item.created_at}</span>
            </div>
        `).join('');
    }
    section.classList.toggle('hidden');
}

async function loadListing(id) {
    const res = await api(`/api/listings/${id}`, 'GET');
    if (res.ok) {
        renderResults(res.data);
        document.getElementById('results').classList.remove('hidden');
        document.getElementById('history-section').classList.add('hidden');
    }
}

// ─── Upgrade ───
function upgradePlan() {
    alert('支付功能即将上线！请联系我们开通 Pro：hello@listify.ai');
}

// ─── Render ───
function renderResults(data) {
    setText('amazon-title', data.amazon?.title);
    setText('amazon-bullets', (data.amazon?.bullet_points || []).map((b, i) => `${i + 1}. ${b}`).join('\n'));
    setText('amazon-description', data.amazon?.description);
    setText('amazon-search-terms', data.amazon?.search_terms);
    setText('shopify-seo-title', data.shopify?.seo_title);
    setText('shopify-description', data.shopify?.description);
    setText('shopify-meta', data.shopify?.meta_description);
    setText('shopify-url', data.shopify?.url_handle);
    setText('temu-title', data.temu?.title);
    setText('temu-description', data.temu?.description);
    setText('temu-selling-points', (data.temu?.selling_points || []).map((s, i) => `${i + 1}. ${s}`).join('\n'));
    setText('tiktok-title', data.tiktok_shop?.title);
    setText('tiktok-description', data.tiktok_shop?.description);
    if (data.tiktok_shop?.video_script) {
        const s = data.tiktok_shop.video_script;
        setText('tiktok-script', `🎬 Hook:\n${s.hook}\n\n📹 Body:\n${s.body}\n\n📢 CTA:\n${s.cta}`);
    }
    setText('seo-keywords', (data.seo_keywords || []).join(', '));
    setText('suggested-tags', (data.suggested_tags || []).join(', '));
}

function setText(id, text) {
    const el = document.getElementById(id);
    if (el) el.textContent = text || '';
}

function copyText(id) {
    const el = document.getElementById(id);
    if (!el) return;
    navigator.clipboard.writeText(el.textContent).then(() => {
        const btn = el.parentElement.querySelector('.btn-copy');
        btn.textContent = '✅ 已复制';
        btn.classList.add('copied');
        setTimeout(() => { btn.textContent = '📋 复制'; btn.classList.remove('copied'); }, 1500);
    });
}

// ─── API helper ───
async function api(url, method = 'GET', body = null) {
    const opts = { method, headers: {} };
    if (body) {
        opts.headers['Content-Type'] = 'application/json';
        opts.body = JSON.stringify(body);
    }
    try {
        const resp = await fetch(url, opts);
        const data = await resp.json();
        return { ok: resp.ok, status: resp.status, data };
    } catch (e) {
        return { ok: false, status: 0, data: { detail: e.message } };
    }
}

function showError(msg) {
    document.getElementById('error-msg').textContent = '❌ ' + msg;
    document.getElementById('error').classList.remove('hidden');
}

function hideError() {
    document.getElementById('error').classList.add('hidden');
}
