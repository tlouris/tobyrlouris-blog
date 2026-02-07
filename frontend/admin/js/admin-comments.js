/**
 * Comment moderation page logic.
 */

let currentStatus = '';
let currentPage = 1;

document.addEventListener('DOMContentLoaded', async () => {
    if (!(await checkAuth())) return;
    initSidebar();
    loadComments();

    document.querySelectorAll('#statusTabs button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#statusTabs button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentStatus = btn.dataset.status;
            currentPage = 1;
            loadComments();
        });
    });
});

async function loadComments(page) {
    if (page) currentPage = page;
    const tbody = document.getElementById('commentsTableBody');
    tbody.innerHTML = '<tr><td colspan="6"><div class="loading"><div class="spinner"></div></div></td></tr>';

    try {
        let url = `/comments?page=${currentPage}&per_page=20`;
        if (currentStatus) url += `&status=${currentStatus}`;

        const data = await apiGet(url);
        if (!data) return;

        if (data.comments.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><p>No comments found.</p></div></td></tr>';
            document.getElementById('pagination').innerHTML = '';
            return;
        }

        tbody.innerHTML = data.comments.map(c => `
            <tr>
                <td><strong>${escapeHtml(c.author)}</strong><br><small style="color:var(--text-muted)">${escapeHtml(c.email)}</small></td>
                <td>${escapeHtml(c.post_id)}</td>
                <td class="truncate">${escapeHtml(c.content)}</td>
                <td><span class="badge badge-${c.approved ? 'approved' : 'pending'}">${c.approved ? 'Approved' : 'Pending'}</span></td>
                <td>${formatDate(c.created_at)}</td>
                <td class="actions">
                    ${!c.approved
                        ? `<button class="btn btn-sm btn-success" onclick="approveComment(${c.id})">Approve</button>`
                        : `<button class="btn btn-sm btn-outline" onclick="rejectComment(${c.id})">Reject</button>`
                    }
                    <button class="btn btn-sm btn-danger" onclick="deleteComment(${c.id})">Delete</button>
                </td>
            </tr>
        `).join('');

        renderPagination(document.getElementById('pagination'), data, loadComments);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><p>Error: ${escapeHtml(err.message)}</p></div></td></tr>`;
    }
}

async function approveComment(id) {
    try {
        await apiPatch(`/comments/${id}/approve`);
        showToast('Comment approved');
        loadComments();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function rejectComment(id) {
    try {
        await apiPatch(`/comments/${id}/reject`);
        showToast('Comment rejected');
        loadComments();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function deleteComment(id) {
    if (!confirm('Delete this comment permanently?')) return;
    try {
        await apiDelete(`/comments/${id}`);
        showToast('Comment deleted');
        loadComments();
    } catch (err) {
        showToast(err.message, 'error');
    }
}
