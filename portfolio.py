import pandas as pd
import datetime as dt
import json
import os
import glob
from stock_data import get_stock_data, get_multiple_stock_data


class Portfolio:
    def __init__(self):
        """
        Initialize an empty portfolio.
        """
        self.stocks = {}  # Dictionary to store stock data: {symbol: {'shares': n, 'purchase_price': p}}
        self.transactions = {}  # Dictionary to store transaction history: {symbol: [list of transactions]}
        self.realized_profits = {}  # Dictionary to store realized profits from sold shares: {symbol: total_profit}

    def add_stock(self, symbol, shares, purchase_price=None):
        """
        Add a stock to the portfolio.

        Args:
            symbol (str): Stock ticker symbol
            shares (float): Number of shares
            purchase_price (float, optional): Purchase price per share
        """
        # Check if we already have this stock
        if symbol in self.stocks:
            # If already in portfolio, update the shares and purchase price (weighted average)
            existing_shares = self.stocks[symbol]["shares"]

            if purchase_price is not None:
                if self.stocks[symbol]["purchase_price"] is not None:
                    # Calculate new weighted average purchase price
                    old_value = existing_shares * self.stocks[symbol]["purchase_price"]
                    new_value = shares * purchase_price
                    total_shares = existing_shares + shares
                    new_avg_price = (old_value + new_value) / total_shares

                    self.stocks[symbol] = {
                        "shares": total_shares,
                        "purchase_price": new_avg_price,
                    }
                else:
                    # If previous purchase price was None, use the new one
                    self.stocks[symbol] = {
                        "shares": existing_shares + shares,
                        "purchase_price": purchase_price,
                    }
            else:
                # If no new purchase price provided, keep the old one but update shares
                self.stocks[symbol] = {
                    "shares": existing_shares + shares,
                    "purchase_price": self.stocks[symbol]["purchase_price"],
                }
        else:
            # Add new stock
            self.stocks[symbol] = {"shares": shares, "purchase_price": purchase_price}

    def remove_stock(self, symbol, shares=None):
        """
        Remove a stock from the portfolio.

        Args:
            symbol (str): Stock ticker symbol
            shares (float, optional): Number of shares to remove. If None, removes all shares.

        Returns:
            bool: True if successful, False otherwise
        """
        if symbol not in self.stocks:
            return False

        if shares is None or shares >= self.stocks[symbol]["shares"]:
            # Remove the entire stock
            del self.stocks[symbol]
        else:
            # Remove only specified shares
            self.stocks[symbol]["shares"] -= shares

            # If shares become 0, remove the stock
            if self.stocks[symbol]["shares"] <= 0:
                del self.stocks[symbol]

        return True

    def get_portfolio_data(self):
        """
        Get current portfolio data with latest prices and values.

        Returns:
            list: List of dictionaries with portfolio data
        """
        if not self.stocks:
            return []

        portfolio_data = []

        for symbol, data in self.stocks.items():
            try:
                # Get latest stock data
                stock_df = get_stock_data(symbol, period="5d")

                if not stock_df.empty:
                    current_price = stock_df["Close"].iloc[-1]
                    current_value = current_price * data["shares"]

                    # Get the actual remaining investment (cost basis)
                    remaining_cost = data.get(
                        "remaining_cost", data["purchase_price"] * data["shares"]
                    )

                    stock_info = {
                        "symbol": symbol,
                        "shares": data["shares"],
                        "current_price": current_price,
                        "current_value": current_value,
                        "purchase_price": data["purchase_price"],
                        "remaining_cost": remaining_cost,
                    }

                    # Calculate gain/loss if purchase price is available
                    if data["purchase_price"] is not None:
                        # Calculate gain/loss based on remaining cost (actual investment)
                        gain_loss = current_value - remaining_cost
                        gain_loss_percent = (
                            current_price / data["purchase_price"] - 1
                        ) * 100

                        stock_info["gain_loss"] = gain_loss
                        stock_info["gain_loss_percent"] = gain_loss_percent

                    portfolio_data.append(stock_info)
            except Exception as e:
                print(f"Error getting data for {symbol}: {str(e)}")

        return portfolio_data

    def get_portfolio_performance(self, period="1y"):
        """
        Get historical portfolio performance data.

        Args:
            period (str): Time period

        Returns:
            pandas.DataFrame: DataFrame with portfolio value over time
        """
        if not self.stocks:
            return pd.DataFrame()

        symbols = list(self.stocks.keys())
        stock_data = get_multiple_stock_data(symbols, period)

        if stock_data.empty:
            return pd.DataFrame()

        # Calculate portfolio value over time
        portfolio_value = pd.DataFrame(index=stock_data.index)
        portfolio_value["Total"] = 0

        for symbol in symbols:
            if symbol in stock_data.columns:
                # Multiply price by number of shares
                shares = self.stocks[symbol]["shares"]
                portfolio_value[symbol] = stock_data[symbol] * shares
                portfolio_value["Total"] += portfolio_value[symbol]

        return portfolio_value

    def get_historical_performance(self, period="1y"):
        """
        Get historical performance data for the portfolio.

        Args:
            period (str): Time period to fetch data for

        Returns:
            pandas.DataFrame: DataFrame with historical portfolio value
        """
        if not self.stocks:
            return pd.DataFrame()

        symbols = list(self.stocks.keys())

        # Get historical data for all stocks in the portfolio
        all_data = get_multiple_stock_data(symbols, period)

        if all_data.empty:
            return pd.DataFrame()

        # Calculate daily portfolio value
        portfolio_value = pd.DataFrame(index=all_data.index)
        portfolio_value["Total"] = 0

        for symbol in symbols:
            shares = self.stocks[symbol]["shares"]

            if symbol in all_data.columns:
                portfolio_value[symbol] = all_data[symbol] * shares
                portfolio_value["Total"] += portfolio_value[symbol]

        return portfolio_value

    def get_portfolio_summary(self):
        """
        Get a summary of the portfolio.

        Returns:
            dict: Dictionary with portfolio summary data
        """
        # Default empty summary
        empty_summary = {
            "total_value": 0,
            "gain_loss": 0,
            "gain_loss_percent": 0,
            "total_realized_profit": 0,
            "overall_profit": 0,  # Combined realized and unrealized profit
        }

        # If no current stocks but we have realized profits
        if not self.stocks and self.realized_profits:
            total_realized_profit = sum(self.realized_profits.values())
            empty_summary["total_realized_profit"] = total_realized_profit
            empty_summary["overall_profit"] = total_realized_profit
            return empty_summary

        # If no stocks and no realized profits
        if not self.stocks:
            return empty_summary

        # Get current portfolio data
        portfolio_data = self.get_portfolio_data()

        # Calculate current total value
        total_value = sum(stock["current_value"] for stock in portfolio_data)

        # Calculate the actual remaining investment (not including costs of sold shares)
        total_cost = sum(
            self.stocks[stock["symbol"]].get(
                "remaining_cost", stock["purchase_price"] * stock["shares"]
            )
            for stock in portfolio_data
            if stock["purchase_price"] is not None
        )

        # Calculate unrealized gain/loss
        if total_cost > 0:
            gain_loss = total_value - total_cost
            gain_loss_percent = (gain_loss / total_cost) * 100
        else:
            gain_loss = 0
            gain_loss_percent = 0

        # Calculate total realized profit from sold shares
        total_realized_profit = (
            sum(self.realized_profits.values()) if self.realized_profits else 0
        )

        # Calculate overall profit (realized + unrealized)
        overall_profit = total_realized_profit + gain_loss

        return {
            "total_value": total_value,
            "gain_loss": gain_loss,  # Unrealized gain/loss on current holdings
            "gain_loss_percent": gain_loss_percent,
            "total_realized_profit": total_realized_profit,  # Profit from sold shares
            "overall_profit": overall_profit,  # Combined profit
        }

    def import_from_json(self, file_path):
        """
        Import portfolio from a JSON file.

        Args:
            file_path (str): Path to the JSON file

        Returns:
            bool: True if import was successful, False otherwise
        """
        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # Clear current portfolio
            self.stocks = {}
            self.transactions = {}
            self.realized_profits = {}

            # Process each stock and its transactions
            for symbol, transactions in data.items():
                self.transactions[symbol] = transactions

                # Calculate total shares and current position
                total_shares = 0
                total_cost = 0
                total_realized_profit = 0
                running_avg_cost = 0  # Keep track of running average cost basis
                shares_owned = 0  # Keep track of shares owned at each step

                # First pass: Calculate running cost basis and track all buys
                buy_transactions = []
                for transaction in transactions:
                    action, date, shares, price = transaction
                    shares = float(shares)
                    price = float(price)

                    if action.lower() == "bought":
                        buy_transactions.append((shares, price))

                        # Calculate new average cost basis
                        if shares_owned > 0:
                            # If we already own shares, calculate weighted average
                            old_value = shares_owned * running_avg_cost
                            new_value = shares * price
                            new_total_shares = shares_owned + shares
                            running_avg_cost = (
                                old_value + new_value
                            ) / new_total_shares
                        else:
                            # First purchase
                            running_avg_cost = price

                        shares_owned += shares
                        total_shares += shares
                        total_cost += shares * price

                    elif action.lower() == "sold":
                        if shares_owned >= shares:
                            # Calculate realized profit from this sale
                            cost_basis = running_avg_cost * shares
                            sale_proceeds = price * shares
                            realized_profit = sale_proceeds - cost_basis

                            # Add to total realized profit
                            total_realized_profit += realized_profit

                            # Update shares owned
                            shares_owned -= shares
                            total_shares -= shares

                            # Note: We keep the same running_avg_cost when selling
                        else:
                            print(
                                f"Warning: Attempting to sell more shares ({shares}) than owned ({shares_owned}) for {symbol}"
                            )

                # Store realized profits for this symbol
                if total_realized_profit != 0:
                    self.realized_profits[symbol] = total_realized_profit

                # Calculate the true remaining cost basis after sales
                # This is what we actually have invested in remaining shares
                remaining_cost = total_shares * running_avg_cost

                # Only add to portfolio if we still have shares
                if total_shares > 0:
                    self.stocks[symbol] = {
                        "shares": total_shares,
                        "purchase_price": running_avg_cost,
                        "remaining_cost": remaining_cost,  # Track actual remaining cost
                    }

            return True
        except Exception as e:
            print(f"Error importing portfolio: {str(e)}")
            return False

    def get_available_portfolios(self, directory="PersonalPortfolios"):
        """
        Get list of available portfolio JSON files.

        Args:
            directory (str): Directory containing portfolio JSON files

        Returns:
            list: List of portfolio file paths
        """
        try:
            # Get absolute path
            base_dir = os.path.dirname(os.path.abspath(__file__))
            portfolios_dir = os.path.join(base_dir, directory)

            # List all JSON files
            portfolio_files = glob.glob(os.path.join(portfolios_dir, "*.json"))
            return portfolio_files
        except Exception as e:
            print(f"Error listing portfolios: {str(e)}")
            return []

    def get_performance_metrics(self):
        """
        Calculate detailed performance metrics for the portfolio based on transaction history.

        Returns:
            dict: Dictionary with performance metrics
        """
        metrics = {
            "total_invested": 0,
            "total_current_value": 0,
            "total_gain_loss": 0,
            "total_gain_loss_pct": 0,
            "total_realized_profit": 0,  # Add total realized profit field
            "stocks_metrics": [],
        }

        # Process each stock with transactions
        for symbol in self.transactions:
            if symbol not in self.stocks:
                continue

            # Get current stock data
            df = get_stock_data(symbol, period="1y")
            if df.empty:
                continue

            current_price = df["Close"].iloc[-1]
            shares = self.stocks[symbol]["shares"]

            # Calculate metrics for this stock
            transactions = self.transactions[symbol]
            initial_investment = 0
            earliest_date = None

            for transaction in transactions:
                action, date, shares_traded, price = transaction

                if action.lower() == "bought":
                    initial_investment += float(shares_traded) * float(price)

                    # Track earliest purchase date
                    transaction_date = dt.datetime.strptime(date, "%Y-%m-%d")
                    if earliest_date is None or transaction_date < earliest_date:
                        earliest_date = transaction_date

            # Calculate current value
            current_value = shares * current_price

            # Get the actual remaining investment after sales
            purchase_price = self.stocks[symbol]["purchase_price"]
            remaining_cost = self.stocks[symbol].get(
                "remaining_cost", shares * purchase_price
            )

            # Calculate gain/loss based on the actual remaining investment
            gain_loss = current_value - remaining_cost
            gain_loss_pct = (
                (gain_loss / remaining_cost * 100) if remaining_cost > 0 else 0
            )

            # Calculate time-based performance if we have a valid earliest date
            time_based_metrics = {}
            if earliest_date:
                days_held = (dt.datetime.now() - earliest_date).days
                if days_held > 0:
                    annual_return = (
                        ((1 + gain_loss_pct / 100) ** (365 / days_held) - 1) * 100
                        if days_held > 0
                        else 0
                    )
                    time_based_metrics = {
                        "days_held": days_held,
                        "annual_return": annual_return,
                    }

            # Get realized profit for this symbol, if any
            realized_profit = self.realized_profits.get(symbol, 0)

            # Add stock metrics to the list
            metrics["stocks_metrics"].append(
                {
                    "symbol": symbol,
                    "shares": shares,
                    "current_price": current_price,
                    "current_value": current_value,
                    "initial_investment": initial_investment,
                    "gain_loss": gain_loss,
                    "gain_loss_pct": gain_loss_pct,
                    "realized_profit": realized_profit,  # Add realized profit to each stock's metrics
                    "earliest_date": earliest_date.strftime("%Y-%m-%d")
                    if earliest_date
                    else None,
                    **time_based_metrics,
                }
            )

            # Update total metrics
            metrics["total_invested"] += initial_investment
            metrics["total_current_value"] += current_value

        # Calculate the actual remaining investment (cost basis) for current holdings
        remaining_investment = sum(
            self.stocks[stock.get("symbol", "")].get("remaining_cost", 0)
            for stock in metrics["stocks_metrics"]
        )

        # Calculate total gain/loss based on remaining investment, not initial investment
        metrics["total_gain_loss"] = (
            metrics["total_current_value"] - remaining_investment
        )
        metrics["total_gain_loss_pct"] = (
            (metrics["total_gain_loss"] / remaining_investment * 100)
            if remaining_investment > 0
            else 0
        )

        # Update total_invested to reflect actual remaining investment
        metrics["total_invested"] = remaining_investment

        # Add realized profits to metrics
        metrics["total_realized_profit"] = (
            sum(self.realized_profits.values()) if self.realized_profits else 0
        )

        # Add realized profits by symbol
        metrics["realized_profits_by_symbol"] = (
            self.realized_profits.copy() if self.realized_profits else {}
        )

        return metrics
