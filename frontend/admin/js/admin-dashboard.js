/**
 * Dashboard page logic — loads stats and visitor chart.
 */

let visitorChart = null;

document.addEventListener('DOMContentLoaded', async () => {
    if (!(await checkAuth())) return;
    initSidebar();
    loadStats();
    loadVisitorChart('7d');

    document.querySelectorAll('.chart-toggle button').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.chart-toggle button').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            loadVisitorChart(btn.dataset.period);
        });
    });
});

async function loadStats() {
    try {
        const stats = await apiGet('/dashboard/stats');
        if (!stats) return;

        document.getElementById('statPosts').textContent = stats.total_posts;
        document.getElementById('statPostsDetail').textContent =
            `${stats.published_posts} published, ${stats.draft_posts} drafts, ${stats.archived_posts} archived`;

        document.getElementById('statVisitors7d').textContent = stats.total_visitors_7d.toLocaleString();
        document.getElementById('statVisitors30d').textContent = `${stats.total_visitors_30d.toLocaleString()} in 30 days`;

        document.getElementById('statComments').textContent = stats.pending_comments;
        document.getElementById('statCommentsDetail').textContent = `${stats.total_comments} total`;

        document.getElementById('statSubscribers').textContent = stats.active_subscribers;
        document.getElementById('statSubscribersDetail').textContent = `${stats.total_subscribers} total`;

        if (stats.unread_contacts > 0) {
            document.getElementById('unreadContactsCard').style.display = '';
            document.getElementById('unreadContactsMsg').textContent =
                `You have ${stats.unread_contacts} unread contact submission${stats.unread_contacts > 1 ? 's' : ''}.`;
        }
    } catch (err) {
        console.error('Failed to load stats:', err);
    }
}

async function loadVisitorChart(period) {
    try {
        const data = await apiGet(`/dashboard/visitors?period=${period}`);
        if (!data) return;

        const labels = data.data.map(d => {
            const date = new Date(d.date);
            return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        });
        const values = data.data.map(d => d.visitors);

        if (visitorChart) visitorChart.destroy();

        const ctx = document.getElementById('visitorChart').getContext('2d');
        visitorChart = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Visitors',
                    data: values,
                    backgroundColor: 'rgba(52, 152, 219, 0.6)',
                    borderColor: '#3498db',
                    borderWidth: 1,
                    borderRadius: 4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: { precision: 0 }
                    }
                }
            }
        });
    } catch (err) {
        console.error('Failed to load visitor chart:', err);
    }
}
