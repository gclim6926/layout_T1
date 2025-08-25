async function run3DViewer() {
    try {
        showLoading();
        const response = await fetch('/api/3d-viewer', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(getFilterValues())
        });
        const result = await response.json();
        hideLoading();
        if (result.success) {
            showStatus('✅ 3D Viewer가 성공적으로 실행되었습니다.', 'success');
            if (result.execution_output) {
                displayExecutionOutput('3D Viewer', result.execution_output, result.config_updated);
            }
        } else {
            showStatus('❌ 3D Viewer 실행 실패: ' + result.message, 'error');
        }
    } catch (error) {
        hideLoading();
        showStatus('❌ 3D Viewer 실행 중 오류 발생: ' + error.message, 'error');
    }
}


