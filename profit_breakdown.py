"""
Module for calculating detailed profit breakdowns for stock portfolios.
This provides enhanced analytics for realized and unrealized profits.
"""

import plotly.graph_objects as go
import plotly.express as px


def calculate_profit_breakdown(portfolio):
    """
    Calculate detailed profit breakdown for a portfolio by stock.

    Args:
        portfolio: Portfolio object with transactions and realized profits

    Returns:
        dict: Dictionary with profit breakdown data
    """
    if not portfolio.stocks and not portfolio.realized_profits:
        return None

    # Initialize breakdown data
    breakdown = {
        "by_stock": [],
        "summary": {
            "total_invested": 0,
            "current_value": 0,
            "total_realized": 0,
            "total_unrealized": 0,
            "total_profit": 0,
        },
        "historical": {"dates": [], "realized": [], "unrealized": []},
    }

    # Get portfolio data and metrics
    portfolio_data = portfolio.get_portfolio_data()
    metrics = portfolio.get_performance_metrics()
    realized_profits = portfolio.realized_profits

    # Build list of all symbols (current holdings + sold positions)
    all_symbols = set(list(portfolio.stocks.keys()))
    all_symbols.update(list(realized_profits.keys()))

    # Calculate profit breakdown by stock
    for symbol in all_symbols:
        stock_data = {}
        stock_data["symbol"] = symbol

        # Get transaction history for this symbol
        transactions = portfolio.transactions.get(symbol, [])

        # Initialize metrics
        stock_data["total_bought"] = 0
        stock_data["total_bought_value"] = 0
        stock_data["total_sold"] = 0
        stock_data["total_sold_value"] = 0
        stock_data["current_shares"] = 0
        stock_data["current_value"] = 0
        stock_data["realized_profit"] = realized_profits.get(symbol, 0)

        # Calculate transaction totals
        for action, date, shares, price in transactions:
            shares = float(shares)
            price = float(price)

            if action.lower() == "bought":
                stock_data["total_bought"] += shares
                stock_data["total_bought_value"] += shares * price
            elif action.lower() == "sold":
                stock_data["total_sold"] += shares
                stock_data["total_sold_value"] += shares * price

        # Get current holdings data
        if symbol in portfolio.stocks:
            stock_info = next(
                (s for s in portfolio_data if s["symbol"] == symbol), None
            )
            if stock_info:
                stock_data["current_shares"] = stock_info["shares"]
                stock_data["current_value"] = stock_info["current_value"]
                stock_data["current_price"] = stock_info["current_price"]
                stock_data["unrealized_profit"] = stock_info.get("gain_loss", 0)
            else:
                stock_data["current_shares"] = portfolio.stocks[symbol]["shares"]
                stock_data["current_value"] = 0
                stock_data["current_price"] = 0
                stock_data["unrealized_profit"] = 0
        else:
            # No current holdings
            stock_data["current_shares"] = 0
            stock_data["current_value"] = 0
            stock_data["current_price"] = 0
            stock_data["unrealized_profit"] = 0

        # Calculate profit metrics
        stock_data["total_profit"] = (
            stock_data["realized_profit"] + stock_data["unrealized_profit"]
        )
        stock_data["profit_pct"] = (
            (stock_data["total_profit"] / stock_data["total_bought_value"] * 100)
            if stock_data["total_bought_value"] > 0
            else 0
        )

        # Calculate profit per share
        stock_data["average_cost"] = (
            (stock_data["total_bought_value"] / stock_data["total_bought"])
            if stock_data["total_bought"] > 0
            else 0
        )

        # Calculate ROI
        initial_investment = (
            stock_data["total_bought_value"] - stock_data["total_sold_value"]
        )
        if initial_investment > 0:
            stock_data["roi"] = (stock_data["total_profit"] / initial_investment) * 100
        else:
            stock_data["roi"] = 0

        # Add to breakdown
        breakdown["by_stock"].append(stock_data)

    # Sort stocks by total profit descending
    breakdown["by_stock"].sort(key=lambda x: x["total_profit"], reverse=True)

    # Calculate summary metrics
    breakdown["summary"]["total_invested"] = metrics["total_invested"]
    breakdown["summary"]["current_value"] = metrics["total_current_value"]
    breakdown["summary"]["total_realized"] = metrics.get("total_realized_profit", 0)
    breakdown["summary"]["total_unrealized"] = metrics["total_gain_loss"]
    breakdown["summary"]["total_profit"] = (
        breakdown["summary"]["total_realized"]
        + breakdown["summary"]["total_unrealized"]
    )

    # Calculate profit ratio
    if breakdown["summary"]["total_profit"] != 0:
        realized_ratio = (
            breakdown["summary"]["total_realized"]
            / breakdown["summary"]["total_profit"]
            if breakdown["summary"]["total_profit"] != 0
            else 0
        )
        unrealized_ratio = (
            breakdown["summary"]["total_unrealized"]
            / breakdown["summary"]["total_profit"]
            if breakdown["summary"]["total_profit"] != 0
            else 0
        )
        breakdown["summary"]["realized_ratio"] = realized_ratio
        breakdown["summary"]["unrealized_ratio"] = unrealized_ratio

    return breakdown


def generate_profit_breakdown_chart(breakdown):
    """
    Generate a chart showing profit breakdown by stock

    Args:
        breakdown: Result of calculate_profit_breakdown()

    Returns:
        plotly.graph_objects.Figure: Chart showing profit breakdown
    """
    if not breakdown or not breakdown["by_stock"]:
        # Return empty figure if no data
        return go.Figure()

    # Prepare data for visualization
    symbols = [stock["symbol"] for stock in breakdown["by_stock"]]
    realized = [stock["realized_profit"] for stock in breakdown["by_stock"]]
    unrealized = [stock["unrealized_profit"] for stock in breakdown["by_stock"]]

    # Create grouped bar chart
    fig = go.Figure()

    fig.add_trace(
        go.Bar(x=symbols, y=realized, name="Realized Profit", marker_color="#00c853")
    )

    fig.add_trace(
        go.Bar(
            x=symbols, y=unrealized, name="Unrealized Profit", marker_color="#536dfe"
        )
    )

    # Add total profit line
    fig.add_trace(
        go.Scatter(
            x=symbols,
            y=[stock["total_profit"] for stock in breakdown["by_stock"]],
            mode="markers+lines",
            name="Total Profit",
            marker_color="#ff9800",
        )
    )

    # Update layout
    fig.update_layout(
        title="Profit Breakdown by Stock",
        xaxis_title="Stock",
        yaxis_title="Profit (USD)",
        barmode="group",
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )

    return fig


def generate_profit_pie_chart(breakdown):
    """
    Generate a pie chart showing profit contribution by stock

    Args:
        breakdown: Result of calculate_profit_breakdown()

    Returns:
        plotly.graph_objects.Figure: Pie chart showing profit contribution
    """
    if not breakdown or not breakdown["by_stock"]:
        # Return empty figure if no data
        return go.Figure()

    # Filter to only stocks with positive profit
    profitable_stocks = [
        stock for stock in breakdown["by_stock"] if stock["total_profit"] > 0
    ]

    if not profitable_stocks:
        return go.Figure()

    # Prepare data for visualization
    labels = [stock["symbol"] for stock in profitable_stocks]
    values = [stock["total_profit"] for stock in profitable_stocks]

    # Create pie chart
    fig = px.pie(
        names=labels,
        values=values,
        title="Profit Contribution by Stock",
        hole=0.4,
    )

    # Update layout
    fig.update_layout(
        height=500,
        legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
    )

    return fig


def generate_profit_tables(breakdown):
    """
    Generate HTML tables for profit breakdown

    Args:
        breakdown: Result of calculate_profit_breakdown()

    Returns:
        dict: Dictionary with HTML tables for different views
    """
    from dash import html

    if not breakdown or not breakdown["by_stock"]:
        return {
            "realized": html.P("No profit data available."),
            "unrealized": html.P("No profit data available."),
            "combined": html.P("No profit data available."),
        }

    # Create realized profit table (for stocks with realized profit)
    realized_stocks = [
        stock for stock in breakdown["by_stock"] if stock["realized_profit"] != 0
    ]
    if realized_stocks:
        realized_header = html.Thead(
            html.Tr(
                [
                    html.Th("Symbol"),
                    html.Th("Shares Sold"),
                    html.Th("Sale Value"),
                    html.Th("Realized Profit"),
                    html.Th("ROI %"),
                ]
            )
        )

        realized_rows = []
        for stock in realized_stocks:
            profit_class = (
                "positive-value" if stock["realized_profit"] >= 0 else "negative-value"
            )
            roi_class = "positive-value" if stock["roi"] >= 0 else "negative-value"

            row = html.Tr(
                [
                    html.Td(stock["symbol"]),
                    html.Td(f"{stock['total_sold']:.2f}"),
                    html.Td(f"${stock['total_sold_value']:.2f}"),
                    html.Td(f"${stock['realized_profit']:.2f}", className=profit_class),
                    html.Td(f"{stock['roi']:.2f}%", className=roi_class),
                ]
            )
            realized_rows.append(row)

        realized_table = html.Table(
            [realized_header, html.Tbody(realized_rows)],
            className="profit-breakdown-table",
        )
    else:
        realized_table = html.P("No realized profits yet.")

    # Create unrealized profit table (for current holdings)
    unrealized_stocks = [
        stock for stock in breakdown["by_stock"] if stock["current_shares"] > 0
    ]
    if unrealized_stocks:
        unrealized_header = html.Thead(
            html.Tr(
                [
                    html.Th("Symbol"),
                    html.Th("Current Shares"),
                    html.Th("Current Value"),
                    html.Th("Unrealized Profit"),
                    html.Th("Profit %"),
                ]
            )
        )

        unrealized_rows = []
        for stock in unrealized_stocks:
            profit_class = (
                "positive-value"
                if stock["unrealized_profit"] >= 0
                else "negative-value"
            )

            row = html.Tr(
                [
                    html.Td(stock["symbol"]),
                    html.Td(f"{stock['current_shares']:.2f}"),
                    html.Td(f"${stock['current_value']:.2f}"),
                    html.Td(
                        f"${stock['unrealized_profit']:.2f}", className=profit_class
                    ),
                    html.Td(
                        f"{stock['profit_pct']:.2f}%",
                        className=profit_class
                        if stock["profit_pct"] >= 0
                        else "negative-value",
                    ),
                ]
            )
            unrealized_rows.append(row)

        unrealized_table = html.Table(
            [unrealized_header, html.Tbody(unrealized_rows)],
            className="profit-breakdown-table",
        )
    else:
        unrealized_table = html.P("No current holdings.")

    # Create combined profit table (all stocks)
    combined_header = html.Thead(
        html.Tr(
            [
                html.Th("Symbol"),
                html.Th("Total Profit"),
                html.Th("Realized"),
                html.Th("Unrealized"),
                html.Th("ROI %"),
            ]
        )
    )

    combined_rows = []
    for stock in breakdown["by_stock"]:
        profit_class = (
            "positive-value" if stock["total_profit"] >= 0 else "negative-value"
        )
        realized_class = (
            "positive-value" if stock["realized_profit"] >= 0 else "negative-value"
        )
        unrealized_class = (
            "positive-value" if stock["unrealized_profit"] >= 0 else "negative-value"
        )
        roi_class = "positive-value" if stock["roi"] >= 0 else "negative-value"

        row = html.Tr(
            [
                html.Td(stock["symbol"]),
                html.Td(f"${stock['total_profit']:.2f}", className=profit_class),
                html.Td(f"${stock['realized_profit']:.2f}", className=realized_class),
                html.Td(
                    f"${stock['unrealized_profit']:.2f}", className=unrealized_class
                ),
                html.Td(f"{stock['roi']:.2f}%", className=roi_class),
            ]
        )
        combined_rows.append(row)

    combined_table = html.Table(
        [combined_header, html.Tbody(combined_rows)], className="profit-breakdown-table"
    )

    return {
        "realized": realized_table,
        "unrealized": unrealized_table,
        "combined": combined_table,
    }
