# models/risk_engine.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class RiskOpportunityEngine:
    """AI-powered product risk and opportunity classifier"""
    
    def __init__(self):
        self.thresholds = {
            'high_risk_trend': -10,  # % weekly decline
            'high_opportunity_trend': 15,  # % weekly growth
            'overstock_threshold': 25,  # days of inventory
            'understock_threshold': 7,   # days of inventory
            'high_volatility': 0.4,      # coefficient of variation
            'low_volatility': 0.2
        }
    
    def calculate_metrics(self, product_data):
        """Calculate key metrics for risk assessment"""
        recent = product_data.tail(30)
        
        metrics = {
            'product': product_data['product'].iloc[0],
            'current_avg': recent['sales'].mean(),
            'trend_7d': self._calculate_trend(recent, 7),
            'trend_30d': self._calculate_trend(recent, 30),
            'volatility': recent['sales'].std() / recent['sales'].mean() if recent['sales'].mean() > 0 else 0,
            'days_of_stock': (recent['inventory'].mean() / recent['sales'].mean()) if recent['sales'].mean() > 0 else 0,
            'stockout_risk': self._calculate_stockout_risk(recent),
            'price_stability': 1 - (recent['price'].std() / recent['price'].mean()) if recent['price'].mean() > 0 else 1
        }
        return metrics
    
    def _calculate_trend(self, data, days):
        """Calculate % change over specified period"""
        if len(data) < days:
            return 0
        
        recent = data['sales'].tail(days)
        older = data['sales'].iloc[-days*2:-days] if len(data) >= days*2 else data['sales'].iloc[:days]
        
        if len(older) == 0 or older.mean() == 0:
            return 0
        
        return ((recent.mean() - older.mean()) / older.mean()) * 100
    
    def _calculate_stockout_risk(self, recent_data):
        """Calculate probability of stockout"""
        sales_std = recent_data['sales'].std()
        sales_mean = recent_data['sales'].mean()
        inventory_mean = recent_data['inventory'].mean()
        
        if sales_mean == 0:
            return 0
        
        # Simplified stockout probability
        z_score = (inventory_mean - sales_mean) / (sales_std + 1e-6)
        risk = max(0, min(1, 0.5 - 0.2 * z_score))  # Normal distribution approximation
        return risk

    def classify_product_v2(self, metrics, forecast_growth):
        """Enhanced classification with 3-color system and trend arrows"""
        
        # Calculate enhanced risk score (0-100)
        risk_score = 0
        opportunity_score = 0
        
        # RISK FACTORS (adds to red score)
        if metrics['trend_7d'] < -10:
            risk_score += 30
        if metrics['days_of_stock'] > 25:
            risk_score += 25
        if metrics['stockout_risk'] > 0.3:
            risk_score += 20
        if metrics['volatility'] > 0.4:
            risk_score += 15
        
        # OPPORTUNITY FACTORS (adds to green score)
        if metrics['trend_7d'] > 15:
            opportunity_score += 30
        if metrics['days_of_stock'] < 7:
            opportunity_score += 25
        if forecast_growth > 10:
            opportunity_score += 20
        if metrics['volatility'] < 0.2 and metrics['trend_7d'] > 5:
            opportunity_score += 15
        
        # Determine category
        if risk_score >= 60 and opportunity_score < 30:
            category = "HIGH RISK"
            color = "red"
            icon = "🔴"
            priority = 1
        elif opportunity_score >= 60 and risk_score < 30:
            category = "HIGH OPPORTUNITY"
            color = "green"
            icon = "🟢"
            priority = 1
        elif risk_score > opportunity_score:
            category = "MODERATE RISK"
            color = "orange"
            icon = "🟡"
            priority = 2
        elif opportunity_score > risk_score:
            category = "MODERATE OPPORTUNITY"
            color = "lightgreen"
            icon = "🟡"
            priority = 2
        else:
            category = "NEUTRAL"
            color = "gray"
            icon = "⚪"
            priority = 3
        
        # Determine trend arrow
        trend = metrics['trend_7d']
        if trend > 5:
            trend_arrow = "↗️"
            trend_text = f"+{trend:.1f}%"
        elif trend < -5:
            trend_arrow = "↘️"
            trend_text = f"{trend:.1f}%"
        else:
            trend_arrow = "➡️"
            trend_text = f"{trend:.1f}%"
        
        # Days until stockout calculation
        if metrics['days_of_stock'] <= 3:
            stockout_status = "IMMINENT"
            stockout_color = "red"
        elif metrics['days_of_stock'] <= 7:
            stockout_status = "SOON"
            stockout_color = "orange"
        else:
            stockout_status = "SAFE"
            stockout_color = "green"
        
        return {
            'category': category,
            'color': color,
            'icon': icon,
            'priority': priority,
            'risk_score': risk_score,
            'opportunity_score': opportunity_score,
            'trend_arrow': trend_arrow,
            'trend_text': trend_text,
            'days_of_stock': metrics['days_of_stock'],
            'stockout_status': stockout_status,
            'stockout_color': stockout_color,
            'stockout_days': int(metrics['days_of_stock']),
            'recommended_action': self._get_recommended_action(category, metrics),
            # backward compatibility keys if needed
            'status': category,
            'reasons': [self._get_recommended_action(category, metrics)]
        }

    def _get_recommended_action(self, category, metrics):
        """Get specific action based on category"""
        actions = {
            "HIGH RISK": [
                f"Discount by 15-20% to clear {int(max(0, metrics['days_of_stock'] - 14))} excess units",
                "Bundle with trending products",
                "Reduce next order by 30%"
            ],
            "HIGH OPPORTUNITY": [
                f"Increase inventory by {int(min(50, metrics['trend_7d']*2))}%",
                "Feature in prime display location",
                "Consider slight price increase (3-5%)"
            ],
            "MODERATE RISK": [
                "Monitor closely for 7 days",
                "Prepare discount plan if trend continues",
                "Review supplier terms"
            ],
            "MODERATE OPPORTUNITY": [
                "Increase promotion frequency",
                "Test bundling options",
                "Consider cross-selling"
            ],
            "NEUTRAL": [
                "Maintain current levels",
                "Monitor weekly trends",
                "Check competitor pricing"
            ]
        }
        return actions.get(category, ["Monitor as usual"])[0]
    
    def classify_product(self, metrics):
        """Legacy wrapper or standard classification"""
        # If needed for backward compatibility, though app calls v2 now.
        # But wait, original code calls classify_product in show_demand_forecast, show_ai_copilot etc.
        # I should probably update those calls in app.py to use v2 or update this method to use v2 logic with default forecast_growth.
        return self.classify_product_v2(metrics, 0)