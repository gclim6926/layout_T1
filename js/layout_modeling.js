async function runLayoutSeed() {
    try {
        showLoading();
        const response = await fetch('/api/get-input-data');
        const result = await response.json();
        if (result.success) {
            showStatus('input.json 데이터를 성공적으로 로드했습니다.', 'success');
            displayInputForm(result.data);
        } else {
            showStatus('input.json 데이터 로드 실패: ' + result.message, 'error');
        }
    } catch (error) {
        showStatus(`input.json 데이터 로드 중 오류가 발생했습니다: ${error.message}`, 'error');
    } finally {
        hideLoading();
    }
}

function displayInputForm(inputData) {
    const resultArea = document.getElementById('resultArea');
    const container = document.createElement('div');
    container.className = 'execution-result';
    const title = document.createElement('h3');
    title.textContent = '🔧 Layout Seed - input.json 편집';
    container.appendChild(title);
    const description = document.createElement('p');
    description.textContent = '아래 폼에서 input.json의 모든 값을 수정할 수 있습니다. 수정 후 "Update input.json" 버튼을 클릭하세요.';
    container.appendChild(description);
    const form = document.createElement('form');
    form.id = 'inputForm';
    form.onsubmit = updateInputJson;

    function createFormFieldsDOM(obj, prefix = '') {
        const fragment = document.createDocumentFragment();
        for (const [key, value] of Object.entries(obj)) {
            const fieldName = prefix ? `${prefix}.${key}` : key;
            if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                const section = document.createElement('div');
                section.className = 'input-section';
                const sectionTitle = document.createElement('h4');
                sectionTitle.textContent = `🔧 ${key}`;
                section.appendChild(sectionTitle);
                const nestedFields = createFormFieldsDOM(value, fieldName);
                section.appendChild(nestedFields);
                fragment.appendChild(section);
            } else {
                const formGroup = document.createElement('div');
                formGroup.className = 'form-group';
                const label = document.createElement('label');
                label.textContent = `${key}:`;
                formGroup.appendChild(label);
                const textarea = document.createElement('textarea');
                textarea.name = fieldName;
                textarea.rows = Array.isArray(value) ? Math.min(value.length + 2, 10) : 4;
                textarea.className = 'form-control';
                textarea.value = JSON.stringify(value, null, 2);
                formGroup.appendChild(textarea);
                fragment.appendChild(formGroup);
            }
        }
        return fragment;
    }

    const formFields = createFormFieldsDOM(inputData);
    form.appendChild(formFields);
    const actionsDiv = document.createElement('div');
    actionsDiv.className = 'form-actions';
    const submitButton = document.createElement('button');
    submitButton.type = 'submit';
    submitButton.className = 'update-btn';
    submitButton.textContent = 'Update input.json';
    actionsDiv.appendChild(submitButton);
    form.appendChild(actionsDiv);
    container.appendChild(form);
    resultArea.innerHTML = '';
    resultArea.appendChild(container);
}

async function updateInputJson(event) {
    event.preventDefault();
    try {
        showLoading();
        let form = document.getElementById('inputForm') || document.querySelector('#resultArea form') || document.querySelector('form');
        if (!form) throw new Error('inputForm을 찾을 수 없습니다.');
        const formData = new FormData(form);
        const inputData = {};
        for (let [key, value] of formData.entries()) {
            const keys = key.split('.');
            let current = inputData;
            for (let i = 0; i < keys.length - 1; i++) {
                if (!current[keys[i]]) current[keys[i]] = {};
                current = current[keys[i]];
            }
            current[keys[keys.length - 1]] = JSON.parse(value);
        }
        const response = await fetch('/api/update-input-json', {
            method: 'POST', headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(inputData)
        });
        const result = await response.json();
        if (result.success) showStatus('✅ input.json이 성공적으로 업데이트되었습니다.', 'success');
        else showStatus('❌ input.json 업데이트 실패: ' + result.message, 'error');
    } catch (error) {
        showStatus(`input.json 업데이트 중 오류가 발생했습니다: ${error.message}`, 'error');
    } finally { hideLoading(); }
}


