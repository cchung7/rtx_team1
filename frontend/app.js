// CLAP Dashboard Application
// Handles data fetching, visualization, and user interactions

// API Configuration
const API_BASE_URL = 'http://localhost:5001/api';

// EPA AQI Categories with colors (WCAG 2.1 Level AA compliant)
const AQI_CATEGORIES = {
    'Good': { range: [0, 50], color: '#00E400', textColor: '#000000' },
    'Moderate': { range: [51, 100], color: '#FFFF00', textColor: '#000000' },
    'Unhealthy for Sensitive Groups': { range: [101, 150], color: '#FF7E00', textColor: '#000000' },
    'Unhealthy': { range: [151, 200], color: '#FF0000', textColor: '#FFFFFF' },
    'Very Unhealthy': { range: [201, 300], color: '#8F3F97', textColor: '#FFFFFF' },
    'Hazardous': { range: [301, 500], color: '#7E0023', textColor: '#FFFFFF' }
};

// Global state
let currentCounty = null;
let currentState = null;
let currentModel = 'balanced';
let aqiChart = null;

// DOM Elements
const modelSelect = document.getElementById('model-select');
const countySelect = document.getElementById('county-select');
const forecastDaysSelect = document.getElementById('forecast-days');
const refreshBtn = document.getElementById('refresh-btn');
const loadBtn = document.getElementById('load-btn');
const loadingSpinner = document.getElementById('loading');
const errorMessage = document.getElementById('error-message');
const predictionSection = document.getElementById('prediction-section');
const chartSection = document.getElementById('chart-section');

// Utility Functions
function showLoading(show = true) {
    if (show) {
        loadingSpinner.classList.add('show');
    } else {
        loadingSpinner.classList.remove('show');
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.add('show');
    setTimeout(() => {
        errorMessage.classList.remove('show');
    }, 5000);
}

function hideError() {
    errorMessage.classList.remove('show');
}

function getCategoryForAQI(aqi) {
    for (const [category, data] of Object.entries(AQI_CATEGORIES)) {
        if (aqi >= data.range[0] && aqi <= data.range[1]) {
            return category;
        }
    }
    return aqi > 500 ? 'Hazardous' : 'Unknown';
}

function getCategoryClass(category) {
    const classMap = {
        'Good': 'aqi-good',
        'Moderate': 'aqi-moderate',
        'Unhealthy for Sensitive Groups': 'aqi-unhealthy-sensitive',
        'Unhealthy': 'aqi-unhealthy',
        'Very Unhealthy': 'aqi-very-unhealthy',
        'Hazardous': 'aqi-hazardous'
    };
    return classMap[category] || '';
}

function getCategoryColor(category) {
    const colorMap = {
        'Good': '#00E400',
        'Moderate': '#FFFF00',
        'Unhealthy for Sensitive Groups': '#FF7E00',
        'Unhealthy': '#FF0000',
        'Very Unhealthy': '#8F3F97',
        'Hazardous': '#7E0023'
    };
    return colorMap[category] || '#6B7280';
}

// API Functions
async function fetchCounties() {
    try {
        const response = await fetch(`${API_BASE_URL}/counties`);
        const data = await response.json();
        
        if (data.success) {
            populateCountySelect(data.counties);
        } else {
            showError('Failed to load counties: ' + data.error);
        }
    } catch (error) {
        showError('Error loading counties: ' + error.message);
        console.error('Error fetching counties:', error);
    }
}

async function fetchHistoricalData(county, state, days = 30) {
    try {
        const response = await fetch(
            `${API_BASE_URL}/aqi/historical?county=${encodeURIComponent(county)}&state=${encodeURIComponent(state)}&days=${days}`
        );
        const data = await response.json();
        
        if (data.success) {
            return data.data;
        } else {
            throw new Error(data.error || 'Failed to fetch historical data');
        }
    } catch (error) {
        throw error;
    }
}

async function fetchPrediction(county, state, days = 1) {
    try {
        const response = await fetch(`${API_BASE_URL}/aqi/predict`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ county, state, model: currentModel, days: days })
        });
        const data = await response.json();
        
        if (data.success) {
            // Return the entire response for proper handling
            return data;
        } else {
            throw new Error(data.error || 'Failed to generate prediction');
        }
    } catch (error) {
        throw error;
    }
}

// UI Update Functions
function populateCountySelect(counties) {
    countySelect.innerHTML = '<option value="">-- Select a County --</option>';
    
    counties.forEach(county => {
        const option = document.createElement('option');
        option.value = JSON.stringify({ county: county.county, state: county.state });
        option.textContent = county.display_name;
        countySelect.appendChild(option);
    });
}

function displayPrediction(prediction, forecastDate) {
    // Update predicted AQI value
    document.getElementById('predicted-aqi').textContent = Math.round(prediction.predicted_aqi);
    
    // Update category
    const categoryElement = document.getElementById('predicted-category');
    categoryElement.textContent = prediction.predicted_category;
    
    // Apply category color
    const categoryClass = getCategoryClass(prediction.predicted_category);
    categoryElement.className = 'prediction-category ' + categoryClass;
    
    // Update forecast date
    document.getElementById('forecast-date').textContent = 
        `Forecast for: ${forecastDate}`;
    
    // Display probabilities
    displayProbabilities(prediction.probabilities);
    
    // Show prediction section
    predictionSection.style.display = 'block';
}

function displayProbabilities(probabilities) {
    const probabilitiesList = document.getElementById('probabilities-list');
    probabilitiesList.innerHTML = '';
    
    // Sort categories by probability (descending)
    const sortedProbs = Object.entries(probabilities)
        .sort((a, b) => b[1] - a[1]);
    
    sortedProbs.forEach(([category, probability]) => {
        const percentage = (probability * 100).toFixed(1);
        const categoryClass = getCategoryClass(category);
        
        const item = document.createElement('div');
        item.className = 'probability-item';
        item.innerHTML = `
            <div class="probability-label">${category}</div>
            <div class="probability-bar-container">
                <div class="probability-bar ${categoryClass}" 
                     style="width: ${percentage}%"
                     role="progressbar"
                     aria-valuenow="${percentage}"
                     aria-valuemin="0"
                     aria-valuemax="100"
                     aria-label="${category} probability">
                    ${percentage}%
                </div>
            </div>
        `;
        
        probabilitiesList.appendChild(item);
    });
}

function createChart(historicalData, prediction = null) {
    const ctx = document.getElementById('aqi-chart').getContext('2d');
    
    // Prepare data
    const dates = historicalData.map(d => d.date);
    const aqiValues = historicalData.map(d => d.aqi);
    
    // Add prediction as future point if available
    if (prediction) {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        dates.push(tomorrow.toISOString().split('T')[0]);
        aqiValues.push(Math.round(prediction.predicted_aqi));
    }
    
    // Calculate background colors based on AQI category
    const backgroundColors = aqiValues.map(aqi => {
        const category = getCategoryForAQI(aqi);
        return AQI_CATEGORIES[category]?.color || '#cccccc';
    });
    
    // Destroy existing chart if it exists
    if (aqiChart) {
        aqiChart.destroy();
    }
    
    // Create new chart
    aqiChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'AQI Value',
                data: aqiValues,
                borderColor: '#2563eb',
                backgroundColor: 'rgba(37, 99, 235, 0.1)',
                pointBackgroundColor: backgroundColors,
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 6,
                pointHoverRadius: 8,
                tension: 0.3,
                fill: true
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                    labels: {
                        font: {
                            size: 14
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const aqi = context.parsed.y;
                            const category = getCategoryForAQI(aqi);
                            return [`AQI: ${aqi}`, `Category: ${category}`];
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 200,
                    title: {
                        display: true,
                        text: 'AQI Value',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.05)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date',
                        font: {
                            size: 14,
                            weight: 'bold'
                        }
                    },
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
    
    // Display statistics
    displayChartStatistics(aqiValues.slice(0, -1)); // Exclude prediction from stats
    
    // Show chart section
    chartSection.style.display = 'block';
}

function displayChartStatistics(aqiValues) {
    const avg = aqiValues.reduce((a, b) => a + b, 0) / aqiValues.length;
    const min = Math.min(...aqiValues);
    const max = Math.max(...aqiValues);
    const latest = aqiValues[aqiValues.length - 1];
    
    const statsContainer = document.getElementById('chart-stats');
    statsContainer.innerHTML = `
        <div class="stat-item">
            <div class="stat-label">Average AQI</div>
            <div class="stat-value">${Math.round(avg)}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Minimum AQI</div>
            <div class="stat-value">${min}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Maximum AQI</div>
            <div class="stat-value">${max}</div>
        </div>
        <div class="stat-item">
            <div class="stat-label">Latest AQI</div>
            <div class="stat-value">${latest}</div>
        </div>
    `;
}

// Event Handlers
async function handleLoadData() {
    const selectedValue = countySelect.value;
    
    if (!selectedValue) {
        showError('Please select a county first');
        return;
    }
    
    const { county, state } = JSON.parse(selectedValue);
    currentCounty = county;
    currentState = state;
    
    showLoading(true);
    hideError();
    
    try {
        // Fetch historical data
        const historicalData = await fetchHistoricalData(county, state, 30);
        
        if (historicalData.length === 0) {
            showError(`No historical data available for ${county}, ${state}`);
            showLoading(false);
            return;
        }
        
        // Create chart without prediction
        createChart(historicalData);
        
        showLoading(false);
    } catch (error) {
        showError('Error loading data: ' + error.message);
        showLoading(false);
        console.error('Error:', error);
    }
}

async function handleRefresh() {
    const selectedValue = countySelect.value;
    
    if (!selectedValue) {
        showError('Please select a county first');
        return;
    }
    
    const { county, state } = JSON.parse(selectedValue);
    currentCounty = county;
    currentState = state;
    
    const forecastDays = parseInt(forecastDaysSelect.value);
    
    showLoading(true);
    hideError();
    
    try {
        // Fetch both historical data and prediction
        const [historicalData, prediction] = await Promise.all([
            fetchHistoricalData(county, state, 30),
            fetchPrediction(county, state, forecastDays)
        ]);
        
        if (historicalData.length === 0) {
            showError(`No historical data available for ${county}, ${state}`);
            showLoading(false);
            return;
        }
        
        // Display prediction
        const forecastTitle = document.getElementById('forecast-title');
        let chartPrediction; // Declare variable for chart creation
        
        if (forecastDays === 1) {
            // Single day forecast
            const singlePrediction = prediction.prediction || prediction;
            const forecastDate = singlePrediction.forecast_date || 
                new Date(Date.now() + 86400000).toISOString().split('T')[0];
            forecastTitle.textContent = 'Next-Day AQI Prediction';
            displayPrediction(singlePrediction, forecastDate);
            document.getElementById('multi-day-section').style.display = 'none';
            document.getElementById('prediction-section').style.display = 'block';
            chartPrediction = singlePrediction;
        } else {
            // Multi-day forecast
            forecastTitle.textContent = `Multi-Day AQI Forecast (${forecastDays} days)`;
            displayMultiDayForecast(prediction.predictions, forecastDays);
            document.getElementById('multi-day-section').style.display = 'block';
            document.getElementById('prediction-section').style.display = 'none';
            // For multi-day, use the first prediction for the main chart
            chartPrediction = prediction.predictions[0];
        }
        
        // Create chart with prediction
        createChart(historicalData, chartPrediction);
        
        showLoading(false);
    } catch (error) {
        showError('Error refreshing data: ' + error.message);
        showLoading(false);
        console.error('Error:', error);
    }
}

// Display multi-day forecast
function displayMultiDayForecast(predictions, days) {
    // Check if predictions is valid
    if (!predictions || !Array.isArray(predictions) || predictions.length === 0) {
        console.error('Invalid predictions data:', predictions);
        showError('No prediction data available for multi-day forecast');
        return;
    }
    
    // Update multi-day title
    document.getElementById('multi-day-title').textContent = `${days}-Day AQI Forecast`;
    
    // Create multi-day chart
    createMultiDayChart(predictions, days);
    
    // Update summary
    updateForecastSummary(predictions, days);
}

// Create multi-day forecast chart
function createMultiDayChart(predictions, days) {
    const ctx = document.getElementById('multi-day-chart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (window.multiDayChart) {
        window.multiDayChart.destroy();
    }
    
    // Prepare data
    const dates = [];
    const aqiValues = [];
    const categories = [];
    
    for (let i = 0; i < predictions.length; i++) {
        const date = new Date();
        date.setDate(date.getDate() + i + 1);
        dates.push(date.toLocaleDateString());
        aqiValues.push(predictions[i].predicted_aqi);
        categories.push(predictions[i].predicted_category);
    }
    
    // Create chart
    window.multiDayChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'Predicted AQI',
                data: aqiValues,
                borderColor: '#4F46E5',
                backgroundColor: 'rgba(79, 70, 229, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: aqiValues.map(aqi => getCategoryColor(getCategoryForAQI(aqi))),
                pointBorderColor: '#fff',
                pointBorderWidth: 2,
                pointRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `${days}-Day AQI Forecast`,
                    font: { size: 18, weight: 'bold' }
                },
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: Math.max(...aqiValues) * 1.2,
                    title: {
                        display: true,
                        text: 'AQI Value'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                },
                x: {
                    title: {
                        display: true,
                        text: 'Date'
                    },
                    grid: {
                        color: 'rgba(0, 0, 0, 0.1)'
                    }
                }
            }
        }
    });
}

// Update forecast summary
function updateForecastSummary(predictions, days) {
    const summary = document.getElementById('multi-day-summary');
    
    const avgAQI = predictions.reduce((sum, p) => sum + p.predicted_aqi, 0) / predictions.length;
    const minAQI = Math.min(...predictions.map(p => p.predicted_aqi));
    const maxAQI = Math.max(...predictions.map(p => p.predicted_aqi));
    
    // Count categories
    const categoryCounts = {};
    predictions.forEach(p => {
        categoryCounts[p.predicted_category] = (categoryCounts[p.predicted_category] || 0) + 1;
    });
    
    const mostCommonCategory = Object.keys(categoryCounts).reduce((a, b) => 
        categoryCounts[a] > categoryCounts[b] ? a : b
    );
    
    summary.innerHTML = `
        <div class="forecast-stats">
            <div class="stat-item">
                <span class="stat-label">Average AQI:</span>
                <span class="stat-value">${Math.round(avgAQI)}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Range:</span>
                <span class="stat-value">${Math.round(minAQI)} - ${Math.round(maxAQI)}</span>
            </div>
            <div class="stat-item">
                <span class="stat-label">Most Common:</span>
                <span class="stat-value ${getCategoryClass(mostCommonCategory)}">${mostCommonCategory}</span>
            </div>
        </div>
    `;
}

// Handle model selection change
function handleModelChange() {
    currentModel = modelSelect.value;
    console.log(`Model changed to: ${currentModel}`);
    
    // Update model information display
    updateModelInfo();
    
    // If we have a county selected, refresh the prediction
    if (currentCounty && currentState) {
        handleRefresh();
    }
}

// Update model information display
async function updateModelInfo() {
    try {
        const response = await fetch(`${API_BASE_URL}/model/metrics?model=${currentModel}`);
        const data = await response.json();
        
        if (data.success) {
            const metrics = data.metrics;
            document.getElementById('model-mse').textContent = metrics.mse.toFixed(2);
            document.getElementById('model-rmse').textContent = `~${Math.round(metrics.rmse)} AQI units`;
            document.getElementById('model-r2').textContent = metrics.r2.toFixed(2);
        }
    } catch (error) {
        console.error('Error fetching model metrics:', error);
    }
}

// Initialize Application
async function initializeApp() {
    console.log('Initializing CLAP Dashboard...');
    
    // Attach event listeners
    modelSelect.addEventListener('change', handleModelChange);
    refreshBtn.addEventListener('click', handleRefresh);
    loadBtn.addEventListener('click', handleLoadData);
    
    // Load counties and model info on startup
    try {
        await fetchCounties();
        await updateModelInfo();
        console.log('Dashboard initialized successfully');
    } catch (error) {
        console.error('Failed to initialize dashboard:', error);
        showError('Failed to initialize dashboard. Please refresh the page.');
    }
}

// Start the application when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeApp);
} else {
    initializeApp();
}

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        getCategoryForAQI,
        getCategoryClass,
        AQI_CATEGORIES
    };
}

