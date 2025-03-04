class Visualizer:
    def get_dashboard(self, metrics):
        # Return an improved HTML dashboard
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>System Monitor Dashboard</title>
            <style>
                body {{ 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    background-color: #f4f4f4;
                    color: #333;
                }}
                .container {{ 
                    max-width: 900px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    background: #fff; 
                    box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
                    border-radius: 10px;
                }}
                .card {{ 
                    padding: 20px; 
                    margin: 15px 0; 
                    border-radius: 8px;
                    background: #fff;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }}
                h1 {{ text-align: center; }}
                .metrics-grid {{
                    display: grid;
                    grid-template-columns: repeat(3, 1fr);
                    gap: 10px;
                    margin-top: 10px;
                }}
                .metric {{
                    padding: 15px;
                    border-radius: 8px;
                    text-align: center;
                    font-size: 16px;
                    font-weight: bold;
                    color: white;
                }}
                .cpu {{ background: #3498db; }}  /* Blue */
                .memory {{ background: #2ecc71; }}  /* Green */
                .disk {{ background: #e74c3c; }}  /* Red */
                .stock-table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin-top: 10px;
                }}
                .stock-table th, .stock-table td {{
                    border: 1px solid #ddd;
                    padding: 10px;
                    text-align: center;
                }}
                .stock-table th {{
                    background: #2c3e50;
                    color: white;
                }}
                .error {{
                    color: red;
                    font-weight: bold;
                }}
                .nav {{
                    display: flex;
                    justify-content: center;
                    margin-bottom: 20px;
                    background: #2c3e50;
                    padding: 15px;
                    border-radius: 8px;
                }}
                .nav a {{
                    margin: 0 10px;
                    padding: 10px 15px;
                    background: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                    transition: background 0.3s ease;
                }}
                .nav a:hover {{
                    background: #2980b9;
                }}
                .nav a.active {{
                    background: #e74c3c;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>System Monitor Dashboard</h1>
                
                <div class="nav">
                    <a href="/" class="active">Live Dashboard</a>
                    <a href="/history">Historical Data</a>
                </div>

                <!-- System Metrics -->
                <div class="card">
                    <h2>System Metrics</h2>
                    <div class="metrics-grid">
                        <div class="metric cpu" id="cpu">CPU: --%</div>
                        <div class="metric memory" id="memory">Memory: --%</div>
                        <div class="metric disk" id="disk">Disk: --%</div>
                    </div>
                </div>

                <!-- Stock Data -->
                <div class="card">
                    <h2>Stock Data</h2>
                    <table class="stock-table">
                        <thead>
                            <tr>
                                <th>Stock</th>
                                <th>Price ($)</th>
                                <th>Change</th>
                                <th>% Change</th>
                                <th>Volume</th>
                            </tr>
                        </thead>
                        <tbody id="stock-data">
                            {self.render_stock_data(metrics['data'])}
                        </tbody>
                    </table>
                </div>
            </div>

            <script>
                async function fetchMetrics() {{
                    try {{
                        const response = await fetch('/metrics');

                        if (!response.ok) {{
                            throw new Error("Failed to fetch data. Server returned " + response.status);
                        }}

                        const data = await response.json();
                        
                        // Update System Metrics
                        document.getElementById('cpu').textContent = "CPU: " + data.system.cpu.usage_percent + "%";
                        document.getElementById('memory').textContent = "Memory: " + data.system.memory.percent + "%";
                        document.getElementById('disk').textContent = "Disk: " + data.system.disk.percent + "%";

                        // Update Stock Data Table
                        let stocksHtml = "";
                        for (let stock in data.stocks.data) {{
                            let s = data.stocks.data[stock];
                            
                            // Handle undefined or null values
                            const price = s.price !== undefined && s.price !== null ? s.price : 'N/A';
                            const volume = s.volume !== undefined && s.volume !== null ? s.volume : 'N/A';
                            
                            // Format change with color and arrow
                            let changeStyle = '';
                            let changeDisplay = 'N/A';
                            let changePercentDisplay = 'N/A';
                            
                            if (s.change !== undefined && s.change !== null) {{
                                changeStyle = s.change > 0 ? 'color: green;' : s.change < 0 ? 'color: red;' : '';
                                let changeArrow = s.change > 0 ? '▲' : s.change < 0 ? '▼' : '';
                                changeDisplay = s.change != 0 ? changeArrow + ' ' + s.change : "0.00";
                                changePercentDisplay = s.change_percent !== undefined && s.change_percent !== null ? 
                                    s.change_percent + '%' : 'N/A';
                            }}
                            
                            stocksHtml += `
                                <tr>
                                    <td>${{stock}}</td>
                                    <td>${{price}}</td>
                                    <td style="${{changeStyle}}">${{changeDisplay}}</td>
                                    <td style="${{changeStyle}}">${{changePercentDisplay}}</td>
                                    <td>${{volume}}</td>
                                </tr>
                            `;
                        }}
                        document.getElementById('stock-data').innerHTML = stocksHtml;

                    }} catch (error) {{
                        console.error('Error fetching metrics:', error);
                        document.getElementById('cpu').innerHTML = "<span class='error'>Failed</span>";
                        document.getElementById('memory').innerHTML = "<span class='error'>Failed</span>";
                        document.getElementById('disk').innerHTML = "<span class='error'>Failed</span>";
                        document.getElementById('stock-data').innerHTML = "<tr><td colspan='5' class='error'>Failed to load stock data</td></tr>";
                    }}
                }}

                // Fetch data every 5 seconds
                fetchMetrics();
                setInterval(fetchMetrics, 5000);
            </script>
        </body>
        </html>
        """

    def render_stock_data(self, stock_data):
        rows = ""
        for symbol, data in stock_data.items():
            # Handle potential missing or error data
            if not isinstance(data, dict):
                rows += f"""
                <tr>
                    <td>{symbol}</td>
                    <td colspan="4">Error: Invalid data</td>
                </tr>
                """
                continue
                
            # Get values with defaults for missing data
            price = data.get('price', 'N/A')
            volume = data.get('volume', 'N/A')
            
            # Format change with color and arrow
            change = data.get('change')
            change_percent = data.get('change_percent')
            
            if change is None:
                change_display = 'N/A'
                change_percent_display = 'N/A'
                change_color = ''
            else:
                change_color = 'color: green;' if change > 0 else 'color: red;' if change < 0 else ''
                change_arrow = '▲' if change > 0 else '▼' if change < 0 else ''
                change_display = f"{change_arrow} {change}" if change != 0 else "0.00"
                change_percent_display = f"{change_percent}%" if change_percent is not None else 'N/A'
            
            rows += f"""
            <tr>
                <td>{symbol}</td>
                <td>{price}</td>
                <td style="{change_color}">{change_display}</td>
                <td style="{change_color}">{change_percent_display}</td>
                <td>{volume}</td>
            </tr>
            """
        return rows
        
    def get_history_dashboard(self):
        """Return a dashboard for historical data visualization."""
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Historical Metrics Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { 
                    font-family: Arial, sans-serif; 
                    margin: 20px; 
                    background-color: #f4f4f4;
                    color: #333;
                }
                .container { 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    padding: 20px; 
                    background: #fff; 
                    box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
                    border-radius: 10px;
                }
                .card { 
                    padding: 20px; 
                    margin: 15px 0; 
                    border-radius: 8px;
                    background: #fff;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                h1, h2 { text-align: center; }
                .chart-container {
                    position: relative;
                    height: 300px;
                    width: 100%;
                    margin-top: 20px;
                }
                .controls {
                    display: flex;
                    justify-content: space-between;
                    margin-bottom: 20px;
                    flex-wrap: wrap;
                }
                .control-group {
                    margin: 10px;
                }
                select, button {
                    padding: 8px 12px;
                    border-radius: 4px;
                    border: 1px solid #ddd;
                    background: white;
                    font-size: 14px;
                }
                button {
                    background: #3498db;
                    color: white;
                    border: none;
                    cursor: pointer;
                }
                button:hover {
                    background: #2980b9;
                }
                .nav {
                    display: flex;
                    justify-content: center;
                    margin-bottom: 20px;
                }
                .nav a {
                    margin: 0 10px;
                    padding: 10px 15px;
                    background: #3498db;
                    color: white;
                    text-decoration: none;
                    border-radius: 5px;
                    font-weight: bold;
                }
                .nav a:hover {
                    background: #2980b9;
                }
                .tab-container {
                    margin-top: 20px;
                }
                .tab-buttons {
                    display: flex;
                    border-bottom: 1px solid #ddd;
                }
                .tab-button {
                    padding: 10px 20px;
                    background: #f1f1f1;
                    border: none;
                    border-radius: 5px 5px 0 0;
                    margin-right: 5px;
                    cursor: pointer;
                }
                .tab-button.active {
                    background: #3498db;
                    color: white;
                }
                .tab-content {
                    display: none;
                    padding: 20px;
                    border: 1px solid #ddd;
                    border-top: none;
                }
                .tab-content.active {
                    display: block;
                }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>Historical Metrics Dashboard</h1>
                
                <div class="nav">
                    <a href="/">Live Dashboard</a>
                    <a href="/history" class="active">Historical Data</a>
                </div>
                
                <div class="tab-container">
                    <div class="tab-buttons">
                        <button class="tab-button active" onclick="openTab(event, 'system-tab')">System Metrics</button>
                        <button class="tab-button" onclick="openTab(event, 'stock-tab')">Stock Metrics</button>
                        <button class="tab-button" onclick="openTab(event, 'custom-tab')">Custom Query</button>
                    </div>
                    
                    <!-- System Metrics Tab -->
                    <div id="system-tab" class="tab-content active">
                        <div class="card">
                            <h2>System Metrics History</h2>
                            
                            <div class="controls">
                                <div class="control-group">
                                    <label for="system-timerange">Time Range:</label>
                                    <select id="system-timerange">
                                        <option value="24h">Last 24 Hours</option>
                                        <option value="7d" selected>Last 7 Days</option>
                                        <option value="30d">Last 30 Days</option>
                                    </select>
                                </div>
                                
                                <div class="control-group">
                                    <label for="system-interval">Interval:</label>
                                    <select id="system-interval">
                                        <option value="hour">Hourly</option>
                                        <option value="day" selected>Daily</option>
                                        <option value="week">Weekly</option>
                                    </select>
                                </div>
                                
                                <div class="control-group">
                                    <label for="system-metric">Metric:</label>
                                    <select id="system-metric">
                                        <option value="CPU Usage" selected>CPU Usage</option>
                                        <option value="Memory Usage">Memory Usage</option>
                                        <option value="Disk Usage">Disk Usage</option>
                                        <option value="Running Processes">Running Processes</option>
                                        <option value="Thread Count">Thread Count</option>
                                    </select>
                                </div>
                                
                                <div class="control-group">
                                    <button onclick="updateSystemChart()">Update Chart</button>
                                </div>
                            </div>
                            
                            <div class="chart-container">
                                <canvas id="systemChart"></canvas>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Stock Metrics Tab -->
                    <div id="stock-tab" class="tab-content">
                        <div class="card">
                            <h2>Stock Metrics History</h2>
                            
                            <div class="controls">
                                <div class="control-group">
                                    <label for="stock-symbol">Symbol:</label>
                                    <select id="stock-symbol">
                                        <!-- Will be populated dynamically -->
                                    </select>
                                </div>
                                
                                <div class="control-group">
                                    <label for="stock-timerange">Time Range:</label>
                                    <select id="stock-timerange">
                                        <option value="24h">Last 24 Hours</option>
                                        <option value="7d" selected>Last 7 Days</option>
                                        <option value="30d">Last 30 Days</option>
                                    </select>
                                </div>
                                
                                <div class="control-group">
                                    <label for="stock-interval">Interval:</label>
                                    <select id="stock-interval">
                                        <option value="hour">Hourly</option>
                                        <option value="day" selected>Daily</option>
                                        <option value="week">Weekly</option>
                                    </select>
                                </div>
                                
                                <div class="control-group">
                                    <label for="stock-metric">Metric:</label>
                                    <select id="stock-metric">
                                        <option value="Price" selected>Price</option>
                                        <option value="Volume">Volume</option>
                                        <option value="Change">Change</option>
                                        <option value="Change Percent">Change Percent</option>
                                        <option value="Market Cap">Market Cap</option>
                                    </select>
                                </div>
                                
                                <div class="control-group">
                                    <button onclick="updateStockChart()">Update Chart</button>
                                </div>
                            </div>
                            
                            <div class="chart-container">
                                <canvas id="stockChart"></canvas>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Custom Query Tab -->
                    <div id="custom-tab" class="tab-content">
                        <div class="card">
                            <h2>Custom Metric Query</h2>
                            
                            <div class="controls">
                                <div class="control-group">
                                    <label for="custom-device">Device:</label>
                                    <select id="custom-device">
                                        <!-- Will be populated dynamically -->
                                    </select>
                                </div>
                                
                                <div class="control-group">
                                    <label for="custom-metric">Metric:</label>
                                    <select id="custom-metric">
                                        <!-- Will be populated dynamically -->
                                    </select>
                                </div>
                                
                                <div class="control-group">
                                    <label for="custom-timerange">Time Range:</label>
                                    <select id="custom-timerange">
                                        <option value="24h">Last 24 Hours</option>
                                        <option value="7d" selected>Last 7 Days</option>
                                        <option value="30d">Last 30 Days</option>
                                        <option value="custom">Custom Range</option>
                                    </select>
                                </div>
                                
                                <div class="control-group" id="custom-date-range" style="display: none;">
                                    <label for="custom-start-date">Start Date:</label>
                                    <input type="datetime-local" id="custom-start-date">
                                    <label for="custom-end-date">End Date:</label>
                                    <input type="datetime-local" id="custom-end-date">
                                </div>
                                
                                <div class="control-group">
                                    <label for="custom-aggregate">Aggregate Data:</label>
                                    <input type="checkbox" id="custom-aggregate" checked>
                                </div>
                                
                                <div class="control-group" id="custom-interval-group">
                                    <label for="custom-interval">Interval:</label>
                                    <select id="custom-interval">
                                        <option value="hour">Hourly</option>
                                        <option value="day" selected>Daily</option>
                                        <option value="week">Weekly</option>
                                    </select>
                                </div>
                                
                                <div class="control-group">
                                    <button onclick="updateCustomChart()">Update Chart</button>
                                </div>
                            </div>
                            
                            <div class="chart-container">
                                <canvas id="customChart"></canvas>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <script>
                // Global chart objects
                let systemChart = null;
                let stockChart = null;
                let customChart = null;
                
                // Initialize the page
                document.addEventListener('DOMContentLoaded', function() {
                    // Load available stock symbols
                    loadStockSymbols();
                    
                    // Load devices and metrics for custom query
                    loadDevices();
                    
                    // Initialize charts
                    updateSystemChart();
                    // Stock chart will be initialized after symbols are loaded
                    
                    // Set up custom date range toggle
                    document.getElementById('custom-timerange').addEventListener('change', function() {
                        const customDateRange = document.getElementById('custom-date-range');
                        if (this.value === 'custom') {
                            customDateRange.style.display = 'block';
                        } else {
                            customDateRange.style.display = 'none';
                        }
                    });
                    
                    // Set up aggregate toggle
                    document.getElementById('custom-aggregate').addEventListener('change', function() {
                        const intervalGroup = document.getElementById('custom-interval-group');
                        if (this.checked) {
                            intervalGroup.style.display = 'block';
                        } else {
                            intervalGroup.style.display = 'none';
                        }
                    });
                });
                
                // Tab functionality
                function openTab(evt, tabName) {
                    // Hide all tab content
                    const tabContents = document.getElementsByClassName('tab-content');
                    for (let i = 0; i < tabContents.length; i++) {
                        tabContents[i].classList.remove('active');
                    }
                    
                    // Remove active class from all tab buttons
                    const tabButtons = document.getElementsByClassName('tab-button');
                    for (let i = 0; i < tabButtons.length; i++) {
                        tabButtons[i].classList.remove('active');
                    }
                    
                    // Show the selected tab and mark its button as active
                    document.getElementById(tabName).classList.add('active');
                    evt.currentTarget.classList.add('active');
                }
                
                // Load available stock symbols
                async function loadStockSymbols() {
                    try {
                        const response = await fetch('/api/devices');
                        if (!response.ok) {
                            throw new Error("Failed to fetch devices");
                        }
                        
                        const devices = await response.json();
                        const stockSymbols = devices
                            .filter(device => device.name.startsWith('Stock-'))
                            .map(device => device.name.replace('Stock-', ''));
                        
                        const symbolSelect = document.getElementById('stock-symbol');
                        symbolSelect.innerHTML = ''; // Clear existing options
                        
                        stockSymbols.forEach(symbol => {
                            const option = document.createElement('option');
                            option.value = symbol;
                            option.textContent = symbol;
                            symbolSelect.appendChild(option);
                        });
                        
                        // Initialize stock chart with the first symbol if available
                        if (stockSymbols.length > 0) {
                            updateStockChart();
                        }
                        
                    } catch (error) {
                        console.error('Error loading stock symbols:', error);
                    }
                }
                
                // Load available devices for custom query
                async function loadDevices() {
                    try {
                        const response = await fetch('/api/devices');
                        if (!response.ok) {
                            throw new Error("Failed to fetch devices");
                        }
                        
                        const devices = await response.json();
                        const deviceSelect = document.getElementById('custom-device');
                        deviceSelect.innerHTML = ''; // Clear existing options
                        
                        devices.forEach(device => {
                            const option = document.createElement('option');
                            option.value = device.name;
                            option.textContent = device.name;
                            deviceSelect.appendChild(option);
                        });
                        
                        // Load metrics for the first device
                        if (devices.length > 0) {
                            loadMetrics(devices[0].name);
                            deviceSelect.addEventListener('change', function() {
                                loadMetrics(this.value);
                            });
                        }
                        
                    } catch (error) {
                        console.error('Error loading devices:', error);
                    }
                }
                
                // Load available metrics for a device
                async function loadMetrics(deviceName) {
                    try {
                        const response = await fetch('/api/metrics');
                        if (!response.ok) {
                            throw new Error("Failed to fetch metrics");
                        }
                        
                        const metrics = await response.json();
                        const metricSelect = document.getElementById('custom-metric');
                        metricSelect.innerHTML = ''; // Clear existing options
                        
                        metrics.forEach(metric => {
                            const option = document.createElement('option');
                            option.value = metric.name;
                            option.textContent = metric.name;
                            metricSelect.appendChild(option);
                        });
                        
                    } catch (error) {
                        console.error('Error loading metrics:', error);
                    }
                }
                
                // Helper function to get date range
                function getDateRange(rangeValue) {
                    const now = new Date();
                    let startDate = new Date();
                    
                    if (rangeValue === '24h') {
                        startDate.setHours(startDate.getHours() - 24);
                    } else if (rangeValue === '7d') {
                        startDate.setDate(startDate.getDate() - 7);
                    } else if (rangeValue === '30d') {
                        startDate.setDate(startDate.getDate() - 30);
                    }
                    
                    return {
                        start: startDate.toISOString().split('.')[0].replace('T', ' '),
                        end: now.toISOString().split('.')[0].replace('T', ' ')
                    };
                }
                
                // Update system metrics chart
                async function updateSystemChart() {
                    const timeRange = document.getElementById('system-timerange').value;
                    const interval = document.getElementById('system-interval').value;
                    const metricName = document.getElementById('system-metric').value;
                    
                    try {
                        const dateRange = getDateRange(timeRange);
                        const url = `/api/device/PC/metric/${metricName}/history?start_time=${dateRange.start}&end_time=${dateRange.end}&interval=${interval}&aggregate=true`;
                        
                        const response = await fetch(url);
                        if (!response.ok) {
                            throw new Error("Failed to fetch system metrics");
                        }
                        
                        const data = await response.json();
                        
                        // Process data for the chart
                        const labels = data.map(item => item.time_bucket);
                        const avgValues = data.map(item => item.avg_value);
                        const minValues = data.map(item => item.min_value);
                        const maxValues = data.map(item => item.max_value);
                        
                        // Create or update the chart
                        const ctx = document.getElementById('systemChart').getContext('2d');
                        
                        if (systemChart) {
                            systemChart.destroy();
                        }
                        
                        systemChart = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: labels,
                                datasets: [
                                    {
                                        label: `Avg ${metricName}`,
                                        data: avgValues,
                                        borderColor: '#3498db',
                                        backgroundColor: 'rgba(52, 152, 219, 0.1)',
                                        borderWidth: 2,
                                        fill: false,
                                        tension: 0.1
                                    },
                                    {
                                        label: `Min ${metricName}`,
                                        data: minValues,
                                        borderColor: '#2ecc71',
                                        backgroundColor: 'rgba(46, 204, 113, 0.1)',
                                        borderWidth: 1,
                                        fill: false,
                                        tension: 0.1
                                    },
                                    {
                                        label: `Max ${metricName}`,
                                        data: maxValues,
                                        borderColor: '#e74c3c',
                                        backgroundColor: 'rgba(231, 76, 60, 0.1)',
                                        borderWidth: 1,
                                        fill: false,
                                        tension: 0.1
                                    }
                                ]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: {
                                    y: {
                                        beginAtZero: true
                                    }
                                }
                            }
                        });
                        
                    } catch (error) {
                        console.error('Error updating system chart:', error);
                    }
                }
                
                // Update stock metrics chart
                async function updateStockChart() {
                    const symbol = document.getElementById('stock-symbol').value;
                    const timeRange = document.getElementById('stock-timerange').value;
                    const interval = document.getElementById('stock-interval').value;
                    const metricName = document.getElementById('stock-metric').value;
                    
                    if (!symbol) return;
                    
                    try {
                        const dateRange = getDateRange(timeRange);
                        const url = `/api/device/Stock-${symbol}/metric/${metricName}/history?start_time=${dateRange.start}&end_time=${dateRange.end}&interval=${interval}&aggregate=true`;
                        
                        const response = await fetch(url);
                        if (!response.ok) {
                            throw new Error("Failed to fetch stock metrics");
                        }
                        
                        const data = await response.json();
                        
                        // Process data for the chart
                        const labels = data.map(item => item.time_bucket);
                        const avgValues = data.map(item => item.avg_value);
                        
                        // Create or update the chart
                        const ctx = document.getElementById('stockChart').getContext('2d');
                        
                        if (stockChart) {
                            stockChart.destroy();
                        }
                        
                        stockChart = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: labels,
                                datasets: [{
                                    label: `${symbol} ${metricName}`,
                                    data: avgValues,
                                    borderColor: '#2ecc71',
                                    backgroundColor: 'rgba(46, 204, 113, 0.1)',
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.1
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: {
                                    y: {
                                        beginAtZero: false
                                    }
                                }
                            }
                        });
                        
                    } catch (error) {
                        console.error('Error updating stock chart:', error);
                    }
                }
                
                // Update custom metrics chart
                async function updateCustomChart() {
                    const deviceName = document.getElementById('custom-device').value;
                    const metricName = document.getElementById('custom-metric').value;
                    const timeRangeType = document.getElementById('custom-timerange').value;
                    const aggregate = document.getElementById('custom-aggregate').checked;
                    const interval = document.getElementById('custom-interval').value;
                    
                    let startTime, endTime;
                    
                    if (timeRangeType === 'custom') {
                        startTime = document.getElementById('custom-start-date').value.replace('T', ' ');
                        endTime = document.getElementById('custom-end-date').value.replace('T', ' ');
                    } else {
                        const dateRange = getDateRange(timeRangeType);
                        startTime = dateRange.start;
                        endTime = dateRange.end;
                    }
                    
                    try {
                        const url = `/api/device/${deviceName}/metric/${metricName}/history?start_time=${startTime}&end_time=${endTime}&interval=${interval}&aggregate=${aggregate}`;
                        
                        const response = await fetch(url);
                        if (!response.ok) {
                            throw new Error("Failed to fetch custom metrics");
                        }
                        
                        const data = await response.json();
                        
                        // Process data for the chart
                        let labels, values;
                        
                        if (aggregate) {
                            labels = data.map(item => item.time_bucket);
                            values = data.map(item => item.avg_value);
                        } else {
                            labels = data.map(item => item.timestamp);
                            values = data.map(item => item.value);
                        }
                        
                        // Create or update the chart
                        const ctx = document.getElementById('customChart').getContext('2d');
                        
                        if (customChart) {
                            customChart.destroy();
                        }
                        
                        customChart = new Chart(ctx, {
                            type: 'line',
                            data: {
                                labels: labels,
                                datasets: [{
                                    label: `${deviceName} - ${metricName}`,
                                    data: values,
                                    borderColor: '#9b59b6',
                                    backgroundColor: 'rgba(155, 89, 182, 0.1)',
                                    borderWidth: 2,
                                    fill: true,
                                    tension: 0.1
                                }]
                            },
                            options: {
                                responsive: true,
                                maintainAspectRatio: false,
                                scales: {
                                    y: {
                                        beginAtZero: false
                                    }
                                }
                            }
                        });
                        
                    } catch (error) {
                        console.error('Error updating custom chart:', error);
                    }
                }
            </script>
        </body>
        </html>
        """