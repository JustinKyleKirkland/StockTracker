# Stock Tracker

A Python application for tracking and visualizing stock/fund performance.

## Features

- **Stock Visualization**: View historical stock prices with line and candlestick charts
- **Portfolio Management**: Track your portfolio with real-time values and gain/loss calculations
- **Stock Comparison**: Compare multiple stocks and see correlation between them

## Installation

1. Clone this repository
2. Install required packages:

```bash
pip install yfinance pandas matplotlib dash plotly pandas-datareader
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

## Technologies Used

- Python 3
- yfinance: Yahoo Finance API wrapper
- pandas: Data analysis
- plotly: Interactive graphs
- Dash: Web application framework

## License

See the LICENSE file for details.
