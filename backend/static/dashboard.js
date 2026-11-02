/**
 * Smart Blind Stick - Real-Time Telemetry Dashboard
 * Handles live polling, Chart.js time-series updates, gauge calculations,
 * and connection health monitoring.
 */

// Global Configuration
const CONFIG = {
  POLL_INTERVAL_MS: 1500,
  MAX_CHART_POINTS: 25,
  STALE_THRESHOLD_SECONDS: 5.0,
  API_BASE: window.location.origin
};

// Application State
const state = {
  backendConnected: false,
  lastReading: null,
  lastSuccessfulFetchTime: null,
  totalReadingsCount: 0,
  readingsHistory: [],
  chartInstance: null
};

// DOM Element References
const elements = {
  alertBanner: document.getElementById('system-alert-banner'),
  alertIcon: document.getElementById('alert-icon'),
  alertText: document.getElementById('alert-text'),
  backendStatusText: document.getElementById('backend-status-text'),
  backendDot: document.getElementById('backend-dot'),
  esp32Dot: document.getElementById('esp32-dot'),
  deviceIdText: document.getElementById('device-id-text'),
  lastPingText: document.getElementById('last-ping-text'),
  heroCard: document.getElementById('hero-card'),
  distanceValue: document.getElementById('distance-value'),
  distanceUnit: document.getElementById('distance-unit'),
  distanceDescription: document.getElementById('distance-description'),
  warningBadge: document.getElementById('warning-badge'),
  gaugeFill: document.getElementById('gauge-fill'),
  buzzerStateText: document.getElementById('buzzer-state-text'),
  rhythmVisualizer: document.getElementById('rhythm-visualizer'),
  totalReadingsCount: document.getElementById('total-readings-count'),
  sensorLatencyVal: document.getElementById('sensor-latency-val'),
  dbHealthBadge: document.getElementById('db-health-badge'),
  chartCanvas: document.getElementById('distanceChart'),
  chartOverlay: document.getElementById('chart-empty-overlay'),
  tableRowCount: document.getElementById('table-row-count'),
  readingsTbody: document.getElementById('readings-tbody'),
  btnRefreshChart: document.getElementById('btn-refresh-chart')
};

// Warning Level Evaluator (Matches ESP32 firmware thresholds)
function evaluateWarningLevel(distanceCm, status) {
  if (status !== 'valid' || distanceCm === null || distanceCm === undefined || distanceCm < 0) {
    return {
      level: 'UNKNOWN',
      badgeClass: 'badge-unknown',
      label: 'Unknown',
      description: 'Sensor timeout or obstacle out of reliable range.',
      buzzerText: 'Silent (Safe state / Invalid measurement)',
      visualizerClass: '',
      gaugePercent: 0
    };
  }

  if (distanceCm < 15.0) {
    return {
      level: 'VERY CLOSE',
      badgeClass: 'badge-very-close',
      label: 'Very Close',
      description: 'Immediate hazard ahead (< 15 cm)! Rapid alert pulses.',
      buzzerText: 'Rapid Beep (~150 ms cycle, 60ms pulse)',
      visualizerClass: 'active-fast',
      gaugePercent: 100
    };
  } else if (distanceCm <= 30.0) {
    return {
      level: 'DANGER',
      badgeClass: 'badge-danger',
      label: 'Danger',
      description: 'Obstacle in critical proximity (15 - 30 cm).',
      buzzerText: 'Fast Beep (~250 ms cycle, 60ms pulse)',
      visualizerClass: 'active',
      gaugePercent: 80
    };
  } else if (distanceCm <= 60.0) {
    return {
      level: 'CAUTION',
      badgeClass: 'badge-caution',
      label: 'Caution',
      description: 'Approaching obstacle (31 - 60 cm). Moderate frequency.',
      buzzerText: 'Medium Beep (~450 ms cycle, 60ms pulse)',
      visualizerClass: 'active',
      gaugePercent: 55
    };
  } else if (distanceCm <= 100.0) {
    return {
      level: 'WARNING',
      badgeClass: 'badge-warning',
      label: 'Warning',
      description: 'Distant obstacle detected (61 - 100 cm). Slow intermittent beeps.',
      buzzerText: 'Slow Beep (~800 ms cycle, 60ms pulse)',
      visualizerClass: 'active',
      gaugePercent: 30
    };
  } else {
    return {
      level: 'CLEAR',
      badgeClass: 'badge-clear',
      label: 'Clear',
      description: 'Path is clear (> 100 cm). Buzzer remains silent.',
      buzzerText: 'Silent (Path clear > 100 cm)',
      visualizerClass: '',
      gaugePercent: 10
    };
  }
}

// Initialize Chart.js Instance
function initChart() {
  if (!elements.chartCanvas) return;

  const ctx = elements.chartCanvas.getContext('2d');
  
  // Create subtle gradient under the distance curve
  const gradient = ctx.createLinearGradient(0, 0, 0, 300);
  gradient.addColorStop(0, 'rgba(56, 189, 248, 0.35)');
  gradient.addColorStop(1, 'rgba(56, 189, 248, 0.0)');

  state.chartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels: [],
      datasets: [{
        label: 'Obstacle Distance (cm)',
        data: [],
        borderColor: '#38bdf8',
        borderWidth: 2.5,
        backgroundColor: gradient,
        fill: true,
        tension: 0.35,
        pointBackgroundColor: '#0284c7',
        pointBorderColor: '#ffffff',
        pointBorderWidth: 1.5,
        pointRadius: 4,
        pointHoverRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: {
        duration: 400
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(255, 255, 255, 0.05)',
            borderColor: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: '#64748b',
            font: { family: 'JetBrains Mono', size: 11 },
            maxRotation: 0,
            autoSkip: true,
            maxTicksLimit: 8
          }
        },
        y: {
          min: 0,
          max: 200,
          grid: {
            color: 'rgba(255, 255, 255, 0.05)',
            borderColor: 'rgba(255, 255, 255, 0.1)'
          },
          ticks: {
            color: '#64748b',
            font: { family: 'JetBrains Mono', size: 11 },
            callback: function(value) { return value + ' cm'; }
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: 'rgba(15, 23, 42, 0.9)',
          titleFont: { family: 'Outfit', size: 13, weight: '600' },
          bodyFont: { family: 'JetBrains Mono', size: 12 },
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          padding: 10,
          displayColors: false,
          callbacks: {
            label: function(context) {
              const val = context.parsed.y;
              return val !== null ? `Distance: ${val.toFixed(1)} cm` : 'Status: Unknown';
            }
          }
        }
      }
    }
  });
}

// Update UI with latest telemetry data
function updateDashboardUI(latestData, recentReadings) {
  const reading = latestData ? latestData.reading : null;
  const isStale = latestData ? latestData.is_stale : true;
  const ageSeconds = latestData ? latestData.age_seconds : null;

  // Handle Backend Alert Banner
  if (!state.backendConnected) {
    showAlert('Backend Disconnected: Unable to reach telemetry server at ' + CONFIG.API_BASE, false);
    elements.backendStatusText.textContent = 'Disconnected';
    elements.backendDot.className = 'pulse-dot danger';
    elements.esp32Dot.className = 'pulse-dot danger';
    return;
  } else {
    elements.backendStatusText.textContent = 'Connected (HTTP 200)';
    elements.backendDot.className = 'pulse-dot pulse';
  }

  // Handle Stale Data Warning
  if (isStale && reading) {
    showAlert(`Stale Data Warning: No readings received from ESP32 for ${ageSeconds ? ageSeconds.toFixed(0) : '>5'}s. Stick may be offline.`, true);
    elements.esp32Dot.className = 'pulse-dot idle';
  } else if (!reading) {
    showAlert('Waiting for sensor data: ESP32 has not transmitted any telemetry yet.', true);
    elements.esp32Dot.className = 'pulse-dot idle';
  } else {
    hideAlert();
    elements.esp32Dot.className = 'pulse-dot pulse';
  }

  // Update Hero Distance Display
  if (reading && reading.status === 'valid' && reading.distance_cm !== null) {
    const dist = reading.distance_cm;
    elements.distanceValue.textContent = dist.toFixed(1);
    elements.distanceUnit.style.display = 'inline';
    elements.deviceIdText.textContent = reading.device_id;

    const evaluation = evaluateWarningLevel(dist, 'valid');
    elements.warningBadge.className = `warning-badge ${evaluation.badgeClass}`;
    elements.warningBadge.textContent = evaluation.level;
    elements.distanceDescription.textContent = evaluation.description;
    elements.gaugeFill.style.width = `${evaluation.gaugePercent}%`;
    elements.buzzerStateText.textContent = evaluation.buzzerText;
    elements.rhythmVisualizer.className = `rhythm-visualizer ${evaluation.visualizerClass}`;
  } else if (reading && reading.status === 'unknown') {
    elements.distanceValue.textContent = '--';
    elements.distanceUnit.style.display = 'none';
    elements.deviceIdText.textContent = reading.device_id;

    const evaluation = evaluateWarningLevel(null, 'unknown');
    elements.warningBadge.className = `warning-badge ${evaluation.badgeClass}`;
    elements.warningBadge.textContent = 'UNKNOWN';
    elements.distanceDescription.textContent = 'Sensor reported invalid reading / timeout.';
    elements.gaugeFill.style.width = '0%';
    elements.buzzerStateText.textContent = evaluation.buzzerText;
    elements.rhythmVisualizer.className = 'rhythm-visualizer';
  } else {
    elements.distanceValue.textContent = '--';
    elements.distanceUnit.style.display = 'none';
    elements.warningBadge.className = 'warning-badge badge-unknown';
    elements.warningBadge.textContent = 'WAITING';
    elements.distanceDescription.textContent = 'Waiting for initial sensor reading from ESP32...';
    elements.gaugeFill.style.width = '0%';
    elements.buzzerStateText.textContent = 'Silent (No data received)';
    elements.rhythmVisualizer.className = 'rhythm-visualizer';
  }

  // Update Summary Indicators
  if (ageSeconds !== null && ageSeconds !== undefined) {
    elements.sensorLatencyVal.textContent = `${ageSeconds.toFixed(1)}s ago`;
    elements.lastPingText.textContent = `${ageSeconds.toFixed(1)}s`;
  } else {
    elements.sensorLatencyVal.textContent = '--';
    elements.lastPingText.textContent = '--';
  }

  elements.totalReadingsCount.textContent = state.totalReadingsCount;

  // Update Chart
  if (state.chartInstance && recentReadings && recentReadings.length > 0) {
    elements.chartOverlay.classList.add('hidden');

    const labels = [];
    const distances = [];

    recentReadings.slice(-CONFIG.MAX_CHART_POINTS).forEach(r => {
      // Parse ISO timestamp to local time string HH:MM:SS
      let timeLabel = '';
      try {
        const d = new Date(r.timestamp);
        timeLabel = d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
      } catch (e) {
        timeLabel = r.timestamp.slice(11, 19);
      }

      labels.push(timeLabel);
      distances.push(r.status === 'valid' && r.distance_cm !== null ? r.distance_cm : null);
    });

    state.chartInstance.data.labels = labels;
    state.chartInstance.data.datasets[0].data = distances;
    state.chartInstance.update('none'); // Update without sluggish full animations
  } else if (elements.chartOverlay) {
    elements.chartOverlay.classList.remove('hidden');
  }

  // Update Historical Readings Table
  updateReadingsTable(recentReadings);
}

// Populate the table with recent records
function updateReadingsTable(readings) {
  if (!elements.readingsTbody) return;

  if (!readings || readings.length === 0) {
    elements.readingsTbody.innerHTML = `
      <tr>
        <td colspan="6" class="table-placeholder">No sensor telemetry recorded in database yet.</td>
      </tr>
    `;
    elements.tableRowCount.textContent = '0 records';
    return;
  }

  elements.tableRowCount.textContent = `${readings.length} records`;

  // Display newest rows first for table audit
  const reversed = [...readings].reverse().slice(0, 15);

  const rowsHtml = reversed.map((r, index) => {
    const isLatest = index === 0;
    const isValid = r.status === 'valid';
    const distText = isValid && r.distance_cm !== null ? `${r.distance_cm.toFixed(1)} cm` : 'N/A';
    const statusClass = isValid ? 'pill-valid' : 'pill-unknown';
    const evaluation = evaluateWarningLevel(r.distance_cm, r.status);

    let timeFormatted = r.timestamp;
    try {
      const d = new Date(r.timestamp);
      timeFormatted = d.toISOString().replace('T', ' ').slice(0, 19);
    } catch (e) {}

    return `
      <tr style="${isLatest ? 'background: rgba(56, 189, 248, 0.08);' : ''}">
        <td class="font-mono">#${r.id}</td>
        <td><strong>${escapeHtml(r.device_id)}</strong></td>
        <td class="font-mono">${distText}</td>
        <td><span class="table-pill ${statusClass}">${r.status}</span></td>
        <td><span class="warning-badge ${evaluation.badgeClass}" style="padding: 2px 8px; font-size: 0.72rem;">${evaluation.level}</span></td>
        <td class="font-mono" style="font-size: 0.8rem;">${timeFormatted}</td>
      </tr>
    `;
  }).join('');

  elements.readingsTbody.innerHTML = rowsHtml;
}

// Fetch telemetry data from backend API
async function pollTelemetry() {
  try {
    // 1. Fetch latest reading
    const latestRes = await fetch(`${CONFIG.API_BASE}/api/latest`, { cache: 'no-store' });
    if (!latestRes.ok) throw new Error(`HTTP ${latestRes.status}`);
    const latestData = await latestRes.json();

    // 2. Fetch recent readings
    const readingsRes = await fetch(`${CONFIG.API_BASE}/api/readings?limit=${CONFIG.MAX_CHART_POINTS}`, { cache: 'no-store' });
    if (!readingsRes.ok) throw new Error(`HTTP ${readingsRes.status}`);
    const readingsData = await readingsRes.json();

    state.backendConnected = true;
    state.lastReading = latestData.reading;
    state.lastSuccessfulFetchTime = Date.now();
    
    if (readingsData && readingsData.readings) {
      state.totalReadingsCount = readingsData.count;
      state.readingsHistory = readingsData.readings;
    }

    updateDashboardUI(latestData, state.readingsHistory);
  } catch (err) {
    console.warn('[Dashboard] Telemetry poll failed:', err);
    state.backendConnected = false;
    updateDashboardUI(null, []);
  }
}

// Alert banner helpers
function showAlert(message, isStaleWarning = false) {
  if (!elements.alertBanner) return;
  elements.alertText.textContent = message;
  elements.alertBanner.classList.remove('hidden');
  if (isStaleWarning) {
    elements.alertBanner.classList.add('stale');
    elements.alertIcon.textContent = '⏳';
  } else {
    elements.alertBanner.classList.remove('stale');
    elements.alertIcon.textContent = '⚠️';
  }
}

function hideAlert() {
  if (!elements.alertBanner) return;
  elements.alertBanner.classList.add('hidden');
}

// Utility: Escape HTML to prevent injection
function escapeHtml(str) {
  if (!str) return '';
  return str.replace(/[&<>"']/g, function(m) {
    return {
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      '"': '&quot;',
      "'": '&#39;'
    }[m];
  });
}

// Lifecycle Initialization
document.addEventListener('DOMContentLoaded', () => {
  initChart();

  if (elements.btnRefreshChart) {
    elements.btnRefreshChart.addEventListener('click', () => {
      pollTelemetry();
    });
  }

  // Initial fetch and start periodic polling interval
  pollTelemetry();
  setInterval(pollTelemetry, CONFIG.POLL_INTERVAL_MS);
});
