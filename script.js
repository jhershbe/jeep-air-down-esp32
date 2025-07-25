// Command state for Air Up/Down (local UI state)
let airUpActive = false;
let airDownActive = false;

// Track expected states to prevent flicker from slow status updates
let airUpExpectedState = 'live';
let airDownExpectedState = 'live';

// Refresh pressure reading
function refreshPressure() {
    fetch('/pressure').then(r => r.json()).then(d => {
        document.getElementById('pressure').innerText = d.pressure;
    });
}

// Load setpoints from server
function loadSetpoints() {
    fetch('/get_setpoints').then(r => r.json()).then(d => {
        document.getElementById('setpoint_onroad').value = d.setpoint_onroad;
        document.getElementById('setpoint_offroad').value = d.setpoint_offroad;
    });
}

// Save setpoints with visual feedback
function saveSetpoints() {
    const btn = document.querySelector('.save-setpoints');
    const originalBg = btn.style.backgroundColor;
    const originalColor = btn.style.color;
    btn.style.backgroundColor = '#bae6fd'; // mild baby blue
    btn.style.color = '#2563eb'; // blue text for contrast
    btn.disabled = true;
    const s_onroad = document.getElementById('setpoint_onroad').value;
    const s_offroad = document.getElementById('setpoint_offroad').value;
    fetch('/set_setpoints', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({setpoint_onroad: s_onroad, setpoint_offroad: s_offroad})
    }).then(() => {
        btn.style.backgroundColor = originalBg;
        btn.style.color = originalColor;
        btn.disabled = false;
    });
}

// Apply button visual changes immediately
function updateButtonVisuals(btn, state, elapsed) {
    if (state === 'idle') {
        btn.textContent = btn.classList.contains('air-up') ? 'Air Up' : 'Air Down';
        btn.style.backgroundColor = '';
        btn.style.color = '';
        btn.disabled = false;
    } else if (state === 'starting') {
        btn.textContent = btn.classList.contains('air-up') ? 'Air Up...' : 'Air Down...';
        btn.style.backgroundColor = '';
        btn.style.color = '';
        btn.disabled = true;
    } else if (state === 'running') {
        const timeText = elapsed !== undefined ? `Cancel (${elapsed.toFixed(0)}s)` : 'Cancel';
        btn.textContent = timeText;
        btn.style.backgroundColor = '#bae6fd';
        btn.style.color = '#2563eb';
        btn.disabled = false;
    } else if (state === 'cancelling') {
        btn.textContent = 'Cancelling...';
        btn.style.backgroundColor = '#bae6fd';
        btn.style.color = '#2563eb';
        btn.disabled = true;
    } else if (state === 'blocked') {
        btn.style.backgroundColor = '#fecaca';
        setTimeout(() => { btn.style.backgroundColor = ''; }, 300);
    }
}

// Set button state with flicker prevention
function setButtonState(btn, state, elapsed, source) {
    const isAirUp = btn.classList.contains('air-up');
    const currentExpected = isAirUp ? airUpExpectedState : airDownExpectedState;

    if (source === 'click') {
        // Update immediately and set expected state
        if (isAirUp) {
            airUpExpectedState = state;
        } else {
            airDownExpectedState = state;
        }
        if (state === 'running') {
            temp_state = 'starting';
        } else if (state === 'idle') {
            temp_state = 'cancelling';
        } else {
            temp_state = state;
        }
        updateButtonVisuals(btn, temp_state, elapsed);
    } else if (source === 'status' && currentExpected !== 'live') {
        // Only update if status matches expected state or if we're not expecting anything
        if (state === currentExpected) {
            updateButtonVisuals(btn, state, elapsed);
            // Clear expected state when status catches up
            if (isAirUp) {
                airUpExpectedState = 'live';
            } else {
                airDownExpectedState = 'live';
            }
        }
    } else {
        // Default behavior when live
        updateButtonVisuals(btn, state, elapsed);
    }
}

// Air Up with visual feedback and cancellation
function airUp() {
    const btn = document.querySelector('.air-up');
    if (airDownActive) {
        setButtonState(btn, 'blocked', undefined, 'click');
        return;
    }
    if (!airUpActive) {
        // Start operation - update UI immediately
        setButtonState(btn, 'running', 0, 'click');
        fetch('/air_up?action=start', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
            });
    } else {
        // Cancel operation - update UI immediately
        setButtonState(btn, 'idle', undefined, 'click');
        fetch('/air_up?action=cancel', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
            });
    }
}

// Air Down with visual feedback and cancellation
function airDown() {
    const btn = document.querySelector('.air-down');
    if (airUpActive) {
        setButtonState(btn, 'blocked', undefined, 'click');
        return;
    }
    if (!airDownActive) {
        // Start operation - update UI immediately
        setButtonState(btn, 'running', 0, 'click');
        fetch('/air_down?action=start', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
            });
    } else {
        // Cancel operation - update UI immediately
        setButtonState(btn, 'idle', undefined, 'click');
        fetch('/air_down?action=cancel', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
            });
    }
}

// Poll firmware status when both commands are idle
function pollFirmwareStatus() {
    fetch('/air_up?action=status', {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            const btn = document.querySelector('.air-up');
            if (data.status === 'running') {
                airUpActive = true;
                const elapsedTime = data.time || 0;
                setButtonState(btn, 'running', elapsedTime, 'status');
            } else {
                airUpActive = false;
                setButtonState(btn, 'idle', undefined, 'status');
            }
        });
    fetch('/air_down?action=status', {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            const btn = document.querySelector('.air-down');
            if (data.status === 'running') {
                airDownActive = true;
                const elapsedTime = data.time || 0;
                setButtonState(btn, 'running', elapsedTime, 'status');
            } else {
                airDownActive = false;
                setButtonState(btn, 'idle', undefined, 'status');
            }
        });
}

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh pressure every 1000ms to avoid overwhelming the ESP32
    setInterval(refreshPressure, 1000);
    setInterval(pollFirmwareStatus, 1000);
    refreshPressure();
    loadSetpoints();
});
