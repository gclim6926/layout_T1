let currentView = null;
let sidebarVisible = true;

function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.getElementById('mainContent');
    const toggleBtn = document.querySelector('.sidebar-toggle');
    sidebarVisible = !sidebarVisible;
    if (sidebarVisible) {
        sidebar.classList.remove('hidden');
        mainContent.classList.remove('expanded');
        toggleBtn.style.left = '200px';
    } else {
        sidebar.classList.add('hidden');
        mainContent.classList.add('expanded');
        toggleBtn.style.left = '20px';
    }
}

function showStatus(message, type = 'info') {
    const statusArea = document.getElementById('statusArea');
    statusArea.innerHTML = `<div class="status-message status-${type}">${message}</div>`;
}

function showLoading() {
    document.getElementById('loadingArea').style.display = 'block';
    document.getElementById('resultArea').innerHTML = '';
}

function hideLoading() {
    document.getElementById('loadingArea').style.display = 'none';
}

window.addEventListener('load', async () => {
    try {
        const response = await fetch('/api/check-status');
        const result = await response.json();
        if (result.success) {
            showStatus('서버에 성공적으로 연결되었습니다.', 'success');
        } else {
            showStatus('서버 연결에 실패했습니다.', 'error');
        }
    } catch (error) {
        showStatus('서버 상태 확인 중 오류가 발생했습니다.', 'error');
    }
});


