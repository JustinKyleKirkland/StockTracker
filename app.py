import dash
from dash import dcc, html, no_update
from dash.dependencies import Input, Output, State, MATCH, ALL
import plotly.graph_objs as go
import plotly.express as px
import pandas as pd
import datetime as dt
import os

from stock_data import get_stock_data, get_multiple_stock_data, get_stock_info
from portfolio import Portfolio
from news import get_stock_news

# Initialize the Dash app with assets folder for custom CSS
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    assets_folder='assets',  # Look for custom CSS in the assets folder
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
    # Load enhanced charts.js instead of charts.js
    # This is a workaround for the issue with modifying charts.js
    external_scripts=[
        {"src": "/assets/enhanced_charts.js"}
    ]
)
app.title = "Stock Tracker"

# Create a Portfolio instance
portfolio = Portfolio()

# Define the layout
app.layout = html.Div([
    # Header section
    html.Div([
        html.H1("Stock Tracker", className="app-header-title"),
        # Dark mode toggle button (will be styled via JavaScript)
        html.Button("🌙", id="dark-mode-toggle", className="dark-mode-toggle", title="Toggle dark/light mode"),
    ], className="app-header"),
    
    # Tabs for different sections
    dcc.Tabs(id="tabs", value="tab-1", className="dash-tabs", children=[
        # Tab for stock visualization
        dcc.Tab(label="Stock Visualization", value="tab-1", className="dash-tab", children=[
            html.Div([
                html.Div([
                    html.H3("Stock Symbol", className="card-header"),
                    html.Div([
                        dcc.Input(
                            id="stock-input",
                            type="text",
                            value="AAPL",
                            placeholder="Enter a stock symbol (e.g., AAPL)",
                            className="form-control",
                        ),
                        html.Button("Submit", id="submit-button", n_clicks=0),
                    ], className="form-group"),
                ], className="card"),
                
                html.Div([
                    html.Div([
                        html.Div([
                            html.H3("Time Period", className="card-header"),
                            dcc.Dropdown(
                                id="time-period",
                                options=[
                                    {"label": "1 Month", "value": "1mo"},
                                    {"label": "3 Months", "value": "3mo"},
                                    {"label": "6 Months", "value": "6mo"},
                                    {"label": "1 Year", "value": "1y"},
                                    {"label": "5 Years", "value": "5y"},
                                ],
                                value="1y",
                                className="dash-dropdown",
                            ),
                        ], className="card", style={"flex": "1"}),
                        
                        html.Div([
                            html.H3("Chart Type", className="card-header"),
                            dcc.Dropdown(
                                id="chart-type",
                                options=[
                                    {"label": "Line", "value": "line"},
                                    {"label": "Candlestick", "value": "candlestick"},
                                ],
                                value="line",
                                className="dash-dropdown",
                            ),
                        ], className="card", style={"flex": "1"}),
                    ], style={"display": "flex", "gap": "20px", "margin-bottom": "20px"}),
                ]),
                
                # Stock info display with KPIs
                html.Div([
                    html.Div(id="stock-info", className="stock-info"),
                    html.Div(id="stock-kpi-cards", className="stock-kpi-container"),
                ], className="info-section"),
                
                # Graph with loading indicator
                html.Div([
                    dcc.Loading(
                        id="loading-graph",
                        type="circle",
                        children=[
                            dcc.Graph(id="stock-graph"),
                        ]
                    ),
                ], className="graph-container"),
                
                # News section
                html.Div([
                    html.H3("Latest News", className="section-header"),
                    dcc.Loading(
                        id="loading-news",
                        type="circle",
                        children=[
                            html.Div(id="stock-news", className="news-container"),
                        ]
                    ),
                ], className="news-section card"),
                
                # Error message
                html.Div(id="error-message", style={"color": "red", "margin-top": "10px"}),
            ], style={"padding": "20px"}),
        ]),
        
        # Tab for portfolio management
        dcc.Tab(label="Portfolio Management", value="tab-2", className="dash-tab", children=[
            html.Div([
                # Import Portfolio section
                html.Div([
                    html.H3("Import Portfolio", className="card-header"),
                    html.Div([
                        dcc.Dropdown(
                            id="portfolio-file-dropdown",
                            placeholder="Select a portfolio file",
                            className="dash-dropdown",
                            style={"flex-grow": "1"}
                        ),
                        html.Button("Import", id="import-portfolio-button", n_clicks=0),
                    ], className="form-group"),
                    html.Div(id="import-status", className="status-message"),
                ], className="card"),
                
                html.Div([
                    html.H3("Add Stock to Portfolio", className="card-header"),
                    html.Div([
                        dcc.Input(
                            id="add-stock-symbol",
                            type="text",
                            placeholder="Stock Symbol (e.g., AAPL)",
                            className="form-control",
                        ),
                        dcc.Input(
                            id="add-stock-shares",
                            type="number",
                            placeholder="Number of Shares",
                            className="form-control",
                        ),
                        dcc.Input(
                            id="add-stock-price",
                            type="number",
                            placeholder="Purchase Price (optional)",
                            className="form-control",
                        ),
                        html.Button("Add to Portfolio", id="add-stock-button", n_clicks=0),
                    ], className="form-group"),
                ], className="card"),
                
                # Portfolio summary card
                html.Div([
                    html.H3("Portfolio Summary", className="card-header"),
                    html.Div(id="portfolio-summary", className="portfolio-summary"),
                ], className="card"),
                
                # Portfolio table
                html.Div([
                    html.H3("Your Portfolio", className="card-header"),
                    html.Div(id="portfolio-table"),
                ], className="card"),
                
                # Portfolio performance graph
                html.Div([
                    html.H3("Portfolio Performance", className="card-header"),
                    html.Div([
                        dcc.Loading(
                            id="loading-portfolio-graph",
                            type="circle",
                            children=[
                                dcc.Graph(id="portfolio-graph"),
                            ]
                        ),
                    ], className="graph-container"),
                ], className="card"),
                
                # Portfolio correlation heatmap
                html.Div([
                    html.H3("Portfolio Stock Correlation", className="card-header"),
                    html.Div([
                        dcc.Loading(
                            id="loading-correlation",
                            type="circle",
                            children=[
                                dcc.Graph(id="portfolio-correlation-heatmap"),
                            ]
                        ),
                    ], className="graph-container"),
                ], className="card"),
            ], style={"padding": "20px"}),
        ]),
        
        # Tab for comparison
        dcc.Tab(label="Stock Comparison", value="tab-3", className="dash-tab", children=[
            html.Div([
                html.Div([
                    html.H3("Compare Stocks", className="card-header"),
                    html.Div([
                        dcc.Input(
                            id="compare-stocks-input",
                            type="text",
                            placeholder="Enter stock symbols separated by commas (e.g., AAPL,MSFT,GOOG)",
                            className="form-control",
                            style={"flex-grow": "1"}
                        ),
                        html.Button("Compare", id="compare-button", n_clicks=0),
                    ], className="form-group"),
                ], className="card"),
                
                # Comparison graph
                html.Div([
                    html.H3("Price Comparison", className="card-header"),
                    html.Div([
                        dcc.Graph(id="comparison-graph"),
                    ], className="graph-container"),
                ], className="card"),
                
                # Correlation heatmap
                html.Div([
                    html.H3("Correlation Matrix", className="card-header"),
                    html.Div([
                        dcc.Graph(id="comparison-correlation-heatmap"),
                    ], className="graph-container"),
                ], className="card"),
            ], style={"padding": "20px"}),
        ]),
    ]),
])

# Callback for stock visualization
@app.callback(
    [Output("stock-graph", "figure"), 
     Output("stock-info", "children"),
     Output("error-message", "children")],
    [Input("submit-button", "n_clicks"), 
     Input("time-period", "value"),
     Input("chart-type", "value")],
    [State("stock-input", "value")]
)
def update_stock_graph(n_clicks, period, chart_type, stock_symbol):
    if n_clicks == 0:
        # Default stock on initial load
        stock_symbol = "AAPL"
    
    if not stock_symbol:
        return {}, "", "Please enter a stock symbol"
    
    try:
        # Get stock data
        df = get_stock_data(stock_symbol.upper(), period)
        
        # Create stock info display
        info = ""
        if not df.empty:
            last_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2] if len(df) > 1 else last_price
            price_change = last_price - prev_price
            price_change_pct = (price_change / prev_price) * 100 if prev_price != 0 else 0
            
            info = html.Div([
                html.H3(f"{stock_symbol.upper()} - ${last_price:.2f}"),
                html.P(f"Change: {price_change:.2f} ({price_change_pct:.2f}%)", 
                      className="positive-value" if price_change >= 0 else "negative-value"),
                html.P(f"Period: {period}")
            ])
        
        # Create graph
        if chart_type == "line":
            figure = {
                "data": [
                    go.Scatter(
                        x=df.index,
                        y=df["Close"],
                        mode="lines",
                        name="Close Price",
                        line={"color": "#536dfe", "width": 2},
                        fill='tozeroy',
                        fillcolor='rgba(83, 109, 254, 0.2)',
                    )
                ],
                "layout": go.Layout(
                    title=f"{stock_symbol.upper()} Stock Price",
                    xaxis={"title": "Date"},
                    yaxis={"title": "Price (USD)"},
                    height=600,
                    hovermode="closest",
                ),
            }
        else:  # candlestick
            # Calculate 20-day moving average
            if len(df) > 20:
                df['MA20'] = df['Close'].rolling(window=20).mean()
                
            figure = {
                "data": [
                    go.Candlestick(
                        x=df.index,
                        open=df["Open"],
                        high=df["High"],
                        low=df["Low"],
                        close=df["Close"],
                        name="Candlestick",
                        increasing={'line': {'color': '#00c853'}},
                        decreasing={'line': {'color': '#ff3d00'}},
                    ),
                    go.Scatter(
                        x=df.index,
                        y=df['MA20'] if len(df) > 20 else [],
                        mode="lines",
                        name="20-Day MA",
                        line={"color": "#536dfe", "width": 2},
                    )
                ],
                "layout": go.Layout(
                    title=f"{stock_symbol.upper()} Stock Price",
                    xaxis={"title": "Date"},
                    yaxis={"title": "Price (USD)"},
                    height=600,
                    legend={"orientation": "h", "y": -0.1}
                ),
            }
            
        return figure, info, ""
        
    except Exception as e:
        return {}, "", f"Error: {str(e)}"

# Callback for portfolio management
@app.callback(
    [Output("portfolio-table", "children"),
     Output("portfolio-graph", "figure")],
    [Input("add-stock-button", "n_clicks")],
    [State("add-stock-symbol", "value"),
     State("add-stock-shares", "value"),
     State("add-stock-price", "value")]
)
def update_portfolio(n_clicks, symbol, shares, price):
    # Add the stock to portfolio if inputs are provided
    if n_clicks > 0 and symbol and shares:
        portfolio.add_stock(symbol.upper(), float(shares), price)
    
    # Generate portfolio table
    portfolio_data = portfolio.get_portfolio_data()
    
    if portfolio_data:
        table_header = [
            html.Thead(html.Tr([
                html.Th("Symbol"),
                html.Th("Shares"),
                html.Th("Current Price"),
                html.Th("Current Value"),
                html.Th("Purchase Price"),
                html.Th("Gain/Loss"),
                html.Th("Gain/Loss %"),
                html.Th("Actions")
            ]))
        ]
        
        rows = []
        for stock in portfolio_data:
            row = html.Tr([
                html.Td(stock["symbol"]),
                html.Td(f"{stock['shares']:.2f}"),
                html.Td(f"${stock['current_price']:.2f}"),
                html.Td(f"${stock['current_value']:.2f}"),
                html.Td(f"${stock['purchase_price']:.2f}" if stock['purchase_price'] else "N/A"),
                html.Td(f"${stock['gain_loss']:.2f}" if stock['purchase_price'] else "N/A", 
                        className="positive-value" if stock.get('gain_loss', 0) >= 0 else "negative-value"),
                html.Td(f"{stock['gain_loss_percent']:.2f}%" if stock['purchase_price'] else "N/A",
                        className="positive-value" if stock.get('gain_loss_percent', 0) >= 0 else "negative-value"),
                html.Td(html.Button("Remove", id={"type": "remove-stock", "index": stock["symbol"]}))
            ])
            rows.append(row)
        
        table_body = [html.Tbody(rows)]
        table = html.Table(table_header + table_body, className="portfolio-table")
        
        # Create portfolio performance graph
        if len(portfolio_data) > 0:
            performance_data = portfolio.get_portfolio_performance()
            
            figure = {
                "data": [                            go.Scatter(
                                x=performance_data.index,
                                y=performance_data["Total"],
                                mode="lines",
                                name="Portfolio Value",
                                line={"color": "#00c853", "width": 2},
                                fill='tozeroy',
                                fillcolor='rgba(0, 200, 83, 0.2)',
                            )
                ],
                "layout": go.Layout(
                    title="Portfolio Performance",
                    xaxis={"title": "Date"},
                    yaxis={"title": "Value (USD)"},
                    height=500,
                ),
            }
        else:
            figure = {}
            
        return table, figure
    
    return html.P("No stocks in portfolio yet."), {}

# Callback for stock comparison
@app.callback(
    [Output("comparison-graph", "figure"),
     Output("comparison-correlation-heatmap", "figure")],
    [Input("compare-button", "n_clicks")],
    [State("compare-stocks-input", "value")]
)
def update_comparison(n_clicks, stock_symbols):
    if n_clicks == 0 or not stock_symbols:
        # Default comparison on initial load
        stock_symbols = "AAPL,MSFT,GOOG"
    
    try:
        symbols = [s.strip().upper() for s in stock_symbols.split(",")]
        
        # Get data for multiple stocks
        df = get_multiple_stock_data(symbols)
        
        # Normalize data for comparison (start at 100)
        normalized_df = pd.DataFrame()
        
        for symbol in symbols:
            if symbol in df.columns:
                normalized_df[symbol] = (df[symbol] / df[symbol].iloc[0]) * 100
        
        # Create comparison graph
        comparison_data = []
        
        for symbol in normalized_df.columns:
            comparison_data.append(
                go.Scatter(
                    x=normalized_df.index,
                    y=normalized_df[symbol],
                    mode="lines",
                    name=symbol
                )
            )
            
        comparison_figure = {
            "data": comparison_data,
            "layout": go.Layout(
                title="Stock Price Comparison (Normalized)",
                xaxis={"title": "Date"},
                yaxis={"title": "Normalized Price (Base = 100)"},
                height=500,
            )
        }
        
        # Create correlation heatmap
        correlation_matrix = df.corr()
        
        heatmap_figure = {
            "data": [
                go.Heatmap(
                    z=correlation_matrix.values,
                    x=correlation_matrix.columns,
                    y=correlation_matrix.index,
                    colorscale="RdBu",
                )
            ],
            "layout": go.Layout(
                title="Correlation Matrix",
                height=500,
            )
        }
        
        return comparison_figure, heatmap_figure
        
    except Exception as e:
        empty_fig = {"data": [], "layout": go.Layout(title=f"Error: {str(e)}")}
        return empty_fig, empty_fig

# Callback for removing stocks from portfolio
@app.callback(
    [Output("portfolio-table", "children", allow_duplicate=True),
     Output("portfolio-graph", "figure", allow_duplicate=True)],
    [Input({"type": "remove-stock", "index": ALL}, "n_clicks")],
    [State({"type": "remove-stock", "index": ALL}, "id")],
    prevent_initial_call=True
)
def remove_stock(n_clicks_list, button_ids):
    # Check if any button was clicked
    if not n_clicks_list or not any(click for click in n_clicks_list if click):
        # If callback triggered on page load, don't do anything
        return no_update, no_update
    
    # Find which button was clicked
    ctx = dash.callback_context
    if not ctx.triggered:
        return no_update, no_update
    
    # Get the id of the clicked button
    button_id = ctx.triggered[0]["prop_id"].split(".")[0]
    if button_id:
        try:
            # Extract the symbol from the button id
            button_id_dict = eval(button_id)
            symbol = button_id_dict["index"]
            
            # Remove the stock from the portfolio
            portfolio.remove_stock(symbol)
            
            # Generate updated portfolio table
            portfolio_data = portfolio.get_portfolio_data()
            
            if portfolio_data:
                table_header = [
                    html.Thead(html.Tr([
                        html.Th("Symbol"),
                        html.Th("Shares"),
                        html.Th("Current Price"),
                        html.Th("Current Value"),
                        html.Th("Purchase Price"),
                        html.Th("Gain/Loss"),
                        html.Th("Gain/Loss %"),
                        html.Th("Actions")
                    ]))
                ]
                
                rows = []
                for stock in portfolio_data:
                    row = html.Tr([
                        html.Td(stock["symbol"]),
                        html.Td(f"{stock['shares']:.2f}"),
                        html.Td(f"${stock['current_price']:.2f}"),
                        html.Td(f"${stock['current_value']:.2f}"),
                        html.Td(f"${stock['purchase_price']:.2f}" if stock['purchase_price'] else "N/A"),
                        html.Td(f"${stock['gain_loss']:.2f}" if stock['purchase_price'] else "N/A", 
                                className="positive-value" if stock.get('gain_loss', 0) >= 0 else "negative-value"),
                        html.Td(f"{stock['gain_loss_percent']:.2f}%" if stock['purchase_price'] else "N/A",
                                className="positive-value" if stock.get('gain_loss_percent', 0) >= 0 else "negative-value"),
                        html.Td(html.Button("Remove", id={"type": "remove-stock", "index": stock["symbol"]}))
                    ])
                    rows.append(row)
                
                table_body = [html.Tbody(rows)]
                table = html.Table(table_header + table_body, className="portfolio-table")
                
                # Create portfolio performance graph
                if len(portfolio_data) > 0:
                    performance_data = portfolio.get_portfolio_performance()
                    
                    figure = {
                        "data": [
                            go.Scatter(
                                x=performance_data.index,
                                y=performance_data["Total"],
                                mode="lines",
                                name="Portfolio Value",
                                line={"color": "#00c853", "width": 2},
                                fill='tozeroy',
                                fillcolor='rgba(0, 200, 83, 0.2)',
                            )
                        ],
                        "layout": go.Layout(
                            title="Portfolio Performance",
                            xaxis={"title": "Date"},
                            yaxis={"title": "Value (USD)"},
                            height=500,
                        ),
                    }
                else:
                    figure = {}
                    
                return table, figure
            
            return html.P("No stocks in portfolio yet."), {}
        except Exception as e:
            print(f"Error removing stock: {str(e)}")
            return no_update, no_update
    
    return no_update, no_update

# Callback to populate portfolio files dropdown
@app.callback(
    Output("portfolio-file-dropdown", "options"),
    [Input("tabs", "value")]  # Triggered when switching to the Portfolio tab
)
def update_portfolio_files_dropdown(tab_value):
    """
    Update the dropdown with available portfolio files when the Portfolio tab is selected.
    """
    if tab_value == "tab-2":  # Portfolio Management tab
        portfolio_files = portfolio.get_available_portfolios()
        
        # Format options for dropdown
        options = [
            {"label": os.path.basename(file_path), "value": file_path}
            for file_path in portfolio_files
        ]
        
        return options
    
    return []

# Callback for importing portfolio
@app.callback(
    [Output("import-status", "children"),
     Output("portfolio-table", "children", allow_duplicate=True),
     Output("portfolio-graph", "figure", allow_duplicate=True),
     Output("portfolio-summary", "children")],
    [Input("import-portfolio-button", "n_clicks")],
    [State("portfolio-file-dropdown", "value")],
    prevent_initial_call=True
)
def import_portfolio(n_clicks, file_path):
    """
    Import portfolio from selected JSON file.
    """
    if n_clicks == 0 or not file_path:
        return "", no_update, no_update, no_update
    
    try:
        # Import the portfolio
        success = portfolio.import_from_json(file_path)
        
        if success:
            # Get portfolio data after successful import
            portfolio_data = portfolio.get_portfolio_data()
            
            # Generate portfolio table
            if portfolio_data:
                table_header = [
                    html.Thead(html.Tr([
                        html.Th("Symbol"),
                        html.Th("Shares"),
                        html.Th("Purchase Price"),
                        html.Th("Current Price"),
                        html.Th("Current Value"),
                        html.Th("Gain/Loss"),
                        html.Th("Gain/Loss %"),
                        html.Th("Actions"),
                    ]))
                ]
                
                rows = []
                for stock in portfolio_data:
                    symbol = stock["symbol"]
                    shares = stock["shares"]
                    purchase_price = stock["purchase_price"]
                    current_price = stock["current_price"]
                    current_value = shares * current_price
                    gain_loss = current_value - (shares * purchase_price)
                    gain_loss_pct = (gain_loss / (shares * purchase_price)) * 100 if purchase_price else 0
                    
                    # Determine CSS class based on gain/loss
                    gain_loss_class = "positive-value" if gain_loss >= 0 else "negative-value"
                    
                    row = html.Tr([
                        html.Td(symbol),
                        html.Td(f"{shares:.2f}"),
                        html.Td(f"${purchase_price:.2f}" if purchase_price else "N/A"),
                        html.Td(f"${current_price:.2f}"),
                        html.Td(f"${current_value:.2f}"),
                        html.Td(f"${gain_loss:.2f}", className=gain_loss_class),
                        html.Td(f"{gain_loss_pct:.2f}%", className=gain_loss_class),
                        html.Td(
                            html.Button(
                                "✕", 
                                id={"type": "remove-stock", "index": symbol},
                                className="remove-btn",
                                title=f"Remove {symbol}"
                            )
                        ),
                    ])
                    rows.append(row)
                
                table_body = [html.Tbody(rows)]
                table = html.Table(table_header + table_body, className="portfolio-table")
                
                # Create portfolio performance graph
                if len(portfolio_data) > 0:
                    performance_data = portfolio.get_historical_performance()
                    
                    figure = {
                        "data": [
                            go.Scatter(
                                x=performance_data.index,
                                y=performance_data["Total"],
                                mode="lines",
                                name="Portfolio Value",
                                line={"color": "#00c853", "width": 2},
                                fill='tozeroy',
                                fillcolor='rgba(0, 200, 83, 0.2)',
                            )
                        ],
                        "layout": go.Layout(
                            title="Portfolio Performance",
                            xaxis={"title": "Date"},
                            yaxis={"title": "Value (USD)"},
                            height=500,
                        ),
                    }
                else:
                    figure = {}
                
                # Generate portfolio summary
                metrics = portfolio.get_performance_metrics()
                
                total_invested = metrics['total_invested']
                total_current_value = metrics['total_current_value']
                total_gain_loss = metrics['total_gain_loss']
                total_gain_loss_pct = metrics['total_gain_loss_pct']
                
                # Create summary component
                summary = html.Div([
                    html.Div([
                        html.Div([
                            html.H4("Total Invested"),
                            html.Div(f"${total_invested:.2f}", className="summary-value")
                        ], className="summary-card"),
                        html.Div([
                            html.H4("Current Value"),
                            html.Div(f"${total_current_value:.2f}", className="summary-value")
                        ], className="summary-card"),
                        html.Div([
                            html.H4("Total Gain/Loss"),
                            html.Div(f"${total_gain_loss:.2f} ({total_gain_loss_pct:.2f}%)", 
                                    className="positive-value" if total_gain_loss >= 0 else "negative-value")
                        ], className="summary-card"),
                    ], className="summary-cards-container")
                ], className="portfolio-summary-container")
                
                return html.Div(f"Successfully imported portfolio from {os.path.basename(file_path)}", className="success-message"), table, figure, summary
            
            return html.Div("Portfolio imported but no stocks found", className="warning-message"), html.P("No stocks in portfolio yet."), {}, no_update
        else:
            return html.Div("Failed to import portfolio", className="error-message"), no_update, no_update, no_update
    except Exception as e:
        return html.Div(f"Error: {str(e)}", className="error-message"), no_update, no_update, no_update

# Callback for dark mode toggle - Using clientside callback
app.clientside_callback(
    """
    function(n_clicks) {
        return window.dash_clientside.dark_mode.toggleDarkMode(n_clicks);
    }
    """,
    Output("dark-mode-toggle", "children"),
    [Input("dark-mode-toggle", "n_clicks")],
)

# Callback for stock info
@app.callback(
    [Output("stock-graph", "figure", allow_duplicate=True),
     Output("stock-info", "children", allow_duplicate=True),
     Output("error-message", "children", allow_duplicate=True),
     Output("stock-kpi-cards", "children"),
     Output("stock-news", "children")],
    [Input("submit-button", "n_clicks")],
    [State("stock-input", "value"),
     State("time-period", "value"),
     State("chart-type", "value")],
    prevent_initial_call=True
)
def update_graph(n_clicks, stock_symbol, time_period, chart_type):
    if not stock_symbol:
        return {}, "", "", [], []
    
    try:
        # Get stock data
        df = get_stock_data(stock_symbol.upper(), period=time_period)
        
        if df.empty:
            return {}, "", f"No data found for {stock_symbol.upper()}", [], []
            
        # Generate info section with stock details
        info = get_stock_info(stock_symbol.upper())
        
        info_div = html.Div([
            html.H2(info.get("name", stock_symbol.upper()), className="stock-name"),
            html.Div([
                html.Span(f"Sector: {info.get('sector', 'N/A')} | "),
                html.Span(f"Industry: {info.get('industry', 'N/A')}"),
            ], className="stock-sector-industry"),
        ])
        
        # Create KPI cards
        kpi_cards = []
        
        # Current price card
        current_price = info.get("current_price", "N/A")
        if current_price != "N/A":
            price_change = df["Close"][-1] - df["Close"][-2] if len(df) >= 2 else 0
            price_change_pct = (price_change / df["Close"][-2] * 100) if len(df) >= 2 else 0
            price_class = "positive-value" if price_change >= 0 else "negative-value"
            price_icon = "▲" if price_change >= 0 else "▼"
            
            kpi_cards.append(
                html.Div([
                    html.H4("Current Price"),
                    html.Div([
                        html.Span(f"${current_price:.2f}" if isinstance(current_price, (int, float)) else current_price, className="kpi-value"),
                        html.Span(f" {price_icon} {price_change_pct:.2f}%", className=price_class)
                    ]),
                ], className="kpi-card")
            )
            
        # Market cap card
        market_cap = info.get("market_cap", "N/A")
        if market_cap != "N/A" and isinstance(market_cap, (int, float)):
            market_cap_str = f"${market_cap/1000000000:.2f}B" if market_cap >= 1000000000 else f"${market_cap/1000000:.2f}M"
            kpi_cards.append(
                html.Div([
                    html.H4("Market Cap"),
                    html.Div(market_cap_str, className="kpi-value")
                ], className="kpi-card")
            )
            
        # P/E ratio card
        pe_ratio = info.get("pe_ratio", "N/A")
        kpi_cards.append(
            html.Div([
                html.H4("P/E Ratio"),
                html.Div(f"{pe_ratio:.2f}" if isinstance(pe_ratio, (int, float)) else pe_ratio, className="kpi-value")
            ], className="kpi-card")
        )
            
        # 52 week range
        week_high = info.get("52_week_high", "N/A")
        week_low = info.get("52_week_low", "N/A")
        if week_high != "N/A" and week_low != "N/A":
            kpi_cards.append(
                html.Div([
                    html.H4("52-Week Range"),
                    html.Div([
                        html.Span(f"${week_low:.2f}" if isinstance(week_low, (int, float)) else week_low),
                        html.Span(" - "),
                        html.Span(f"${week_high:.2f}" if isinstance(week_high, (int, float)) else week_high)
                    ], className="kpi-value")
                ], className="kpi-card")
            )
            
        # Dividend yield
        div_yield = info.get("dividend_yield", "N/A")
        if div_yield not in ("N/A", None):
            div_yield_pct = div_yield * 100 if isinstance(div_yield, (int, float)) else div_yield
            kpi_cards.append(
                html.Div([
                    html.H4("Dividend Yield"),
                    html.Div(f"{div_yield_pct:.2f}%" if isinstance(div_yield_pct, (int, float)) else "N/A", className="kpi-value")
                ], className="kpi-card")
            )
            
        # Create kpi cards container
        kpi_cards_container = html.Div(kpi_cards, className="kpi-cards")
        
        # Get news for the stock
        news_items = get_stock_news(stock_symbol.upper())
        
        # Create news cards
        news_cards = []
        for item in news_items:
            news_cards.append(
                html.A([
                    html.Div([
                        html.Img(src=item.get('thumbnail', ''), className="news-thumbnail") if item.get('thumbnail') else html.Div(className="news-thumbnail-placeholder"),
                        html.Div([
                            html.H4(item.get('title'), className="news-title"),
                            html.Div([
                                html.Span(item.get('publisher'), className="news-publisher"),
                                html.Span(" • "),
                                html.Span(item.get('published'), className="news-date")
                            ], className="news-meta")
                        ], className="news-content")
                    ], className="news-card")
                ], href=item.get('url'), target="_blank", className="news-link")
            )
            
        news_container = html.Div(news_cards if news_cards else html.Div("No recent news found", className="no-news"))
        
        # Create figure based on chart type
        if chart_type == "line":
            figure = {
                "data": [
                    go.Scatter(
                        x=df.index,
                        y=df["Close"],
                        mode="lines",
                        name="Close Price",
                        line={"color": "#00c853", "width": 2},
                    ),
                    go.Scatter(
                        x=df.index,
                        y=df['MA20'] if len(df) > 20 else [],
                        mode="lines",
                        name="20-Day MA",
                        line={"color": "#536dfe", "width": 2},
                    )
                ],
                "layout": go.Layout(
                    title=f"{stock_symbol.upper()} Stock Price",
                    xaxis={"title": "Date"},
                    yaxis={"title": "Price (USD)"},
                    height=600,
                    legend={"orientation": "h", "y": -0.1}
                ),
            }
        else:  # Candlestick
            figure = {
                "data": [
                    go.Candlestick(
                        x=df.index,
                        open=df["Open"],
                        high=df["High"],
                        low=df["Low"],
                        close=df["Close"],
                        name="OHLC",
                        increasing={"line": {"color": "#00c853"}},
                        decreasing={"line": {"color": "#ff3d00"}},
                    ),
                    go.Scatter(
                        x=df.index,
                        y=df['MA20'] if len(df) > 20 else [],
                        mode="lines",
                        name="20-Day MA",
                        line={"color": "#536dfe", "width": 2},
                    )
                ],
                "layout": go.Layout(
                    title=f"{stock_symbol.upper()} Stock Price",
                    xaxis={"title": "Date"},
                    yaxis={"title": "Price (USD)"},
                    height=600,
                    legend={"orientation": "h", "y": -0.1}
                ),
            }
            
        return figure, info_div, "", kpi_cards_container, news_container
        
    except Exception as e:
        return {}, "", f"Error: {str(e)}", [], []

# Callback for portfolio correlation heatmap
@app.callback(
    Output("portfolio-correlation-heatmap", "figure"),
    [Input("portfolio-table", "children")],
)
def update_correlation_heatmap(portfolio_table):
    """Create a correlation heatmap for portfolio stocks"""
    try:
        # Get portfolio data
        portfolio_data = portfolio.get_portfolio_data()
        
        if not portfolio_data or len(portfolio_data) < 2:
            # Not enough stocks for correlation
            return {
                "data": [],
                "layout": go.Layout(
                    title="Add at least 2 stocks to see correlation",
                    height=400
                )
            }
        
        # Extract symbols
        symbols = [stock["symbol"] for stock in portfolio_data]
        
        # Get historical data for all stocks
        historical_data = get_multiple_stock_data(symbols, period="1y")
        
        # Calculate correlation
        returns = historical_data.pct_change().dropna()
        correlation_matrix = returns.corr()
        
        # Create heatmap
        heatmap = go.Heatmap(
            z=correlation_matrix.values,
            x=correlation_matrix.columns,
            y=correlation_matrix.index,
            colorscale='RdBu_r',  # Red to blue color scale, reversed
            zmin=-1,
            zmax=1,
            text=[[f"{val:.2f}" for val in row] for row in correlation_matrix.values],
            hoverinfo="text",
            colorbar={"title": "Correlation"}
        )
        
        # Create figure
        figure = {
            "data": [heatmap],
            "layout": go.Layout(
                title="Portfolio Stock Correlation",
                height=400,
                xaxis={"title": ""},
                yaxis={"title": ""},
            )
        }
        
        return figure
    except Exception as e:
        print(f"Error updating correlation heatmap: {str(e)}")
        # Return empty figure on error
        return {
            "data": [],
            "layout": go.Layout(
                title="Unable to generate correlation heatmap",
                height=400
            )
        }

# Run the app
if __name__ == "__main__":
    app.run(debug=True)
