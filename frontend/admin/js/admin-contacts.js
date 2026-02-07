/**
 * Contact submissions management page logic.
 */

let currentStatus = '';
let currentPage = 1;

document.addEventListener('DOMContentLoaded', async () => {
    if (!(await checkAuth())) return;
    initSidebar();
    loadContacts();

    document.querySelectorAll('#statusTabs button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#statusTabs button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentStatus = btn.dataset.status;
            currentPage = 1;
            loadContacts();
        });
    });
});

async function loadContacts(page) {
    if (page) currentPage = page;
    const tbody = document.getElementById('contactsTableBody');
    tbody.innerHTML = '<tr><td colspan="7"><div class="loading"><div class="spinner"></div></div></td></tr>';

    try {
        let url = `/contacts?page=${currentPage}&per_page=20`;
        if (currentStatus) url += `&status=${currentStatus}`;

        const data = await apiGet(url);
        if (!data) return;

        if (data.contacts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state"><p>No contact submissions found.</p></div></td></tr>';
            document.getElementById('pagination').innerHTML = '';
            return;
        }

        tbody.innerHTML = data.contacts.map(c => `
            <tr style="${!c.is_read ? 'font-weight:600' : ''}">
                <td>${escapeHtml(c.name)}</td>
                <td>${escapeHtml(c.email)}</td>
                <td>${escapeHtml(c.organization || '—')}</td>
                <td>${escapeHtml(c.topic)}</td>
                <td><span class="badge badge-${c.is_read ? 'read' : 'unread'}">${c.is_read ? 'Read' : 'Unread'}</span></td>
                <td>${formatDate(c.submitted_at)}</td>
                <td class="actions">
                    <button class="btn btn-sm btn-outline" onclick="viewContact(${c.id})">View</button>
                    ${!c.is_read
                        ? `<button class="btn btn-sm btn-success" onclick="markRead(${c.id})">Read</button>`
                        : `<button class="btn btn-sm btn-outline" onclick="markUnread(${c.id})">Unread</button>`
                    }
                    <button class="btn btn-sm btn-danger" onclick="deleteContact(${c.id})">Delete</button>
                </td>
            </tr>
        `).join('');

        renderPagination(document.getElementById('pagination'), data, loadContacts);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="7"><div class="empty-state"><p>Error: ${escapeHtml(err.message)}</p></div></td></tr>`;
    }
}

async function viewContact(id) {
    try {
        const c = await apiGet(`/contacts/${id}`);
        if (!c) return;

        document.getElementById('modalContactName').textContent = c.name;
        document.getElementById('modalContactBody').innerHTML = `
            <p><strong>Email:</strong> ${escapeHtml(c.email)}</p>
            <p><strong>Organization:</strong> ${escapeHtml(c.organization || 'N/A')}</p>
            <p><strong>Topic:</strong> ${escapeHtml(c.topic)}</p>
            <p><strong>Date:</strong> ${formatDate(c.submitted_at)}</p>
            <hr style="margin: 16px 0; border: none; border-top: 1px solid var(--border);">
            <p>${escapeHtml(c.message)}</p>
        `;
        document.getElementById('viewModal').classList.add('visible');

        // Auto-mark as read
        if (!c.is_read) {
            await apiPatch(`/contacts/${id}/read`);
            loadContacts();
        }
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function closeViewModal() {
    document.getElementById('viewModal').classList.remove('visible');
}

async function markRead(id) {
    try {
        await apiPatch(`/contacts/${id}/read`);
        showToast('Marked as read');
        loadContacts();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function markUnread(id) {
    try {
        await apiPatch(`/contacts/${id}/unread`);
        showToast('Marked as unread');
        loadContacts();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function deleteContact(id) {
    if (!confirm('Delete this contact submission permanently?')) return;
    try {
        await apiDelete(`/contacts/${id}`);
        showToast('Contact submission deleted');
        loadContacts();
    } catch (err) {
        showToast(err.message, 'error');
    }
}
