let rankingChart;

document.addEventListener("DOMContentLoaded", () => {
    loadData();
});

async function loadData() {
    try {
        const response = await fetch('database.json?_=' + new Date().getTime());
        if (!response.ok) throw new Error("JSON Fetch failed");
        const data = await response.json();
        
        renderDashboard(data);
    } catch (e) {
        console.warn("Lỗi fetch JSON, đang chạy dữ liệu Demo...", e);
        const demoData = {
            "revenue": 14500000, 
            "keywords": [
              {"keyword": "bọt vệ sinh tai chó mèo tốt nhất", "history": [45, 30, 15, 4]},
              {"keyword": "chữa viêm tai chó ecopets", "history": [60, 42, 21, 9]},
              {"keyword": "chó bầu nên uống canxi gì", "history": [80, 55, 35, 12]}
            ],
            "articles": [
              {"title": "Cách Trị Dứt Điểm Viêm Tai Chó Mèo Tại Nhà Bằng Bọt Thuần Chay", "keyword": "bọt vệ sinh tai chó mèo tốt nhất", "status": "Published", "date": "2026-03-10"},
              {"title": "Bà Bầu Chó Mèo Nên Uống Canxi Hữu Cơ Để Tránh Sỏi Thận", "keyword": "chó bầu nên uống canxi gì", "status": "Published", "date": "2026-03-15"}
            ]
        };
        renderDashboard(demoData);
    }
}

function formatVND(value) {
    return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' }).format(value);
}

function renderDashboard(data) {
    // Render Revenue
    let rev = data.revenue || 0;
    document.getElementById('total-revenue').innerText = formatVND(rev);
    
    document.getElementById('total-keywords').innerText = data.keywords ? data.keywords.length : 0;
    document.getElementById('total-articles').innerText = data.articles ? data.articles.length : 0;
    
    let top10 = 0;
    if(data.keywords) {
        top10 = data.keywords.filter(k => k.history[k.history.length - 1] <= 10).length;
    }
    document.getElementById('top-10-count').innerText = top10;

    if(data.keywords) renderChart(data.keywords);
    if(data.articles) {
        renderTimeline(data.articles);
        renderTable(data.articles);
    }
}

function renderChart(keywordsData) {
    const ctx = document.getElementById('rankingChart').getContext('2d');
    if(rankingChart) rankingChart.destroy();

    const colors = ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6'];
    const datasets = keywordsData.map((kw, idx) => ({
        label: kw.keyword,
        data: kw.history,
        borderColor: colors[idx % colors.length],
        tension: 0.4,
        fill: false,
        borderWidth: 3,
        pointBackgroundColor: colors[idx % colors.length],
        pointRadius: 4
    }));

    rankingChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: ['Tuần 1', 'Tuần 2', 'Tuần 3', 'Tuần Hiện Tại'],
            datasets: datasets
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    reverse: true, // Rank 1 is at the top
                    min: 1,
                    max: 100,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8' }
                }
            },
            plugins: {
                legend: {
                    labels: { color: '#f8fafc', font: { family: 'Outfit' } }
                }
            }
        }
    });
}

function renderTimeline(articles) {
    const container = document.getElementById('timeline-container');
    container.innerHTML = '';
    const sorted = [...articles].sort((a,b) => new Date(a.date) - new Date(b.date));
    
    sorted.slice(-4).forEach(art => {
        const d = new Date(art.date);
        const dateStr = d.toLocaleDateString('vi-VN', { day: '2-digit', month: 'short' });
        
        container.innerHTML += `
            <div class="timeline-item">
                <div class="timeline-date">${dateStr}</div>
                <div class="timeline-content">
                    <h4>${art.title.length > 35 ? art.title.substring(0,35)+'...' : art.title}</h4>
                    <p>Khách mục tiêu: ${art.keyword}</p>
                </div>
            </div>
        `;
    });
}

function renderTable(articles) {
    const tbody = document.getElementById('articles-tbody');
    tbody.innerHTML = '';
    articles.forEach(art => {
        let statusClass = art.status.toLowerCase();
        const d = new Date(art.date);
        const dateStr = d.toLocaleDateString('vi-VN');

        tbody.innerHTML += `
            <tr>
                <td><strong>${art.title}</strong></td>
                <td><span style="color:#10b981;">${art.keyword}</span></td>
                <td><span class="status ${statusClass}">${art.status}</span></td>
                <td>${dateStr}</td>
            </tr>
        `;
    });
}
