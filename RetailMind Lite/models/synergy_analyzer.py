# models/synergy_analyzer.py
import pandas as pd
import numpy as np
from itertools import combinations

class SynergyAnalyzer:
    """Identifies products that sell together and predicts ripple effects"""
    
    def __init__(self):
        self.correlation_threshold = 0.6
        self.synergy_threshold = 0.7
    
    def analyze_product_synergies(self, sales_data):
        """Identify product pairs with strong demand correlations"""
        print("\n" + "="*60)
        print("CROSS-PRODUCT DEMAND SYNERGY IDENTIFICATION")
        print("="*60)
        
        # Pivot data to get product sales matrix
        pivot_data = sales_data.pivot_table(
            index='date',
            columns='product',
            values='sales',
            aggfunc='sum'
        ).fillna(0)
        
        products = pivot_data.columns.tolist()
        
        # Calculate correlation matrix
        correlation_matrix = pivot_data.corr()
        
        # Find strong synergies
        strong_synergies = []
        for i, prod1 in enumerate(products):
            for j, prod2 in enumerate(products[i+1:], i+1):
                corr = correlation_matrix.iloc[i, j]
                
                if abs(corr) > self.correlation_threshold:
                    # Calculate synergy metrics
                    synergy_score = self._calculate_synergy_score(pivot_data, prod1, prod2)
                    
                    if synergy_score > self.synergy_threshold:
                        relationship = "complementary" if corr > 0 else "substitute"
                        
                        strong_synergies.append({
                            'product_pair': f"{prod1} + {prod2}",
                            'product1': prod1,
                            'product2': prod2,
                            'correlation': corr,
                            'synergy_score': synergy_score,
                            'relationship': relationship,
                            'expected_lift': synergy_score * 100  # Estimated sales lift from bundling
                        })
        
        # Sort by synergy score
        strong_synergies.sort(key=lambda x: x['synergy_score'], reverse=True)
        
        # Generate recommendations
        recommendations = self._generate_synergy_recommendations(strong_synergies, sales_data)
        
        # Predict ripple effects
        ripple_effects = self._predict_ripple_effects(strong_synergies, sales_data)
        
        return {
            'synergies': strong_synergies,
            'recommendations': recommendations,
            'ripple_effects': ripple_effects,
            'correlation_matrix': correlation_matrix,
            'summary': {
                'total_synergies': len(strong_synergies),
                'top_synergy': strong_synergies[0]['product_pair'] if strong_synergies else None,
                'avg_lift_potential': np.mean([s['expected_lift'] for s in strong_synergies]) if strong_synergies else 0
            }
        }
    
    def _calculate_synergy_score(self, pivot_data, prod1, prod2):
        """Calculate synergy score between two products"""
        # Get sales data
        sales1 = pivot_data[prod1]
        sales2 = pivot_data[prod2]
        
        # Calculate probability of selling together
        both_sold = ((sales1 > 0) & (sales2 > 0)).sum()
        total_days = len(sales1)
        co_purchase_prob = both_sold / total_days if total_days > 0 else 0
        
        # Calculate correlation strength
        correlation = sales1.corr(sales2)
        
        # Combined synergy score
        synergy = (co_purchase_prob * 0.6) + (abs(correlation) * 0.4)
        
        return synergy
    
    def _generate_synergy_recommendations(self, synergies, sales_data):
        """Generate merchandising recommendations from synergies"""
        recommendations = []
        
        if not synergies:
            return [{
                'type': 'NO_SYNERGY',
                'message': "No strong product synergies detected",
                'action': 'Continue current merchandising'
            }]
        
        # Top 3 synergies
        for synergy in synergies[:3]:
            prod1, prod2 = synergy['product1'], synergy['product2']
            
            if synergy['relationship'] == 'complementary':
                rec = {
                    'type': 'BUNDLE_RECOMMENDATION',
                    'product_pair': synergy['product_pair'],
                    'message': f"🎯 CREATE BUNDLE: '{prod1} & {prod2} Combo'",
                    'details': [
                        f"Expected sales lift: +{synergy['expected_lift']:.1f}%",
                        f"Price suggestion: 10-15% discount on bundle",
                        f"Display: Place products adjacently"
                    ],
                    'action': 'Implement bundle pricing',
                    'priority': 'HIGH'
                }
            else:  # substitute relationship
                rec = {
                    'type': 'SEPARATE_MERCHANDISING',
                    'product_pair': synergy['product_pair'],
                    'message': f"⚠️ SEPARATE DISPLAY: {prod1} and {prod2}",
                    'details': [
                        f"Products are substitutes (customers choose one or the other)",
                        f"Place in different aisles to encourage multiple purchases",
                        f"Consider different promotions for each"
                    ],
                    'action': 'Separate in store layout',
                    'priority': 'MEDIUM'
                }
            
            recommendations.append(rec)
        
        return recommendations
    
    def _predict_ripple_effects(self, synergies, sales_data):
        """Predict demand ripple effects when one product's demand changes"""
        ripple_predictions = []
        
        if not synergies:
            return ripple_predictions
        
        # Get recent demand trends
        recent_trends = {}
        products = sales_data['product'].unique()
        
        for product in products:
            product_data = sales_data[sales_data['product'] == product]
            recent = product_data.tail(30)['sales']
            if len(recent) >= 14:
                trend = (recent.tail(7).mean() - recent.iloc[-14:-7].mean()) / recent.iloc[-14:-7].mean() * 100
                recent_trends[product] = trend if not np.isnan(trend) else 0
        
        # Predict ripple effects for products with strong trends
        for product, trend in recent_trends.items():
            if abs(trend) > 10:  # Significant trend
                related_products = []
                
                for synergy in synergies:
                    if product in [synergy['product1'], synergy['product2']]:
                        other = synergy['product2'] if synergy['product1'] == product else synergy['product1']
                        relationship = synergy['relationship']
                        
                        # Estimate ripple effect
                        if relationship == 'complementary':
                            ripple_effect = trend * synergy['correlation'] * 0.5
                            explanation = f"complements {product}"
                        else:
                            ripple_effect = trend * synergy['correlation'] * -0.3  # Opposite direction for substitutes
                            explanation = f"substitute for {product}"
                        
                        related_products.append({
                            'product': other,
                            'predicted_change': ripple_effect,
                            'relationship': explanation,
                            'confidence': synergy['synergy_score']
                        })
                
                if related_products:
                    ripple_predictions.append({
                        'trigger_product': product,
                        'trend': trend,
                        'related_products': related_products,
                        'action': f"Stock up on complements" if trend > 0 else f"Watch substitute demand"
                    })
        
        return ripple_predictions
    
    def get_bundle_suggestions(self, synergies, top_n=5):
        """Get specific bundle suggestions from synergies"""
        bundle_suggestions = []
        
        complementary_synergies = [s for s in synergies if s['relationship'] == 'complementary']
        complementary_synergies.sort(key=lambda x: x['synergy_score'], reverse=True)
        
        for synergy in complementary_synergies[:top_n]:
            suggestion = {
                'bundle_name': f"{synergy['product1']} & {synergy['product2']} Bundle",
                'products': [synergy['product1'], synergy['product2']],
                'expected_lift': f"+{synergy['expected_lift']:.1f}%",
                'pricing_suggestion': "10-15% discount vs buying separately",
                'placement': "Endcap or featured display",
                'promotion_idea': f"Buy {synergy['product1']}, get {synergy['product2']} at 20% off"
            }
            bundle_suggestions.append(suggestion)
        
        return bundle_suggestions