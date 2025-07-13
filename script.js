// Command state for Air Up/Down
let airUpActive = false;
let airDownActive = false;

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

// Air Up with visual feedback and cancellation
function airUp() {
    const btn = document.querySelector('.air-up');
    
    // Don't allow Air Up if Air Down is active
    if (airDownActive) {
        // Optional: flash or highlight the Air Down button to show it's blocking
        const downBtn = document.querySelector('.air-down');
        const originalBg = downBtn.style.backgroundColor;
        downBtn.style.backgroundColor = '#fecaca'; // light red
        setTimeout(() => { downBtn.style.backgroundColor = originalBg; }, 300);
        return; // Do nothing else
    }
    
    if (!airUpActive) {
        // Start operation
        btn.style.backgroundColor = '#bae6fd';
        btn.style.color = '#2563eb';
        btn.disabled = true;
        
        fetch('/air_up?action=start', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.status === 'started' || data.status === 'already_running') {
                    airUpActive = true;
                    btn.disabled = false;
                    btn.textContent = 'Cancel (0.0s)'; // Set initial timer text
                    checkAirUpStatus();
                } else {
                    btn.style.backgroundColor = '';
                    btn.style.color = '';
                    btn.disabled = false;
                }
            });
    } else {
        // Cancel operation
        fetch('/air_up?action=cancel', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                airUpActive = false;
                btn.style.backgroundColor = '';
                btn.style.color = '';
                btn.textContent = 'Air Up';
            });
    }
}

// Air Down with visual feedback and cancellation
function airDown() {
    const btn = document.querySelector('.air-down');
    
    // Don't allow Air Down if Air Up is active
    if (airUpActive) {
        // Optional: flash or highlight the Air Up button to show it's blocking
        const upBtn = document.querySelector('.air-up');
        const originalBg = upBtn.style.backgroundColor;
        upBtn.style.backgroundColor = '#fecaca'; // light red
        setTimeout(() => { upBtn.style.backgroundColor = originalBg; }, 300);
        return; // Do nothing else
    }
    
    if (!airDownActive) {
        // Start operation
        btn.style.backgroundColor = '#bae6fd';
        btn.style.color = '#2563eb';
        btn.disabled = true;
        
        fetch('/air_down?action=start', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                if (data.status === 'started' || data.status === 'already_running') {
                    airDownActive = true;
                    btn.disabled = false;
                    btn.textContent = 'Cancel (0.0s)'; // Set initial timer text
                    checkAirDownStatus();
                } else {
                    // Error or other status
                    btn.style.backgroundColor = '';
                    btn.style.color = '';
                    btn.disabled = false;
                }
            });
    } else {
        // Cancel operation
        fetch('/air_down?action=cancel', {method: 'POST'})
            .then(response => response.json())
            .then(data => {
                airDownActive = false;
                btn.style.backgroundColor = '';
                btn.style.color = '';
                btn.textContent = 'Air Down';
            });
    }
}

// Check Air Up status periodically
function checkAirUpStatus() {
    if (!airUpActive) return;
    
    fetch('/air_up?action=status', {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            const btn = document.querySelector('.air-up');
            if (data.status === 'running') {
                // Get elapsed time from API response (already calculated on server)
                const elapsedTime = data.time || 0;
                const formattedTime = elapsedTime.toFixed(1);
                
                // Update button text with elapsed time
                btn.textContent = `Cancel (${formattedTime}s)`;
                
                // Simple static highlight color for active state
                btn.style.backgroundColor = '#bae6fd'; // Light blue
                
                // Use 1000ms refresh to avoid overwhelming the ESP32
                setTimeout(checkAirUpStatus, 1000);
            } else {
                // Completed or cancelled
                airUpActive = false;
                btn.style.backgroundColor = '';
                btn.style.color = '';
                btn.textContent = 'Air Up'; // Restore button text
            }
        });
}

// Check Air Down status periodically
function checkAirDownStatus() {
    if (!airDownActive) return;
    
    fetch('/air_down?action=status', {method: 'GET'})
        .then(response => response.json())
        .then(data => {
            const btn = document.querySelector('.air-down');
            if (data.status === 'running') {
                // Get elapsed time from API response (already calculated on server)
                const elapsedTime = data.time || 0;
                const formattedTime = elapsedTime.toFixed(1);
                
                // Update button text with elapsed time
                btn.textContent = `Cancel (${formattedTime}s)`;
                
                // Simple static highlight color for active state
                btn.style.backgroundColor = '#bae6fd'; // Light blue
                
                // Use 1000ms refresh to avoid overwhelming the ESP32
                setTimeout(checkAirDownStatus, 1000);
            } else {
                // Completed or cancelled
                airDownActive = false;
                btn.style.backgroundColor = '';
                btn.style.color = '';
                btn.textContent = 'Air Down'; // Restore button text
            }
        });
}

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    // Auto-refresh pressure every 1000ms to avoid overwhelming the ESP32
    setInterval(refreshPressure, 1000);
    refreshPressure();
    loadSetpoints();
});
