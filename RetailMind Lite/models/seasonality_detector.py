# models/seasonality_detector.py
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class SeasonalityDetector:
    """Detects when seasonal patterns deviate from historical norms"""
    
    def __init__(self, window_size=30, deviation_threshold=25):
        self.window_size = window_size
        self.deviation_threshold = deviation_threshold
    
    def detect_breaks(self, product_data, product_name):
        """
        Detect when seasonal patterns deviate from historical norms
        Returns list of break events with insights
        """
        print(f"\n🔍 Seasonality Break Detection for {product_name}")
        print("-" * 50)
        
        data = product_data.copy()
        data['day_of_year'] = data['date'].dt.dayofyear
        
        # Calculate expected seasonality (historical average for each day of year)
        seasonal_pattern = data.groupby('day_of_year')['sales'].mean().rolling(7, center=True).mean()
        
        # Compare recent sales to expected
        recent_data = data.tail(self.window_size)
        breaks = []
        
        for idx, row in recent_data.iterrows():
            expected = seasonal_pattern.get(row['day_of_year'], np.nan)
            if not np.isnan(expected) and expected > 0:
                deviation = (row['sales'] - expected) / expected * 100
                
                if abs(deviation) > self.deviation_threshold:
                    breaks.append({
                        'date': row['date'],
                        'actual': row['sales'],
                        'expected': int(expected),
                        'deviation_%': deviation,
                        'signal': 'ABOVE' if deviation > 0 else 'BELOW',
                        'magnitude': 'HIGH' if abs(deviation) > 40 else 'MEDIUM' if abs(deviation) > 25 else 'LOW'
                    })
        
        # Generate insights
        insights = self._generate_insights(breaks, product_name)
        
        return {
            'breaks': breaks,
            'total_breaks': len(breaks),
            'insights': insights,
            'seasonal_pattern': seasonal_pattern,
            'recent_data': recent_data
        }
    
    def _generate_insights(self, breaks, product_name):
        """Generate business insights from detected breaks"""
        if not breaks:
            return [{
                'type': 'NO_BREAK',
                'message': f"✓ {product_name}: Seasonality pattern holding steady",
                'action': 'Monitor as usual'
            }]
        
        # Calculate average deviation
        deviations = [b['deviation_%'] for b in breaks]
        avg_deviation = np.mean(deviations)
        trend_direction = "increasing" if avg_deviation > 0 else "decreasing"
        
        insights = []
        
        # Main insight
        insights.append({
            'type': 'BREAK_DETECTED',
            'message': f"⚠️ SEASONALITY BREAK DETECTED!",
            'detail': f"Recent sales are {abs(avg_deviation):.1f}% {trend_direction} vs historical pattern.",
            'severity': 'HIGH' if abs(avg_deviation) > 40 else 'MEDIUM'
        })
        
        # Hypothesis generation
        if avg_deviation > 25:
            insights.append({
                'type': 'HYPOTHESIS',
                'message': f"🎯 Potential causes for {product_name}:",
                'detail': [
                    "• New social media trend or viral content",
                    "• Supply chain issue resolved (better availability)",
                    "• Competitor stockout driving customers to you",
                    "• New recipe/usage trend emerging"
                ],
                'action': 'Investigate cause'
            })
        elif avg_deviation < -25:
            insights.append({
                'type': 'HYPOTHESIS',
                'message': f"🎯 Potential causes for {product_name}:",
                'detail': [
                    "• New substitute product entered market",
                    "• Negative review/news affecting perception",
                    "• Quality issues reported",
                    "• Changing consumer preferences"
                ],
                'action': 'Quality check needed'
            })
        
        # Action recommendation
        if avg_deviation > 25:
            action_units = int(abs(avg_deviation) / 10) * 10
            insights.append({
                'type': 'ACTION',
                'message': f"🚀 IMMEDIATE ACTION REQUIRED",
                'detail': f"Increase orders by {action_units}% immediately",
                'reason': "Capitalize on emerging trend before competitors",
                'timing': 'ASAP'
            })
        elif avg_deviation < -25:
            action_units = int(abs(avg_deviation) / 20) * 10
            insights.append({
                'type': 'ACTION',
                'message': f"🛑 ADJUSTMENT NEEDED",
                'detail': f"Reduce next order by {action_units}%",
                'reason': "Prevent overstock from declining demand",
                'timing': 'Next order cycle'
            })
        
        return insights
    
    def plot_seasonality_comparison(self, product_data, product_name):
        """Create visualization comparing actual vs expected seasonality"""
        try:
            import plotly.graph_objects as go
            from plotly.subplots import make_subplots
            
            analysis = self.detect_breaks(product_data, product_name)
            
            if not analysis['breaks']:
                return None
            
            # Create figure
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=(f'{product_name}: Actual vs Expected Sales', 
                              'Deviation from Historical Pattern'),
                vertical_spacing=0.15,
                row_heights=[0.6, 0.4]
            )
            
            # Plot 1: Actual vs Expected
            recent = analysis['recent_data']
            fig.add_trace(
                go.Scatter(x=recent['date'], y=recent['sales'],
                          mode='lines+markers', name='Actual Sales',
                          line=dict(color='blue', width=2)),
                row=1, col=1
            )
            
            # Add expected values
            expected_values = []
            for date in recent['date']:
                day_of_year = date.dayofyear
                expected = analysis['seasonal_pattern'].get(day_of_year, np.nan)
                expected_values.append(expected)
            
            fig.add_trace(
                go.Scatter(x=recent['date'], y=expected_values,
                          mode='lines', name='Expected (Historical)',
                          line=dict(color='red', dash='dash', width=2)),
                row=1, col=1
            )
            
            # Plot 2: Deviation %
            deviations = [b['deviation_%'] for b in analysis['breaks']]
            break_dates = [b['date'] for b in analysis['breaks']]
            
            colors = ['green' if d > 0 else 'red' for d in deviations]
            
            fig.add_trace(
                go.Bar(x=break_dates, y=deviations,
                      name='Deviation %',
                      marker_color=colors,
                      text=[f"{d:+.1f}%" for d in deviations],
                      textposition='auto'),
                row=2, col=1
            )
            
            # Add threshold lines
            fig.add_hline(y=self.deviation_threshold, line_dash="dash", 
                         line_color="orange", row=2, col=1,
                         annotation_text="Upper Threshold")
            fig.add_hline(y=-self.deviation_threshold, line_dash="dash", 
                         line_color="orange", row=2, col=1,
                         annotation_text="Lower Threshold")
            
            fig.update_layout(height=600, showlegend=True,
                            title_text=f"Seasonality Break Analysis: {product_name}")
            
            return fig
            
        except ImportError:
            print("Plotly not available for visualization")
            return None