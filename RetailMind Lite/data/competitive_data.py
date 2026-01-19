# data/competitive_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_competitive_data():
    """Generate simulated competitive pricing data"""
    np.random.seed(42)
    
    products = ['Milk', 'Bread', 'Eggs', 'Coffee', 'Bananas', 'Yogurt', 'Cereal']
    
    competitive_data = []
    
    for product in products:
        # Base prices
        your_price = np.random.uniform(1.5, 4.0)
        
        # Competitor prices with some variation
        competitor_price = your_price * np.random.uniform(0.9, 1.1)
        
        # Price gap percentage
        price_gap = ((your_price - competitor_price) / competitor_price) * 100
        
        # Market share simulation
        market_share = np.random.uniform(20, 50)
        
        # Price changes over last 7 days
        your_price_change = np.random.uniform(-2, 2)
        competitor_price_change = np.random.uniform(-3, 3)
        
        competitive_data.append({
            'product': product,
            'your_price': round(your_price, 2),
            'competitor_price': round(competitor_price, 2),
            'price_gap_%': round(price_gap, 1),
            'market_share': round(market_share, 1),
            'your_price_change_7d': round(your_price_change, 1),
            'competitor_price_change_7d': round(competitor_price_change, 1),
            'price_trend': 'INCREASING' if your_price_change > 0 else 'DECREASING' if your_price_change < 0 else 'STABLE',
            'competition_intensity': 'HIGH' if abs(price_gap) < 5 else 'MEDIUM' if abs(price_gap) < 15 else 'LOW'
        })
    
    df = pd.DataFrame(competitive_data)
    return df

def get_competitor_actions():
    """Simulate recent competitor actions"""
    actions = [
        {
            'competitor': 'MegaMart',
            'action': 'PRICE_CUT',
            'product': 'Milk',
            'amount': '-10%',
            'date': '2024-01-10',
            'impact': 'HIGH'
        },
        {
            'competitor': 'QuickStop',
            'action': 'PROMOTION',
            'product': 'Bread',
            'amount': 'Buy 1 Get 1 50% off',
            'date': '2024-01-09',
            'impact': 'MEDIUM'
        },
        {
            'competitor': 'FreshGrocer',
            'action': 'STOCKOUT',
            'product': 'Eggs',  
            'amount': 'Out of stock',
            'date': '2024-01-08',
            'impact': 'HIGH'
        },
        {
            'competitor': 'ValueMart',
            'action': 'NEW_PRODUCT',
            'product': 'Organic Yogurt',
            'amount': 'New line introduced',
            'date': '2024-01-07',
            'impact': 'LOW'
        }
    ]
    
    return pd.DataFrame(actions)