async function runAddAddresses() {
    try {
        showLoading();
        const res = await fetch('/api/run-generate', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
        const result = await res.json();
        hideLoading();
        if (result.success) {
            showStatus('✅ add Addresses가 성공적으로 실행되었습니다.', 'success');
            if (result.execution_output) displayExecutionOutput('add Addresses', result.execution_output, result.config_updated);
        } else {
            showStatus('❌ add Addresses 실행 실패: ' + result.message, 'error');
        }
    } catch (e) {
        hideLoading();
        showStatus('❌ add Addresses 실행 중 오류 발생: ' + e.message, 'error');
    }
}

async function runAddLines() {
    try {
        showLoading();
        const res = await fetch('/api/run-add-lines', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
        const result = await res.json();
        hideLoading();
        if (result.success) {
            showStatus('✅ add Lines가 성공적으로 실행되었습니다.', 'success');
            if (result.execution_output) displayExecutionOutput('add Lines', result.execution_output, result.config_updated);
        } else {
            showStatus('❌ add Lines 실행 실패: ' + result.message, 'error');
        }
    } catch (e) {
        hideLoading();
        showStatus('❌ add Lines 실행 중 오류 발생: ' + e.message, 'error');
    }
}

async function runCheckPy() {
    try {
        showLoading();
        const res = await fetch('/api/run-check', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
        const result = await res.json();
        hideLoading();
        if (result.success) {
            showStatus('✅ Checker가 성공적으로 실행되었습니다.', 'success');
            if (result.execution_output) displayExecutionOutput('Checker', result.execution_output, result.config_updated);
        } else {
            showStatus('❌ Checker 실행 실패: ' + result.message, 'error');
        }
    } catch (e) {
        hideLoading();
        showStatus('❌ Checker 실행 중 오류 발생: ' + e.message, 'error');
    }
}

async function runStationsPy() {
    try {
        showLoading();
        const res = await fetch('/api/run-stations', { method: 'POST', headers: { 'Content-Type': 'application/json' } });
        const result = await res.json();
        hideLoading();
        if (result.success) {
            showStatus('✅ add Stations가 성공적으로 실행되었습니다.', 'success');
            if (result.execution_output) {
                const resultArea = document.getElementById('resultArea');
                let outputHTML = `
                    <div class="execution-result">
                        <h3>🚀 add Stations 실행 결과</h3>
                        <div class="result-section">
                            <h4>📊 실행 정보</h4>
                            <div class="config-info">
                                <p><strong>스크립트:</strong> ${result.config_updated.script}</p>
                                <p><strong>상태:</strong> ${result.config_updated.status}</p>
                                <p><strong>실행 방법:</strong> ${result.config_updated.method}</p>
                            </div>
                        </div>
                        <div class="result-section">
                            <h4>📝 터미널 출력</h4>
                            <div class="terminal-output"><pre>${result.execution_output.terminal_logs || '출력 없음'}</pre></div>
                        </div>
                        <div class="result-section">
                            <h4>🔍 상세 정보</h4>
                            <div class="detail-info">
                                <details><summary>stdout 출력</summary><pre>${result.execution_output.stdout || '출력 없음'}</pre></details>
                                <details><summary>stderr 출력</summary><pre>${result.execution_output.stderr || '출력 없음'}</pre></details>
                            </div>
                        </div>
                    </div>`;
                resultArea.innerHTML = outputHTML;
            }
        } else {
            showStatus('❌ add Stations 실행 실패: ' + result.message, 'error');
        }
    } catch (e) {
        hideLoading();
        showStatus('❌ add Stations 실행 중 오류 발생: ' + e.message, 'error');
    }
}

function showUDPGeneratorForm() {
    showStatus('UDP Generator 폼을 표시합니다.', 'info');
    document.getElementById('resultArea').innerHTML = `
        <div class="execution-result">
            <h3>🚀 UDP Generator</h3>
            <p>시작 주소에서 목적지 주소까지의 경로로 UDP 데이터를 생성합니다.</p>
            <form id="udpGeneratorForm" onsubmit="runUDPGenerator(event)">
                <div class="form-group">
                    <label for="startAddress">시작 주소:</label>
                    <input type="number" id="startAddress" name="startAddress" value="100050" class="form-control" required>
                </div>
                <div class="form-group">
                    <label for="destinationAddress">목적지 주소:</label>
                    <input type="number" id="destinationAddress" name="destinationAddress" value="100100" class="form-control" required>
                </div>
                <div class="form-actions">
                    <button type="submit" class="update-btn">UDP 데이터 생성</button>
                </div>
            </form>
        </div>`;
}

async function runUDPGenerator(event) {
    event.preventDefault();
    try {
        const startAddress = parseInt(document.getElementById('startAddress').value);
        const destinationAddress = parseInt(document.getElementById('destinationAddress').value);
        showLoading();
        const response = await fetch('/api/run-udp-generator', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ start_address: startAddress, destination_address: destinationAddress })
        });
        const result = await response.json();
        hideLoading();
        if (result.success) {
            showStatus('✅ UDP Generator가 성공적으로 실행되었습니다.', 'success');
            if (result.execution_output) {
                const resultArea = document.getElementById('resultArea');
                let outputHTML = `
                    <div class="execution-result">
                        <h3>🚀 UDP Generator 실행 결과</h3>
                        <div class="result-section">
                            <h4>📊 실행 정보</h4>
                            <div class="config-info">
                                <p><strong>스크립트:</strong> ${result.config_updated.script}</p>
                                <p><strong>상태:</strong> ${result.config_updated.status}</p>
                                <p><strong>실행 방법:</strong> ${result.config_updated.method}</p>
                                <p><strong>시작 주소:</strong> ${result.config_updated.start_address}</p>
                                <p><strong>목적지 주소:</strong> ${result.config_updated.destination_address}</p>
                            </div>
                        </div>
                        <div class="result-section">
                            <h4>📝 터미널 출력</h4>
                            <div class="terminal-output"><pre>${result.execution_output.terminal_logs || '출력 없음'}</pre></div>
                        </div>
                        <div class="result-section">
                            <h4>🔍 상세 정보</h4>
                            <div class="detail-info">
                                <details><summary>stdout 출력</summary><pre>${result.execution_output.stdout || '출력 없음'}</pre></details>
                                <details><summary>stderr 출력</summary><pre>${result.execution_output.stderr || '출력 없음'}</pre></details>
                            </div>
                        </div>
                        <div class="form-actions">
                            <button onclick="showUDPGeneratorForm()" class="update-btn">새로운 UDP 데이터 생성</button>
                        </div>
                    </div>`;
                resultArea.innerHTML = outputHTML;
            }
        } else {
            showStatus('❌ UDP Generator 실행 실패: ' + result.message, 'error');
        }
    } catch (error) {
        hideLoading();
        showStatus('❌ UDP Generator 실행 중 오류 발생: ' + error.message, 'error');
    }
}

function displayExecutionOutput(viewerName, executionOutput, configUpdated) {
    const resultArea = document.getElementById('resultArea');
    let outputHTML = `
        <div class="execution-result">
            <h3>🚀 ${viewerName} 실행 결과</h3>
            <div class="result-section">
                <h4>📊 설정 정보</h4>
                <div class="config-info">
                    <p><strong>선택된 레이어:</strong> ${configUpdated.selected_layers ? configUpdated.selected_layers.join(', ') : 'N/A'}</p>
                    <p><strong>시각화 모드:</strong> ${configUpdated.visualization_mode || 'N/A'}</p>
                </div>
            </div>
            <div class="result-section">
                <h4>📝 터미널 출력</h4>
                <div class="terminal-output"><pre>${executionOutput.terminal_logs || '출력 없음'}</pre></div>
            </div>
            <div class="result-section">
                <h4>🔍 상세 정보</h4>
                <div class="detail-info">
                    <details><summary>stdout 출력</summary><pre>${executionOutput.stdout || '출력 없음'}</pre></details>
                    <details><summary>stderr 출력</summary><pre>${executionOutput.stderr || '출력 없음'}</pre></details>
                </div>
            </div>
        </div>`;
    resultArea.innerHTML = outputHTML;
}

// Menu routing
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.menu-item').forEach(item => {
        item.addEventListener('click', function() {
            document.querySelectorAll('.menu-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
            const view = this.getAttribute('data-view');
            currentView = view;
            switch(view) {
                case '2d': run2DViewer(); break;
                case '3d': run3DViewer(); break;
                case 'layout_seed': runLayoutSeed(); break;
                case 'add_addresses': runAddAddresses(); break;
                case 'add_lines_endpoint': runAddLines(); break;
                case 'check': runCheckPy(); break;
                case 'stations': runStationsPy(); break;
                case 'udp_generator': showUDPGeneratorForm(); break;
                case 'equipments': showEquipmentsInfo(); break;
            }
        });
    });
});

function showEquipmentsInfo() {
    showStatus('Equipments 정보를 표시합니다.', 'info');
    document.getElementById('resultArea').innerHTML = `
        <h3>Equipments 정보</h3>
        <p>Equipments는 레이아웃의 장비들을 나타냅니다.</p>
        <p>현재는 기본적인 정보만 표시됩니다.</p>
        <p>더 자세한 정보를 보려면 "add Addresses" 메뉴를 선택하세요.</p>`;
}


