"""
News data retrieval for Stock Tracker application.
"""
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

def get_stock_news(symbols, max_news=5):
    """
    Fetch news for given stock symbols.
    
    Args:
        symbols (str or list): Stock ticker symbol(s)
        max_news (int): Maximum number of news items to return
    
    Returns:
        list: List of news items with title, publisher, url, and published date
    """
    # Convert single symbol to list
    if isinstance(symbols, str):
        symbols = [symbols]
    
    all_news = []
    
    try:
        # Get news for each symbol
        for symbol in symbols:
            ticker = yf.Ticker(symbol)
            news_data = ticker.news
            
            if news_data:
                # Process news data
                for item in news_data[:max_news]:
                    # Convert timestamp to readable date
                    if 'providerPublishTime' in item:
                        timestamp = item['providerPublishTime']
                        published_date = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M')
                    else:
                        published_date = "N/A"
                    
                    # Create news item dictionary
                    news_item = {
                        'title': item.get('title', 'No Title'),
                        'publisher': item.get('publisher', 'Unknown'),
                        'url': item.get('link', '#'),
                        'published': published_date,
                        'symbol': symbol,
                        'thumbnail': item.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', '') if 'thumbnail' in item else ''
                    }
                    all_news.append(news_item)
        
        # Sort news by published date (newest first) and limit to max_news
        all_news = sorted(all_news, key=lambda x: x['published'], reverse=True)[:max_news]
        
        return all_news
    except Exception as e:
        print(f"Error fetching news: {str(e)}")
        return []
