/**
 * Visitor logs page logic.
 */

let currentPage = 1;

document.addEventListener('DOMContentLoaded', async () => {
    if (!(await checkAuth())) return;
    initSidebar();

    // Set default date range to last 7 days
    const now = new Date();
    const weekAgo = new Date(now);
    weekAgo.setDate(weekAgo.getDate() - 7);
    document.getElementById('endDate').value = now.toISOString().split('T')[0];
    document.getElementById('startDate').value = weekAgo.toISOString().split('T')[0];

    loadVisitors();
});

async function loadVisitors(page) {
    if (page) currentPage = page;
    const tbody = document.getElementById('visitorsTableBody');
    tbody.innerHTML = '<tr><td colspan="5"><div class="loading"><div class="spinner"></div></div></td></tr>';

    try {
        let url = `/visitors?page=${currentPage}&per_page=50`;

        const startDate = document.getElementById('startDate').value;
        const endDate = document.getElementById('endDate').value;
        const pageFilter = document.getElementById('pageFilter').value;

        if (startDate) url += `&start_date=${startDate}`;
        if (endDate) url += `&end_date=${endDate}`;
        if (pageFilter) url += `&page_filter=${encodeURIComponent(pageFilter)}`;

        const data = await apiGet(url);
        if (!data) return;

        if (data.visitors.length === 0) {
            tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state"><p>No visitor logs found for the selected period.</p></div></td></tr>';
            document.getElementById('pagination').innerHTML = '';
            return;
        }

        tbody.innerHTML = data.visitors.map(v => `
            <tr>
                <td>${escapeHtml(v.page || '—')}</td>
                <td class="truncate">${escapeHtml(v.referrer || '—')}</td>
                <td class="truncate" style="max-width:200px">${escapeHtml(truncate(v.user_agent, 60) || '—')}</td>
                <td>${escapeHtml(v.ip_address || '—')}</td>
                <td style="white-space:nowrap">${formatDate(v.timestamp)}</td>
            </tr>
        `).join('');

        renderPagination(document.getElementById('pagination'), data, loadVisitors);
    } catch (err) {
        tbody.innerHTML = `<tr><td colspan="5"><div class="empty-state"><p>Error: ${escapeHtml(err.message)}</p></div></td></tr>`;
    }
}
