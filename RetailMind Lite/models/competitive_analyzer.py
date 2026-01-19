# models/competitive_analyzer.py
import pandas as pd
import numpy as np

class CompetitiveAnalyzer:
    """Analyzes how competitor price changes affect your demand"""
    
    def __init__(self):
        self.price_elasticity = {
            'Milk': 1.2, 'Bread': 0.8, 'Eggs': 1.5, 
            'Coffee': 0.5, 'Bananas': 2.1, 'Yogurt': 1.0, 'Cereal': 0.9
        }
    
    def analyze_competitive_position(self, product_data):
        """Analyze competitive position for all products"""
        print("\n" + "="*60)
        print("COMPETITIVE PRICE SENSITIVITY ANALYZER")
        print("="*60)
        
        # Simulated competitive data (in real app, this would come from API)
        competitor_data = {
            'product': ['Milk', 'Bread', 'Eggs', 'Coffee', 'Bananas', 'Yogurt', 'Cereal'],
            'your_price': [3.99, 2.49, 2.99, 8.99, 0.69, 1.49, 3.49],
            'competitor_price': [3.89, 2.79, 3.19, 9.49, 0.59, 1.39, 3.79],
            'price_gap_%': [2.5, -10.8, -6.3, -5.3, 16.9, 7.2, -7.9],
            'market_share': [28, 32, 25, 40, 45, 22, 35]
        }
        
        comp_df = pd.DataFrame(competitor_data)
        
        # Calculate demand impact using price elasticity
        comp_df['demand_shift_%'] = comp_df.apply(
            lambda row: self.price_elasticity.get(row['product'], 1.0) * row['price_gap_%'] * -0.1, 
            axis=1
        )
        
        # Classify competitive position
        def get_competitive_position(row):
            if row['demand_shift_%'] < -5:
                return "🟥 Losing Share"
            elif row['demand_shift_%'] > 5:
                return "🟩 Gaining Share"
            elif row['demand_shift_%'] > 0:
                return "🟨 Slightly Ahead"
            else:
                return "⬜️ Neutral"
        
        comp_df['position'] = comp_df.apply(get_competitive_position, axis=1)
        
        # Generate pricing recommendations
        recommendations = []
        for _, row in comp_df.iterrows():
            elasticity = self.price_elasticity.get(row['product'], 1.0)
            
            if row['position'] == "🟥 Losing Share":
                if elasticity > 1.0:  # Price sensitive
                    rec = {
                        'product': row['product'],
                        'action': 'MATCH_PRICE',
                        'reason': f"Competitor undercutting by {abs(row['price_gap_%']):.1f}%",
                        'impact': f"Regain {abs(row['demand_shift_%']):.1f}% demand",
                        'priority': 'HIGH'
                    }
                else:
                    rec = {
                        'product': row['product'],
                        'action': 'VALUE_ADD',
                        'reason': "Low price sensitivity",
                        'impact': "Focus on quality/bundling instead",
                        'priority': 'MEDIUM'
                    }
                recommendations.append(rec)
                
            elif row['position'] == "🟩 Gaining Share":
                rec = {
                    'product': row['product'],
                    'action': 'MAINTAIN_OR_INCREASE',
                    'reason': f"Price advantage of {row['price_gap_%']:.1f}%",
                    'impact': f"Could raise price by {min(2, row['price_gap_%']/2):.1f}%",
                    'priority': 'LOW'
                }
                recommendations.append(rec)
        
        return {
            'analysis_df': comp_df,
            'recommendations': recommendations,
            'summary': {
                'losing_share': len(comp_df[comp_df['position'] == "🟥 Losing Share"]),
                'gaining_share': len(comp_df[comp_df['position'] == "🟩 Gaining Share"]),
                'avg_price_gap': comp_df['price_gap_%'].mean()
            }
        }
    
    def simulate_competitor_price_change(self, product, competitor_price_change_pct):
        """Simulate impact of competitor price change on your demand"""
        elasticity = self.price_elasticity.get(product, 1.0)
        
        # If competitor raises price, you gain demand (negative change for them = positive for you)
        demand_impact = elasticity * competitor_price_change_pct * -1.0
        
        return {
            'product': product,
            'competitor_price_change': competitor_price_change_pct,
            'your_demand_change': demand_impact,
            'interpretation': f"If competitor {'raises' if competitor_price_change_pct > 0 else 'lowers'} price by {abs(competitor_price_change_pct)}%, "
                            f"your demand will {'increase' if demand_impact > 0 else 'decrease'} by {abs(demand_impact):.1f}%"
        }