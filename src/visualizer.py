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
            </style>
        </head>
        <body>
            <div class="container">
                <h1>System Monitor Dashboard</h1>

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
                            stocksHtml += `
                                <tr>
                                    <td>${{stock}}</td>
                                    <td>${{s.price}}</td>
                                    <td>${{s.change}}</td>
                                    <td>${{s.change_percent}}%</td>
                                    <td>${{s.volume}}</td>
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
            rows += f"""
            <tr>
                <td>{symbol}</td>
                <td>{data.get('price', 'N/A')}</td>
                <td>{data.get('change', 'N/A')}</td>
                <td>{data.get('change_percent', 'N/A')}%</td>
                <td>{data.get('volume', 'N/A')}</td>
            </tr>
            """
        return rows