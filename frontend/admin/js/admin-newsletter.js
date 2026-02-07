/**
 * Newsletter subscribers management page logic.
 */

let currentStatus = '';
let currentPage = 1;

document.addEventListener('DOMContentLoaded', async () => {
    if (!(await checkAuth())) return;
    initSidebar();
    loadSubscribers();

    document.querySelectorAll('#statusTabs button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#statusTabs button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentStatus = btn.dataset.status;
            currentPage = 1;
            loadSubscribers();
        });
    });
});

async function loadSubscribers(page) {
    if (page) currentPage = page;
    const tbody = document.getElementById('subscribersTableBody');
    tbody.innerHTML = '<tr><td colspan="4"><div class="loading"><div class="spinner"></div></div></td></tr>';

    try {
        let url = `/newsletter/subscribers?page=${currentPage}&per_page=50`;
        if (currentStatus) url += `&status=${currentStatus}`;

        const data = await apiGet(url);
        if (!data) return;

        // Update summary
        document.getElementById('subscriberSummary').textContent = `${data.total} subscriber${data.total !== 1 ? 's' : ''} total`;

        if (data.subscribers.length === 0) {
            tbody.innerHTML = '<tr><td colspan="4"><div class="empty-state"><p>No subscribers found.</p></div></td></tr>';
            document.getElementById('pagination').innerHTML = '';
            return;
        }

        tbody.innerHTML = data.subscribers.map(s => `
            <tr>
                <td>${escapeHtml(s.email)}</td>
                <td><span class="badge badge-${s.active ? 'active' : 'inactive'}">${s.active ? 'Active' : 'Inactive'}</span></td>
                <td>${formatDate(s.subscribed_at)}</td>
                <td class="actions">
                    ${s.active
                        ? `<button class="btn btn-sm btn-outline" onclick="deactivateSubscriber(${s.id})">Deactivate</button>`
                        : `<button class="btn btn-sm btn-success" onclick="activateSubscriber(${s.id})">Activate</button>`
                    }
                    <button class="btn btn-sm btn-danger" onclick="removeSubscriber(${s.id})">Remove</button>
                </td>
            </tr>
        `).join('');

        renderPagination(document.getElementById('pagination'), data, loadSubscribers);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="4"><div class="empty-state"><p>Error: ${escapeHtml(err.message)}</p></div></td></tr>`;
    }
}

async function deactivateSubscriber(id) {
    try {
        await apiPatch(`/newsletter/subscribers/${id}/deactivate`);
        showToast('Subscriber deactivated');
        loadSubscribers();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function activateSubscriber(id) {
    try {
        await apiPatch(`/newsletter/subscribers/${id}/activate`);
        showToast('Subscriber activated');
        loadSubscribers();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function removeSubscriber(id) {
    if (!confirm('Remove this subscriber permanently?')) return;
    try {
        await apiDelete(`/newsletter/subscribers/${id}`);
        showToast('Subscriber removed');
        loadSubscribers();
    } catch (err) {
        showToast(err.message, 'error');
    }
}
