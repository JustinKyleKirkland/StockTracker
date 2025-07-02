#!/usr/bin/env python3
"""
Launcher script for Stock Tracker application.
"""

from app import app, portfolio
from profit_analysis import (
    register_profit_callbacks,
    create_export_transactions_callback,
)
import os
import platform

if __name__ == "__main__":
    # Clear the terminal
    os.system("cls" if platform.system() == "Windows" else "clear")

    # Display a nice startup message
    print("\033[1;36m" + "=" * 60 + "\033[0m")
    print("\033[1;36m║\033[0m" + " " * 58 + "\033[1;36m║\033[0m")
    print(
        "\033[1;36m║\033[0m"
        + "\033[1;33m        🚀  STOCK TRACKER APPLICATION STARTING...  🚀        \033[0m"
        + "\033[1;36m║\033[0m"
    )
    print("\033[1;36m║\033[0m" + " " * 58 + "\033[1;36m║\033[0m")
    print("\033[1;36m" + "=" * 60 + "\033[0m")
    print("\n\033[1;32m✓ Opening server at:\033[0m http://127.0.0.1:8050/")
    print("\n\033[1;34mFeatures:\033[0m")
    print("  • Stock visualization with real-time data")
    print("  • Portfolio management with performance tracking")
    print("  • Multi-stock comparison and correlation analysis")
    print("  • Profit breakdown and transaction history")
    print("  • Dark mode toggle for comfortable viewing")
    print("\n\033[1;35mPress Ctrl+C to stop the server\033[0m\n")

    # Register the profit analysis and export transaction callbacks
    register_profit_callbacks(app, portfolio)
    create_export_transactions_callback(app, portfolio)

    # Run the app
    app.run(debug=True)
