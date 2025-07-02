# Stock Tracker

A Python application for tracking and visualizing stock/fund performance with comprehensive profit analysis.

## Features

- **Stock Visualization**: View historical stock prices with line and candlestick charts
- **Portfolio Management**: Track your portfolio with real-time values and gain/loss calculations
- **Stock Comparison**: Compare multiple stocks and see correlation between them
- **Profit Analysis**: Detailed breakdown of realized and unrealized profits by stock
- **Transaction History**: Track all buy/sell transactions with profit calculations
- **Data Export**: Export transaction data to CSV for further analysis

## Installation

1. Clone this repository
2. Install required packages:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
python app.py
```

2. Open your browser and navigate to http://127.0.0.1:8050/

## How to Use

### Stock Visualization
- Enter a stock symbol (e.g., AAPL, MSFT, GOOG) and select a time period
- Choose between line and candlestick charts
- View current price and price change information

### Portfolio Management
- Add stocks to your portfolio with the number of shares and purchase price
- View your current portfolio value, individual stock performances, and total gain/loss
- Track portfolio performance over time

### Stock Comparison
- Enter multiple stock symbols separated by commas
- View normalized price charts for comparison
- See correlation matrix between stocks

### Profit Analysis
- Detailed breakdown of realized and unrealized profits per stock
- Visualize profit distribution across your portfolio
- Track total profit, realized profit, and unrealized profit separately

### Transaction History
- View complete transaction history for all stocks
- See profit calculations for sold shares
- Export transaction data to CSV for record-keeping

## Technologies Used

- Python 3
- yfinance: Yahoo Finance API wrapper
- pandas: Data analysis
- plotly: Interactive graphs
- Dash: Web application framework

## License

See the LICENSE file for details.
