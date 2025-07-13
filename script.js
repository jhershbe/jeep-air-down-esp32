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
    const s_onroad = document.getElementById('setpoint_onroad').value;
    const s_offroad = document.getElementById('setpoint_offroad').value;
    fetch('/set_setpoints', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({setpoint_onroad: s_onroad, setpoint_offroad: s_offroad})
    }).then(() => alert('Setpoints saved!'));
}

// Air Up with visual feedback and cancellation
function airUp() {
        fetch('/air_up', {method: 'POST'})
            .then(() => alert('Air Up command sent!'));
}

// Air Down with visual feedback and cancellation
function airDown() {
        fetch('/air_down', {method: 'POST'})
            .then(() => alert('Air Down command sent!'));
}

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh pressure every 2 seconds
    setInterval(refreshPressure, 2000);
    refreshPressure();
    loadSetpoints();
});
