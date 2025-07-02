"""
Module for the profit analysis tab in the Stock Tracker app.
This separates profit analysis functionality from the main app for better organization.
"""

from dash import html, Output, Input
import plotly.graph_objs as go
import pandas as pd
import datetime as dt

from profit_breakdown import calculate_profit_breakdown, generate_profit_breakdown_chart
from profit_breakdown import generate_profit_pie_chart, generate_profit_tables


def register_profit_callbacks(app, portfolio):
    """
    Register all callbacks for the profit analysis tab

    Args:
        app (dash.Dash): The Dash app
        portfolio (Portfolio): The portfolio instance
    """

    # Callback for profit overview
    @app.callback(
        Output("profit-overview-cards", "children"),
        [
            Input("tabs", "value"),
            Input("profit-auto-update-interval", "n_intervals"),
            Input("import-portfolio-button", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def update_profit_overview(tab_value, n_intervals, import_clicks):
        """Update the profit overview cards"""
        if not portfolio.stocks and not portfolio.realized_profits:
            return html.P("No profit data available. Import a portfolio or add stocks.")

        # Calculate profit breakdown
        breakdown = calculate_profit_breakdown(portfolio)
        if not breakdown:
            return html.P("No profit data available.")

        # Extract summary data
        summary = breakdown["summary"]

        # Create cards
        cards = []

        # Total profit card
        total_profit = summary["total_profit"]
        total_profit_class = "positive-value" if total_profit >= 0 else "negative-value"
        cards.append(
            html.Div(
                [
                    html.H4("Total Profit"),
                    html.Div(f"${total_profit:.2f}", className=total_profit_class),
                ],
                className="summary-card",
            )
        )

        # Realized profit card
        realized_profit = summary["total_realized"]
        realized_class = "positive-value" if realized_profit >= 0 else "negative-value"
        cards.append(
            html.Div(
                [
                    html.H4("Realized Profit"),
                    html.Div(f"${realized_profit:.2f}", className=realized_class),
                ],
                className="summary-card",
            )
        )

        # Unrealized profit card
        unrealized_profit = summary["total_unrealized"]
        unrealized_class = (
            "positive-value" if unrealized_profit >= 0 else "negative-value"
        )
        cards.append(
            html.Div(
                [
                    html.H4("Unrealized Profit"),
                    html.Div(f"${unrealized_profit:.2f}", className=unrealized_class),
                ],
                className="summary-card",
            )
        )

        # Realized/Unrealized ratio card (if there's profit)
        if total_profit != 0:
            realized_ratio = summary.get("realized_ratio", 0) * 100
            unrealized_ratio = summary.get("unrealized_ratio", 0) * 100
            cards.append(
                html.Div(
                    [
                        html.H4("Profit Ratio"),
                        html.Div(
                            [
                                html.Span(f"Realized: {realized_ratio:.1f}% | "),
                                html.Span(f"Unrealized: {unrealized_ratio:.1f}%"),
                            ]
                        ),
                    ],
                    className="summary-card",
                )
            )

        # Return cards in a container
        return html.Div(cards, className="summary-cards-container")

    # Callback for profit breakdown content
    @app.callback(
        Output("profit-breakdown-content", "children"),
        [
            Input("profit-breakdown-tabs", "value"),
            Input("profit-auto-update-interval", "n_intervals"),
            Input("import-portfolio-button", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def update_profit_breakdown(tab_value, n_intervals, import_clicks):
        """Update the profit breakdown tables based on selected tab"""
        if not portfolio.stocks and not portfolio.realized_profits:
            return html.P("No profit data available. Import a portfolio or add stocks.")

        # Calculate profit breakdown
        breakdown = calculate_profit_breakdown(portfolio)
        if not breakdown:
            return html.P("No profit data available.")

        # Generate tables
        tables = generate_profit_tables(breakdown)

        # Return appropriate table based on selected tab
        if tab_value == "tab-realized":
            return html.Div([html.H4("Realized Profit Breakdown"), tables["realized"]])
        elif tab_value == "tab-unrealized":
            return html.Div(
                [html.H4("Unrealized Profit Breakdown"), tables["unrealized"]]
            )
        else:  # Combined view
            return html.Div([html.H4("Combined Profit Breakdown"), tables["combined"]])

    # Callback for profit charts
    @app.callback(
        Output("profit-chart", "figure"),
        [
            Input("profit-chart-tabs", "value"),
            Input("profit-auto-update-interval", "n_intervals"),
            Input("import-portfolio-button", "n_clicks"),
        ],
        prevent_initial_call=True,
    )
    def update_profit_charts(chart_type, n_intervals, import_clicks):
        """Update the profit charts based on selected type"""
        if not portfolio.stocks and not portfolio.realized_profits:
            # Return empty figure with message
            return {
                "data": [],
                "layout": go.Layout(title="No profit data available", height=500),
            }

        # Calculate profit breakdown
        breakdown = calculate_profit_breakdown(portfolio)
        if not breakdown:
            return {
                "data": [],
                "layout": go.Layout(title="No profit data available", height=500),
            }

        # Generate appropriate chart
        if chart_type == "chart-pie":
            return generate_profit_pie_chart(breakdown)
        else:  # Breakdown chart
            return generate_profit_breakdown_chart(breakdown)


def create_export_transactions_callback(app, portfolio):
    """
    Create callback for exporting transactions to CSV

    Args:
        app (dash.Dash): The Dash app
        portfolio (Portfolio): The portfolio instance
    """

    @app.callback(
        Output("download-transaction-csv", "data"),
        Input("export-transactions-btn", "n_clicks"),
        prevent_initial_call=True,
    )
    def export_transactions_csv(n_clicks):
        """
        Export transaction history to a CSV file when the export button is clicked.
        """
        if n_clicks is None or n_clicks == 0:
            return None

        # If no transactions, return empty
        if not portfolio.transactions:
            return None

        # Convert transactions to a pandas DataFrame for easy CSV export
        transactions_data = []

        for symbol, transactions in portfolio.transactions.items():
            for transaction in transactions:
                action, date, shares, price = transaction
                shares_float = float(shares)
                price_float = float(price)
                total_value = shares_float * price_float

                # Calculate profit for sell transactions if possible
                profit = None
                if action.lower() == "sold" and symbol in portfolio.realized_profits:
                    # Find the specific profit for this transaction
                    for tx in portfolio.transactions.get(symbol, []):
                        tx_action, tx_date, tx_shares, tx_price = tx
                        if (
                            tx_date == date
                            and float(tx_shares) == shares_float
                            and float(tx_price) == price_float
                            and tx_action.lower() == "sold"
                        ):
                            # Use the realized profit per share for this symbol
                            symbol_total_sold_shares = sum(
                                float(s)
                                for a, _, s, _ in portfolio.transactions.get(symbol, [])
                                if a.lower() == "sold"
                            )
                            if symbol_total_sold_shares > 0:
                                profit_per_share = (
                                    portfolio.realized_profits.get(symbol, 0)
                                    / symbol_total_sold_shares
                                )
                                profit = profit_per_share * shares_float
                            break

                transactions_data.append(
                    {
                        "Date": date,
                        "Symbol": symbol,
                        "Action": action,
                        "Shares": shares_float,
                        "Price": price_float,
                        "Total Value": total_value,
                        "Profit/Loss": profit if profit is not None else "",
                    }
                )

        # Sort by date, newest first
        transactions_data.sort(
            key=lambda x: dt.datetime.strptime(x["Date"], "%Y-%m-%d"), reverse=True
        )

        # Create DataFrame
        df = pd.DataFrame(transactions_data)

        # Generate filename with current date and time
        current_time = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"stock_transactions_{current_time}.csv"

        # Return a dict that the Download component can use
        return dict(content=df.to_csv(index=False), filename=filename, type="text/csv")
