# data/generate_data.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_retail_dataset():
    """Generate realistic synthetic retail data for 2 years"""
    np.random.seed(42)
    
    # Date range: Last 2 years
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Products with different characteristics
    products = {
        'Milk': {'base': 80, 'trend': 0.01, 'seasonality': 1.2, 'weekly_boost': 1.3},
        'Bread': {'base': 60, 'trend': 0.02, 'seasonality': 1.1, 'weekly_boost': 1.4},
        'Eggs': {'base': 40, 'trend': 0.03, 'seasonality': 1.3, 'weekly_boost': 1.2},
        'Coffee': {'base': 25, 'trend': 0.015, 'seasonality': 0.9, 'weekly_boost': 1.1},
        'Bananas': {'base': 55, 'trend': 0.01, 'seasonality': 1.1, 'weekly_boost': 1.25},
        'Yogurt': {'base': 35, 'trend': -0.005, 'seasonality': 1.0, 'weekly_boost': 1.15},
        'Cereal': {'base': 30, 'trend': -0.01, 'seasonality': 0.95, 'weekly_boost': 1.1}
    }
    
    records = []
    
    for date in dates:
        # Market signals
        weather_score = 0.8 + 0.4 * np.sin(date.dayofyear / 365 * 2 * np.pi)  # Seasonal
        event_flag = 1 if (date.month == 12 and date.day < 25) or (date.month == 7 and date.day < 7) else 0
        
        for product, params in products.items():
            # Base sales with trend
            base = params['base'] * (1 + params['trend'] * (date - start_date).days / 365)
            
            # Seasonality (higher in winter for some products)
            month_factor = 1 + 0.3 * np.sin(2 * np.pi * date.month / 12) * params['seasonality']
            
            # Day of week effect
            dow_factor = params['weekly_boost'] if date.weekday() >= 5 else 1.0  # Weekend boost
            
            # Random noise
            noise = np.random.normal(0, 0.15)  # 15% noise
            
            # Market impact
            market_impact = weather_score * (1 + 0.2 * event_flag)
            
            # Calculate final sales
            sales = max(5, int(base * month_factor * dow_factor * market_impact * (1 + noise)))
            
            # Inventory simulation (with some randomness)
            inventory = max(sales, int(sales * np.random.uniform(1.5, 3.0)))
            
            records.append({
                'date': date,
                'product': product,
                'sales': sales,
                'inventory': inventory,
                'weather_score': round(weather_score, 2),
                'event_flag': event_flag,
                'price': np.random.uniform(1.5, 4.0)  # Simulated price
            })
    
    df = pd.DataFrame(records)
    df['date'] = pd.to_datetime(df['date'])
    return df

if __name__ == "__main__":
    df = generate_retail_dataset()
    df.to_csv('data/retail_data.csv', index=False)
    print(f"Generated dataset with {len(df)} records")
    print(df.head())