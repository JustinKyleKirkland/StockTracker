import yfinance as yf
import pandas as pd


def get_stock_data(symbol, period="1y"):
    """
    Fetch stock data for a specific symbol and time period.

    Args:
        symbol (str): Stock ticker symbol (e.g., AAPL, MSFT)
        period (str): Time period (1mo, 3mo, 6mo, 1y, 5y, etc.)

    Returns:
        pandas.DataFrame: DataFrame containing stock price data with technical indicators
    """
    try:
        # Fetch stock data directly using yfinance
        # period can be: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period)

        # If dataframe is empty, try using interval parameter
        if df.empty:
            df = ticker.history(period=period, interval="1d")

        # Add technical indicators
        if not df.empty:
            # Calculate moving averages
            df["MA20"] = df["Close"].rolling(window=20).mean()
            df["MA50"] = df["Close"].rolling(window=50).mean()
            df["MA200"] = df["Close"].rolling(window=200).mean()

            # Calculate daily returns
            df["Returns"] = df["Close"].pct_change()

            # Calculate volatility (20-day rolling standard deviation)
            df["Volatility"] = df["Returns"].rolling(window=20).std() * (
                252**0.5
            )  # Annualized

        return df
    except Exception as e:
        print(f"Error fetching data for {symbol}: {str(e)}")
        return pd.DataFrame()  # Return empty DataFrame on error


def get_stock_info(symbol):
    """
    Fetch additional stock information.

    Args:
        symbol (str): Stock ticker symbol

    Returns:
        dict: Dictionary containing stock information
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        # Filter out the most relevant information
        relevant_info = {
            "name": info.get("shortName", "N/A"),
            "sector": info.get("sector", "N/A"),
            "industry": info.get("industry", "N/A"),
            "market_cap": info.get("marketCap", "N/A"),
            "pe_ratio": info.get("trailingPE", "N/A"),
            "eps": info.get("trailingEps", "N/A"),
            # Additional KPIs for enhanced display
            "52_week_high": info.get("fiftyTwoWeekHigh", "N/A"),
            "52_week_low": info.get("fiftyTwoWeekLow", "N/A"),
            "dividend_yield": info.get("dividendYield", "N/A"),
            "beta": info.get("beta", "N/A"),
            "avg_volume": info.get("averageVolume", "N/A"),
            "price_to_book": info.get("priceToBook", "N/A"),
            "current_price": info.get(
                "currentPrice", info.get("regularMarketPrice", "N/A")
            ),
            "recommendation": info.get("recommendationKey", "N/A"),
        }

        return relevant_info
    except Exception as e:
        print(f"Error fetching info for {symbol}: {str(e)}")
        return {}  # Return empty dict on error


def get_multiple_stock_data(symbols, period="1y"):
    """
    Fetch data for multiple stocks for comparison.

    Args:
        symbols (list): List of stock ticker symbols
        period (str): Time period

    Returns:
        pandas.DataFrame: DataFrame containing the closing prices of all stocks
    """
    all_data = pd.DataFrame()

    for symbol in symbols:
        df = get_stock_data(symbol, period)
        if not df.empty:
            all_data[symbol] = df["Close"]

    return all_data


def calculate_returns(df):
    """
    Calculate daily returns from a DataFrame of prices.

    Args:
        df (pandas.DataFrame): DataFrame with stock prices

    Returns:
        pandas.DataFrame: DataFrame with daily returns
    """
    return df.pct_change().dropna()
