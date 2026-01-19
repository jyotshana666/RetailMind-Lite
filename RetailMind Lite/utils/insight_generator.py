# utils/insight_generator.py
import numpy as np


class InsightGenerator:
    """Generate plain English business insights from AI outputs"""
    
    def __init__(self):
        self.templates = {
            'stock_up': [
                "🚀 **Stock up on {product}**: Demand expected to grow {growth}% next week. Order {extra_units} extra units to avoid stockouts.",
                "📈 **Increase inventory for {product}**: Strong growth trend of {trend}% weekly. Recommended order: {forecast} units."
            ],
            'discount': [
                "🎯 **Discount {product}**: Demand declining {decline}% weekly with {days} days of stock. 15% discount could clear {units} excess units.",
                "💡 **Run promotion on {product}**: Overstocked and losing momentum. Bundle with trending items for better results."
            ],
            'hold': [
                "⚖️ **Hold current levels for {product}**: Stable demand pattern. Maintain current inventory of ~{inventory} units.",
                "📊 **No action needed for {product}**: Balanced supply and demand. Monitor for any trend changes."
            ],
            'bundle': [
                "🛍️ **Create bundle with {product}**: Pairs well with {paired_product}. Bundle discount could increase sales by {lift}%.",
                "✨ **Merchandise {product} with {paired_product}**: Strong purchase correlation detected. Create cross-promotion display."
            ]
        }
    
    def generate_insight(self, classification, forecast_data, product_data):
        """Generate business insight based on classification"""
        product = classification['metrics']['product']
        
        if classification['status'] == 'HIGH OPPORTUNITY':
            growth = classification['metrics']['trend_7d']
            forecast = int(forecast_data['forecast_avg'])
            extra_units = int(forecast * 0.3)  # 30% buffer
            
            template = np.random.choice(self.templates['stock_up'])
            return template.format(
                product=product,
                growth=abs(growth),
                extra_units=extra_units,
                forecast=forecast,
                trend=abs(growth)
            )
        
        elif classification['status'] == 'HIGH RISK':
            decline = abs(classification['metrics']['trend_7d'])
            days = int(classification['metrics']['days_of_stock'])
            excess_units = int(classification['metrics']['current_avg'] * (days - 14)) if days > 14 else 20
            
            template = np.random.choice(self.templates['discount'])
            return template.format(
                product=product,
                decline=decline,
                days=days,
                units=excess_units
            )
        
        elif classification['status'] == 'Moderate Opportunity':
            # Look for bundling opportunities
            return f"🔄 **Consider bundling {product}**: Growing steadily. Could pair with complementary items."
        
        else:
            inventory = int(classification['metrics']['current_avg'] * 1.5)
            template = np.random.choice(self.templates['hold'])
            return template.format(
                product=product,
                inventory=inventory
            )
    
    def generate_copilot_response(self, question, context):
        """Generate AI copilot response to business questions"""
        question = question.lower()
        
        if 'order' in question or 'what should i buy' in question:
            return self._generate_order_recommendation(context)
        elif 'risk' in question or 'danger' in question:
            return self._generate_risk_report(context)
        elif 'trend' in question or 'growing' in question:
            return self._generate_trend_report(context)
        elif 'discount' in question or 'promotion' in question:
            return self._generate_discount_recommendation(context)
        elif 'simulate' in question or 'what if' in question:
            return "Use the What-If Simulator below to test price changes, promotions, or inventory adjustments before making decisions."
        else:
            return "I can help you with: 1) What to order, 2) Risk alerts, 3) Trending products, 4) Discount recommendations, 5) Business simulations. Ask away!"
    
    def _generate_order_recommendation(self, context):
        high_opp = [p for p in context if p['classification']['status'] == 'HIGH OPPORTUNITY']
        if not high_opp:
            return "All products at optimal levels. Maintain current orders."
        
        recommendations = []
        for product in high_opp[:3]:  # Top 3
            name = product['metrics']['product']
            forecast = int(product['forecast']['forecast_avg'])
            increase = int(forecast * 0.25)
            recommendations.append(f"{name}: Order {forecast + increase} units (+{increase} for safety)")
        
        return f"🚀 **Priority Orders:**\n" + "\n".join(f"• {rec}" for rec in recommendations)
    
    def _generate_risk_report(self, context):
        high_risk = [p for p in context if p['classification']['status'] == 'HIGH RISK']
        if not high_risk:
            return "✅ No high-risk products detected."
        
        risks = []
        for product in high_risk:
            name = product['metrics']['product']
            reasons = ", ".join(product['classification']['reasons'][:2])
            risks.append(f"**{name}**: {reasons}")
        
        return f"🚨 **High Risk Products:**\n" + "\n".join(f"• {risk}" for risk in risks)

    def _generate_trend_report(self, context):
        high_trend = [p for p in context if p['metrics']['trend_7d'] > 10]
        if not high_trend:
             return "📊 All products showing stable demand. No breakout trends detected."

        trends = []
        for product in high_trend[:3]:
            name = product['metrics']['product']
            trend = product['metrics']['trend_7d']
            trends.append(f"{name}: +{trend:.1f}% weekly growth")
        
        return f"📈 **Trending Products:**\n" + "\n".join(f"• {t}" for t in trends)

    def _generate_discount_recommendation(self, context):
        high_risk = [p for p in context if p['classification']['status'] == 'HIGH RISK']
        if not high_risk:
            return "No products currently need discounting. Inventory health is good."
            
        discounts = []
        for product in high_risk[:3]:
            name = product['metrics']['product']
            excess = int(product['metrics']['current_avg'] * 7) # Rough estimate
            discounts.append(f"{name}: 15% off to clear ~{excess} units")
            
        return f"🏷️ **Discount Recommendations:**\n" + "\n".join(f"• {d}" for d in discounts)