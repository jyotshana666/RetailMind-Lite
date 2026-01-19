# models/simulator.py
import pandas as pd
import numpy as np

class WhatIfSimulator:
    """AI-driven business decision simulator"""
    
    def __init__(self):
        self.price_elasticity = {
            'Milk': 0.8,
            'Bread': 1.2,
            'Eggs': 1.5,
            'Coffee': 0.6,
            'Bananas': 1.8,
            'Yogurt': 1.3,
            'Cereal': 1.1
        }
        
        self.cross_elasticity = {
            ('Milk', 'Cereal'): 0.7,
            ('Bread', 'Eggs'): 0.6,
            ('Coffee', 'Bread'): 0.4,
            ('Eggs', 'Bread'): 0.6
        }
    
    def simulate_price_change(self, product, current_price, new_price, 
                             current_demand, forecast_demand):
        """Simulate impact of price change"""
        price_change_pct = (new_price - current_price) / current_price * 100
        elasticity = self.price_elasticity.get(product, 1.0)
        
        # Calculate demand impact
        demand_change_pct = -elasticity * price_change_pct
        new_demand = current_demand * (1 + demand_change_pct / 100)
        forecast_new = forecast_demand * (1 + demand_change_pct / 100)
        
        # Revenue impact
        current_revenue = current_demand * current_price
        new_revenue = new_demand * new_price
        revenue_change_pct = (new_revenue - current_revenue) / current_revenue * 100
        
        # Profit impact (assume 30% margin)
        margin = 0.3
        current_profit = current_demand * current_price * margin
        new_profit = new_demand * new_price * margin
        profit_change_pct = (new_profit - current_profit) / current_profit * 100
        
        # Cross-product impact
        cross_effects = self._calculate_cross_effects(product, price_change_pct)
        
        return {
            'scenario': 'price_change',
            'product': product,
            'price_change_pct': price_change_pct,
            'demand_change_pct': demand_change_pct,
            'new_demand': new_demand,
            'revenue_change_pct': revenue_change_pct,
            'profit_change_pct': profit_change_pct,
            'recommendation': 'INCREASE' if profit_change_pct > 0 else 'DECREASE' if profit_change_pct < -5 else 'HOLD',
            'cross_effects': cross_effects
        }
    
    def simulate_promotion(self, product, discount_pct, duration_days,
                          current_demand, forecast_demand):
        """Simulate impact of promotion"""
        # Immediate lift
        base_lift = 20  # Base promotion lift percentage
        lift_pct = base_lift + (discount_pct * 0.8)  # Additional lift from discount
        
        # Calculate promotional demand
        promo_demand = current_demand * (1 + lift_pct / 100)
        
        # Post-promotion dip (hangover effect)
        post_promo_dip = -0.3 * lift_pct
        
        # Total additional units
        additional_units = (promo_demand - current_demand) * duration_days
        
        # Cost of promotion
        avg_price = 2.99  # Example price
        discount_cost = additional_units * avg_price * (discount_pct / 100)
        
        # Margin impact (assume some incremental sales are profitable)
        margin = 0.3
        incremental_profit = additional_units * avg_price * margin
        net_profit = incremental_profit - discount_cost
        
        roi = (net_profit / discount_cost * 100) if discount_cost > 0 else 0
        
        return {
            'scenario': 'promotion',
            'product': product,
            'discount_pct': discount_pct,
            'duration_days': duration_days,
            'lift_pct': lift_pct,
            'post_promo_dip': post_promo_dip,
            'additional_units': int(additional_units),
            'promotion_cost': discount_cost,
            'net_profit': net_profit,
            'roi_pct': roi,
            'recommendation': 'RUN' if roi > 30 else 'MODIFY' if roi > 10 else 'AVOID'
        }
    
    def simulate_inventory_change(self, product, current_stock_days,
                                 new_stock_days, current_demand):
        """Simulate impact of inventory level change"""
        stock_change_pct = ((new_stock_days - current_stock_days) / current_stock_days * 100)
        
        # Stockout risk reduction
        stockout_risk_reduction = min(40, abs(stock_change_pct) * 0.8) if stock_change_pct > 0 else 0
        
        # Holding cost impact
        holding_cost_pct = abs(stock_change_pct) * 0.5  # 0.5% increase per 1% stock increase
        
        # Lost sales impact (if decreasing inventory)
        lost_sales_risk = min(30, abs(stock_change_pct) * 0.6) if stock_change_pct < 0 else 0
        
        # Financial impact
        avg_price = 2.99
        daily_sales_value = current_demand * avg_price
        holding_cost_change = daily_sales_value * (holding_cost_pct / 100)
        lost_sales_value = daily_sales_value * (lost_sales_risk / 100) if stock_change_pct < 0 else 0
        
        net_impact = -holding_cost_change - lost_sales_value
        
        return {
            'scenario': 'inventory_change',
            'product': product,
            'stock_change_pct': stock_change_pct,
            'stockout_risk_change': -stockout_risk_reduction if stock_change_pct > 0 else 0,
            'holding_cost_change_pct': holding_cost_pct,
            'lost_sales_risk_pct': lost_sales_risk,
            'net_daily_impact': net_impact,
            'recommendation': 'INCREASE' if stock_change_pct > 0 and stockout_risk_reduction > 20 else 
                            'DECREASE' if stock_change_pct < 0 and holding_cost_pct > 10 else 'HOLD'
        }
    
    def _calculate_cross_effects(self, product, price_change_pct):
        """Calculate cross-product demand effects"""
        effects = []
        for (prod1, prod2), elasticity in self.cross_elasticity.items():
            if prod1 == product:
                effect_pct = elasticity * price_change_pct * 0.5
                effects.append({
                    'affected_product': prod2,
                    'demand_change_pct': effect_pct,
                    'relationship': 'complement'
                })
        return effects