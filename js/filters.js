function getFilterValues() {
    const layers = Array.from(document.querySelectorAll('input[value^="z"]:checked')).map(cb => cb.value);
    const components = [];
    const addressesChecked = document.querySelector('input[value="addresses"]').checked;
    const linesChecked = document.querySelector('input[value="lines"]').checked;
    const stationsChecked = document.querySelector('input[value="stations"]').checked;
    const ohtsChecked = document.querySelector('input[value="ohts"]').checked;
    const equipmentsChecked = document.querySelector('input[value="equipments"]').checked;
    if (addressesChecked) components.push('addresses');
    if (linesChecked) components.push('lines');
    if (stationsChecked) components.push('stations');
    if (ohtsChecked) components.push('ohts');
    if (equipmentsChecked) components.push('equipments');

    const overlapCheckbox = document.querySelector('input[value="Overlap"]');
    const overlapChecked = overlapCheckbox ? overlapCheckbox.checked : false;
    if (overlapChecked) layers.push('Overlap');
    return { layers, components };
}

function applyFilters() {
    const filters = getFilterValues();
    showStatus('필터가 적용되었습니다.', 'info');
    if (currentView === '2d') {
        run2DViewer();
    } else if (currentView === '3d') {
        run3DViewer();
    }
}


