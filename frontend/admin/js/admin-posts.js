/**
 * Posts list page logic — filtering, search, CRUD actions.
 */

let currentStatus = '';
let currentSearch = '';
let currentPage = 1;
let deletePostId = null;

document.addEventListener('DOMContentLoaded', async () => {
    if (!(await checkAuth())) return;
    initSidebar();
    loadPosts();

    // Tab filters
    document.querySelectorAll('#statusTabs button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('#statusTabs button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            currentStatus = btn.dataset.status;
            currentPage = 1;
            loadPosts();
        });
    });

    // Search
    let searchTimeout;
    document.getElementById('searchInput').addEventListener('input', (e) => {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            currentSearch = e.target.value;
            currentPage = 1;
            loadPosts();
        }, 300);
    });
});

async function loadPosts(page) {
    if (page) currentPage = page;
    const tbody = document.getElementById('postsTableBody');
    tbody.innerHTML = '<tr><td colspan="6"><div class="loading"><div class="spinner"></div></div></td></tr>';

    try {
        let url = `/posts?page=${currentPage}&per_page=20`;
        if (currentStatus) url += `&status=${currentStatus}`;
        if (currentSearch) url += `&search=${encodeURIComponent(currentSearch)}`;

        const data = await apiGet(url);
        if (!data) return;

        if (data.posts.length === 0) {
            tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><p>No posts found.</p></div></td></tr>';
            document.getElementById('pagination').innerHTML = '';
            return;
        }

        tbody.innerHTML = data.posts.map(p => `
            <tr>
                <td><strong>${escapeHtml(p.title)}</strong></td>
                <td>${escapeHtml(p.category)}</td>
                <td><span class="badge badge-${p.status}">${p.status}</span></td>
                <td>
                    <button class="btn btn-sm ${p.featured ? 'btn-warning' : 'btn-outline'}" onclick="toggleFeatured(${p.id})" title="${p.featured ? 'Remove featured' : 'Set as featured'}">
                        ${p.featured ? 'Yes' : 'No'}
                    </button>
                </td>
                <td>${formatDate(p.created_at)}</td>
                <td class="actions">
                    <a href="post-editor.html?id=${p.id}" class="btn btn-sm btn-outline">Edit</a>
                    ${p.status === 'archived'
                        ? `<button class="btn btn-sm btn-success" onclick="changeStatus(${p.id}, 'published')">Restore</button>`
                        : p.status === 'published'
                            ? `<button class="btn btn-sm btn-outline" onclick="changeStatus(${p.id}, 'archived')">Archive</button>`
                            : `<button class="btn btn-sm btn-success" onclick="changeStatus(${p.id}, 'published')">Publish</button>`
                    }
                    <button class="btn btn-sm btn-danger" onclick="openDeleteModal(${p.id})">Delete</button>
                </td>
            </tr>
        `).join('');

        renderPagination(document.getElementById('pagination'), data, loadPosts);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="6"><div class="empty-state"><p>Error loading posts: ${escapeHtml(err.message)}</p></div></td></tr>`;
    }
}

async function toggleFeatured(id) {
    try {
        await apiPatch(`/posts/${id}/featured`);
        showToast('Featured status updated');
        loadPosts();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

async function changeStatus(id, status) {
    try {
        const res = await fetch(`${ADMIN_API}/posts/${id}/status`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'include',
            body: JSON.stringify({ status })
        });
        if (!res.ok) throw new Error('Failed to update status');
        showToast(`Post ${status === 'archived' ? 'archived' : status === 'published' ? 'published' : 'updated'}`);
        loadPosts();
    } catch (err) {
        showToast(err.message, 'error');
    }
}

function openDeleteModal(id) {
    deletePostId = id;
    document.getElementById('deleteModal').classList.add('visible');
    document.getElementById('confirmDeleteBtn').onclick = async () => {
        try {
            await apiDelete(`/posts/${deletePostId}`);
            showToast('Post deleted');
            closeDeleteModal();
            loadPosts();
        } catch (err) {
            showToast(err.message, 'error');
        }
    };
}

function closeDeleteModal() {
    document.getElementById('deleteModal').classList.remove('visible');
    deletePostId = null;
}
