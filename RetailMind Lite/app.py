# app.py - Main Streamlit Application
from models.competitive_analyzer import CompetitiveAnalyzer
from models.seasonality_detector import SeasonalityDetector
from models.synergy_analyzer import SynergyAnalyzer
from data.competitive_data import generate_competitive_data
import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add project modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import our modules
from data.generate_data import generate_retail_dataset
from models.forecasting import DemandForecaster
from models.risk_engine import RiskOpportunityEngine
from models.simulator import WhatIfSimulator
from utils.insight_generator import InsightGenerator

# Page configuration
st.set_page_config(
    page_title="RetailMind Lite - AI Market Intelligence Copilot",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        margin-bottom: 2rem;
    }
    .insight-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid;
    }
    .risk-card {
        border-left-color: #EF4444;
        background-color: #FEF2F2;
    }
    .opportunity-card {
        border-left-color: #10B981;
        background-color: #F0FDF4;
    }
    .neutral-card {
        border-left-color: #6B7280;
        background-color: #F9FAFB;
    }
    .metric-card {
        background-color: #F8FAFC;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
    .stButton button {
        width: 100%;
        background-color: #1E3A8A;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class RetailMindApp:
    def __init__(self):
        self.data = None
        self.forecaster = DemandForecaster()
        self.risk_engine = RiskOpportunityEngine()
        self.simulator = WhatIfSimulator()
        self.insight_gen = InsightGenerator()
        self.products = []
        self.initialize_data()
    
    def initialize_data(self):
        """Load or generate data"""
        data_file = 'data/retail_data.csv'
        if os.path.exists(data_file):
            self.data = pd.read_csv(data_file)
        else:
            st.info("Generating synthetic retail data...")
            self.data = generate_retail_dataset()
            self.data.to_csv(data_file, index=False)
        
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.products = sorted(self.data['product'].unique())
    
    def add_tooltips(self):
        """Add informative tooltips throughout the app"""
        return {
            'demand_forecast': "AI predicts sales for next 14 days using historical patterns and seasonality",
            'risk_score': "Combination of trend, volatility, and inventory levels (0-100)",
            'opportunity_score': "Growth potential based on trend and market position (0-100)",
            'days_of_stock': "Current inventory ÷ daily sales = days until stockout",
            'trend_7d': "Weekly sales change compared to previous week",
            'price_elasticity': "How much demand changes when price changes (1.0 = 1% price = 1% demand)",
            'seasonality_break': "When current sales deviate >25% from historical pattern",
            'synergy_score': "How likely products are purchased together (0-1 scale)",
            'stockout_risk': "Probability of running out within next 7 days",
            'confidence_interval': "Range where actual sales will fall 85% of the time"
        }

    def run(self):
        """Main application loop"""
        # Header
        st.markdown('<h1 class="main-header">🛍️ RetailMind Lite</h1>', unsafe_allow_html=True)
        st.markdown('<p class="sub-header">AI Market Intelligence Copilot for Small Retailers</p>', unsafe_allow_html=True)
        
        # Sidebar
        with st.sidebar:
            st.image("https://cdn-icons-png.flaticon.com/512/3710/3710277.png", width=80)
            st.title("Dashboard Controls")
            
            selected_product = st.selectbox(
                "Select Product",
                self.products,
                index=0
            )
            
            forecast_days = st.slider(
                "Forecast Period (Days)",
                min_value=7,
                max_value=30,
                value=14
            )
            
            st.divider()
            st.caption("Built for Hackathon Demo • Team Size: 6 • Time: 6 hours")
        
        # EXECUTIVE SUMMARY SECTION
        st.markdown("---")
        st.subheader("🎯 TOP 3 ACTIONS THIS WEEK")
        
        top_actions = self.show_executive_summary()
        
        if top_actions:
            cols = st.columns(3)
            for idx, action in enumerate(top_actions):
                with cols[idx]:
                    if action['category'] == "HIGH RISK":
                        st.error(f"**{action['product']}**")
                        st.caption(f"🚨 {action['category']}")
                        st.write(action['action'])
                    elif action['category'] == "HIGH OPPORTUNITY":
                        st.success(f"**{action['product']}**")
                        st.caption(f"🎯 {action['category']}")
                        st.write(action['action'])
                    else:
                        st.warning(f"**{action['product']}**")
                        st.caption(f"⚠️ {action['category']}")
                        st.write(action['action'])
        else:
            st.info("All products in normal range. Continue monitoring.")

        # Main content area - Tabs
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Dashboard", 
            "🎯 Demand Forecast", 
            "🚨 Risk Monitor", 
            "💰 Pricing",
            "🔄 Synergies",
            "🎮 Simulator",
            "💬 AI Copilot"
        ])

        with tab1:
            self.show_combined_dashboard(selected_product)
        with tab2:
            self.show_demand_forecast(selected_product, forecast_days)
        with tab3:
            self.show_risk_opportunities_v2()
            st.markdown("---")
            self.stockout_countdown_display()
        with tab4:
            self.show_competitive_analysis()
            st.markdown("---")
            self.interactive_pricing_tool(selected_product)
        with tab5:
            self.show_product_synergies()
        with tab6:
            self.enhanced_what_if_simulator(selected_product)
        with tab7:
            self.show_ai_copilot_v2(selected_product)

    def show_combined_dashboard(self, selected_product):
        """Display combined dashboard view for tab 1"""
        st.subheader(f"📊 Dashboard: {selected_product}")
        
        # Get product data
        product_data = self.data[self.data['product'] == selected_product].copy()
        metrics = self.risk_engine.calculate_metrics(product_data)
        forecast_result = self.forecaster.forecast(selected_product, product_data, 7)
        classification = self.risk_engine.classify_product_v2(metrics, forecast_result['growth_pct'])
        
        # Top Metrics Row
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Risk Status", f"{classification['icon']} {classification['category']}")
        with col2:
            st.metric("Weekly Trend", f"{classification['trend_text']} {classification['trend_arrow']}")
        with col3:
            st.metric("Stock Days", f"{int(metrics['days_of_stock'])}")
        with col4:
            st.metric("Forecast Avg", f"{int(forecast_result['forecast_avg'])}")
            
        st.markdown("---")
        
        # Main Chart & Actions
        c1, c2 = st.columns([2, 1])
        
        with c1:
            st.subheader("Demand Forecast (Next 7 Days)")
            forecast_df = forecast_result['forecast_df']
            
            fig = go.Figure()
            # Historical
            hist = product_data.tail(30)
            fig.add_trace(go.Bar(x=hist['date'], y=hist['sales'], name='Historical', marker_color='#E5E7EB'))
            # Forecast
            fig.add_trace(go.Scatter(x=forecast_df['date'], y=forecast_df['forecast'], name='Forecast', line=dict(color='#1E3A8A', width=3)))
            
            fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0), showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with c2:
            st.subheader("⚡ Quick Actions")
            st.info(f"💡 {classification['recommended_action']}")
            
            if classification['category'] == 'HIGH RISK':
                if st.button("🏷️ Apply Discount"):
                    st.success("Discount applied! (Simulation)")
            elif classification['category'] == 'HIGH OPPORTUNITY':
                if st.button("📦 Order Stock"):
                    st.success("Order placed! (Simulation)")
            
            st.write("**Recent Alerts:**")
            if metrics['stockout_risk'] > 0.3:
                st.warning(f"⚠️ Stockout Risk: {metrics['stockout_risk']*100:.0f}%")
            if abs(metrics['trend_7d']) > 10:
                st.info(f"📈 High Volatility Detected")

    def show_executive_summary(self):
        """Display top 3 action cards on main page"""
        
        # Analyze all products for top actions
        all_actions = []
        
        # Check first 5 products for speed or all if dataset small
        products_to_check = self.products[:10] if len(self.products) > 10 else self.products
        
        for product in products_to_check:
            product_data = self.data[self.data['product'] == product].copy()
            
            # Get metrics
            metrics = self.risk_engine.calculate_metrics(product_data)
            
            # Get forecast
            forecast = self.forecaster.forecast(product, product_data, 7)
            
            # Classify
            classification = self.risk_engine.classify_product_v2(metrics, forecast['growth_pct'])
            
            if classification['priority'] <= 2:  # High or Moderate
                all_actions.append({
                    'product': product,
                    'category': classification['category'],
                    'action': classification['recommended_action'],
                    'priority': classification['priority'],
                    'color': classification['color'],
                    'trend': metrics['trend_7d']
                })
        
        # Sort by priority and trend strength
        all_actions.sort(key=lambda x: (x['priority'], -abs(x['trend'])))
        
        return all_actions[:3]  # Top 3 actions

    def show_risk_opportunities_v2(self):
        """Enhanced version with trend arrows and consistent colors"""
        
        st.subheader("📊 Product Health Dashboard")
        
        # Analyze all products
        results = []
        for product in self.products:
            product_data = self.data[self.data['product'] == product].copy()
            
            # Get metrics and classification
            metrics = self.risk_engine.calculate_metrics(product_data)
            forecast = self.forecaster.forecast(product, product_data, 7)
            classification = self.risk_engine.classify_product_v2(metrics, forecast['growth_pct'])
            
            results.append({
                'Product': product,
                'Status': f"{classification['icon']} {classification['category']}",
                'Trend': f"{classification['trend_arrow']} {classification['trend_text']}",
                'Stock Days': classification['days_of_stock'],
                'Stockout Risk': f"🛒 {classification['stockout_days']} days",
                'Risk Score': classification['risk_score'],
                'Opp Score': classification['opportunity_score'],
                'Action': classification['recommended_action'][:40] + "...",
                '_color': classification['color'],
                '_priority': classification['priority']
            })
        
        # Sort by priority
        results.sort(key=lambda x: x['_priority'])
        
        # Create DataFrame
        df = pd.DataFrame(results)
        
        # Display with color coding
        def color_row(row):
            colors = {
                'red': 'background-color: #fee',
                'orange': 'background-color: #ffedcc',
                'green': 'background-color: #e8f7e8',
                'lightgreen': 'background-color: #f0fff0',
                'gray': 'background-color: #f9f9f9'
            }
            color_val = df.loc[row.name, '_color'] if row.name in df.index else 'gray'
            return [colors.get(color_val, '')] * len(row)
        
        # Display table
        display_df = df.drop(['_color', '_priority'], axis=1)
        styled_df = display_df.style.apply(color_row, axis=1)
        
        st.dataframe(styled_df, use_container_width=True, height=400)
        
        # Add filter buttons
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🔴 Show High Risk", use_container_width=True):
                filtered = df[df['_color'] == 'red']
                st.dataframe(filtered.drop(['_color', '_priority'], axis=1), use_container_width=True)
        with col2:
            if st.button("🟢 Show Opportunities", use_container_width=True):
                filtered = df[df['_color'] == 'green']
                st.dataframe(filtered.drop(['_color', '_priority'], axis=1), use_container_width=True)
        with col3:
            if st.button("🟡 Show Moderate", use_container_width=True):
                filtered = df[df['_color'] == 'orange']
                st.dataframe(filtered.drop(['_color', '_priority'], axis=1), use_container_width=True)
        with col4:
            if st.button("📋 Show All", use_container_width=True):
                st.dataframe(display_df, use_container_width=True)

    def stockout_countdown_display(self):
        """Show imminent stockout warnings"""
        
        st.subheader("⏰ Stockout Countdown")
        
        warnings = []
        for product in self.products:
            product_data = self.data[self.data['product'] == product].copy()
            metrics = self.risk_engine.calculate_metrics(product_data)
            
            # Calculate days until stockout
            days_of_stock = metrics['days_of_stock']
            
            if days_of_stock <= 7:  # Only show critical items
                warnings.append({
                    'product': product,
                    'days_left': int(days_of_stock),
                    'severity': 'CRITICAL' if days_of_stock <= 3 else 'WARNING',
                    'daily_demand': int(metrics['current_avg']),
                    'needed_units': int(metrics['current_avg'] * max(0, 14 - days_of_stock))
                })
        
        if warnings:
            # Sort by urgency
            warnings.sort(key=lambda x: x['days_left'])
            
            for warning in warnings:
                if warning['severity'] == 'CRITICAL':
                    with st.container():
                        col1, col2, col3 = st.columns([1, 2, 1])
                        with col1:
                            st.error(f"🚨 {warning['product']}")
                        with col2:
                            progress = min(1.0, max(0.0, warning['days_left'] / 7))
                            st.progress(progress, 
                                    text=f"{warning['days_left']} days left")
                        with col3:
                            st.write(f"Order {warning['needed_units']} units")
                            
                        st.markdown("---")
        else:
            st.success("✅ No imminent stockouts detected")
        
        # Add quick order button
        if st.button("📦 Generate Reorder List", type="primary"):
            reorder_list = []
            for product in self.products:
                product_data = self.data[self.data['product'] == product].copy()
                metrics = self.risk_engine.calculate_metrics(product_data)
                
                if metrics['days_of_stock'] < 10:
                    forecast = self.forecaster.forecast(product, product_data, 7)
                    order_qty = int(forecast['forecast_avg'] * 7 * 1.2)  # 7 days + 20% buffer
                    reorder_list.append(f"{product}: {order_qty} units")
            
            if reorder_list:
                st.info("**Suggested Order List:**")
                for item in reorder_list:
                    st.write(f"• {item}")
            else:
                st.success("All products sufficiently stocked")

    def enhanced_what_if_simulator(self, selected_product):
        """Enhanced simulator with promotion toggle"""
        
        st.subheader("🎮 What-If Decision Simulator")
        st.caption("Test business decisions before implementing them")
        
        col1, col2 = st.columns(2)
        
        with col1:
            scenario = st.radio(
                "Choose Scenario:",
                ["Price Change", "Promotion", "Inventory Adjustment"],
                horizontal=True
            )
            
            # Dynamic controls based on scenario
            if scenario == "Price Change":
                current_price = st.number_input("Current Price ($)", 
                                            value=2.99, min_value=0.5, 
                                            max_value=20.0, step=0.1,
                                            key="price_current")
                new_price = st.slider("New Price ($)", 
                                    0.5, 20.0, 3.29, 0.1,
                                    key="price_new")
                
                # Add interactive sensitivity slider
                price_sensitivity = st.slider("Price Sensitivity", 
                                        0.5, 3.0, 1.5, 0.1,
                                        help="How much demand changes with price (1.0 = normal)")
                
            elif scenario == "Promotion":
                # Promotion toggle
                promo_active = st.toggle("Activate Promotion", value=True)
                
                if promo_active:
                    discount = st.slider("Discount %", 5, 50, 15, 5,
                                    help="Percentage discount to apply")
                    duration = st.slider("Duration (Days)", 1, 14, 3, 1)
                    promo_type = st.selectbox("Promotion Type",
                                            ["Percentage Off", "Buy One Get One", "Bundle Discount"])
                    
                    # Add promotion timing
                    promo_start = st.date_input("Start Date")
                    promo_channel = st.multiselect("Promotion Channels",
                                                ["In-Store", "Online", "Email", "Social Media"])
                else:
                    st.info("Promotion disabled")
                    discount = 0
                    duration = 1
                    
            else:  # Inventory Adjustment
                current_stock = st.slider("Current Stock Days", 5, 60, 20, 1,
                                        help="How many days of inventory you currently have")
                new_stock = st.slider("New Stock Days", 5, 60, 15, 1)
                
                # Add lead time consideration
                lead_time = st.slider("Supplier Lead Time (Days)", 1, 30, 7, 1,
                                    help="How long to get new stock")
        
        with col2:
            # Get product data for simulation
            product_data = self.data[self.data['product'] == selected_product].copy()
            current_demand = product_data['sales'].tail(30).mean()
            
            if st.button("🚀 Run Simulation", type="primary", use_container_width=True):
                with st.spinner("Simulating..."):
                    # Run appropriate simulation
                    if scenario == "Price Change":
                        result = self.simulator.simulate_price_change(
                            selected_product, current_price, new_price,
                            current_demand, current_demand * 1.1
                        )
                        
                        # Enhanced visualization
                        fig = go.Figure()
                        
                        # Current vs New
                        fig.add_trace(go.Bar(
                            x=['Current', 'Proposed'],
                            y=[current_price, new_price],
                            name='Price',
                            marker_color=['blue', 'red'],
                            text=[f"${current_price}", f"${new_price}"],
                            textposition='auto'
                        ))
                        
                        fig.update_layout(
                            title="Price Change Impact",
                            yaxis_title="Price ($)",
                            showlegend=False,
                            height=300
                        )
                        
                        st.plotly_chart(fig, use_container_width=True)
                        
                    elif scenario == "Promotion" and promo_active:
                        result = self.simulator.simulate_promotion(
                            selected_product, discount, duration,
                            current_demand, current_demand * 1.1
                        )
                        
                        # Promotion impact visualization
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Sales Lift", f"+{result.get('lift_pct', 0):.1f}%")
                        with col_b:
                            st.metric("Additional Units", result.get('additional_units', 0))
                        with col_c:
                            st.metric("ROI", f"{result.get('roi_pct', 0):.1f}%")
                        
                    elif scenario == "Promotion" and not promo_active:
                        result = {"recommendation": "HOLD", "reason": "Promotion disabled"}

                    else:
                        result = self.simulator.simulate_inventory_change(
                            selected_product, current_stock, new_stock,
                            current_demand
                        )
                    
                    # Display recommendation
                    st.markdown("---")
                    if result.get('recommendation') in ['INCREASE', 'RUN']:
                        st.success(f"✅ **RECOMMENDATION: {result.get('recommendation')}**")
                        st.balloons()
                    elif result.get('recommendation') == 'HOLD':
                        st.info(f"ℹ️ **RECOMMENDATION: {result.get('recommendation')}**")
                    else:
                        st.error(f"❌ **RECOMMENDATION: {result.get('recommendation')}**")
                    
                    # Show detailed metrics
                    with st.expander("View Detailed Analysis"):
                        for key, value in result.items():
                            if key not in ['scenario', 'product', 'recommendation']:
                                st.write(f"**{key.replace('_', ' ').title()}:** {value}")

    def interactive_pricing_tool(self, selected_product):
        """Interactive pricing optimization tool"""
        
        st.subheader("💰 Interactive Pricing Optimizer")
        
        # Get product data
        product_data = self.data[self.data['product'] == selected_product].copy()
        current_price = product_data['price'].iloc[-1]
        current_demand = product_data['sales'].tail(30).mean()
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            # Price slider
            new_price = st.slider(
                "Set New Price",
                min_value=float(current_price * 0.5),
                max_value=float(current_price * 1.5),
                value=float(current_price),
                step=0.1,
                format="$%.2f",
                help="Drag to find optimal price point"
            )
            
            # Price elasticity input
            elasticity = st.slider(
                "Price Sensitivity",
                min_value=0.5,
                max_value=3.0,
                value=1.5,
                step=0.1,
                help="Higher = more sensitive to price changes"
            )
        
        with col2:
            # Calculate impacts
            price_change_pct = (new_price - current_price) / current_price * 100
            demand_change_pct = -elasticity * price_change_pct
            new_demand = current_demand * (1 + demand_change_pct / 100)
            
            # Revenue calculations
            current_revenue = current_demand * current_price
            new_revenue = new_demand * new_price
            revenue_change_pct = (new_revenue - current_revenue) / current_revenue * 100
            
            # Display metrics
            st.metric("Price Change", f"{price_change_pct:+.1f}%")
            st.metric("Demand Impact", f"{demand_change_pct:+.1f}%")
            st.metric("Revenue Impact", f"{revenue_change_pct:+.1f}%")
        
        # Real-time visualization
        prices = np.linspace(current_price * 0.5, current_price * 1.5, 20)
        revenues = []
        
        for p in prices:
            demand_change = -elasticity * ((p - current_price) / current_price * 100)
            new_d = current_demand * (1 + demand_change / 100)
            revenues.append(new_d * p)
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=prices,
            y=revenues,
            mode='lines',
            name='Expected Revenue',
            line=dict(color='blue', width=3)
        ))
        
        # Mark current and proposed
        fig.add_vline(x=current_price, line_dash="dash", 
                    line_color="green", annotation_text="Current")
        fig.add_vline(x=new_price, line_dash="dash", 
                    line_color="red", annotation_text="Proposed")
        
        fig.update_layout(
            title="Revenue vs Price Curve",
            xaxis_title="Price ($)",
            yaxis_title="Daily Revenue ($)",
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Optimization recommendation
        optimal_price = prices[np.argmax(revenues)]
        if abs(new_price - optimal_price) / optimal_price < 0.05:
            st.success(f"🎯 Great! Your price is near optimal (${optimal_price:.2f})")
        elif new_price > optimal_price:
            st.warning(f"💡 Consider lowering to ${optimal_price:.2f} for maximum revenue")
        else:
            st.info(f"💡 Consider raising to ${optimal_price:.2f} for maximum revenue")

    def show_ai_copilot_v2(self, selected_product):
        """Enhanced AI Copilot with chat interface"""
        
        st.subheader("🤖 AI Business Copilot")
        st.caption("Ask me anything about your retail business...")
        
        # Initialize session state for chat history
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
        
        # Chat interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            user_input = st.text_input("Type your question:", 
                                    placeholder="e.g., What should I order tomorrow?", key="copilot_input")
        
        with col2:
            if st.button("Ask", type="primary", use_container_width=True):
                if user_input:
                    # Add to history
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': user_input
                    })
                    
                    # Prepare context
                    context = []
                    product_data = self.data[self.data['product'] == selected_product].copy()
                    metrics = self.risk_engine.calculate_metrics(product_data)
                    forecast_result = self.forecaster.forecast(selected_product, product_data, 7)
                    classification = self.risk_engine.classify_product_v2(metrics, forecast_result['growth_pct'])
                    
                    context.append({
                        'product': selected_product, 
                        'metrics': metrics, 
                        'classification': classification,
                        'forecast': forecast_result
                    })

                    # Generate response
                    response = self.insight_gen.generate_copilot_response(user_input, context)
                    
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response
                    })
        
        # Quick action buttons
        st.write("**Quick Actions:**")
        quick_cols = st.columns(5)
        questions = [
            ("📦", "What to order?", "order"),
            ("⚠️", "What's risky?", "risk"),
            ("📈", "What's trending?", "trend"),
            ("💰", "Pricing advice?", "price"),
            ("🎮", "Simulate decision", "simulate")
        ]
        
        for idx, (icon, text, key) in enumerate(questions):
            with quick_cols[idx]:
                if st.button(f"{icon} {text}", key=f"quick_{key}"):
                    # Prepare context again (duplication here but ok for safety)
                    # Prepare context with full details including classification and forecast
                    product_data = self.data[self.data['product'] == selected_product].copy()
                    metrics = self.risk_engine.calculate_metrics(product_data)
                    forecast_result = self.forecaster.forecast(selected_product, product_data, 7)
                    classification = self.risk_engine.classify_product_v2(metrics, forecast_result['growth_pct'])
                    
                    context = [{
                        'product': selected_product, 
                        'metrics': metrics,
                        'classification': classification,
                        'forecast': forecast_result
                    }]

                    response = self.insight_gen.generate_copilot_response(text, context)
                    st.session_state.chat_history.append({
                        'role': 'user',
                        'content': text
                    })
                    st.session_state.chat_history.append({
                        'role': 'assistant',
                        'content': response
                    })
        
        # Display chat history
        st.markdown("---")
        st.subheader("💬 Conversation")
        
        for message in st.session_state.chat_history[-5:]:  # Last 5 messages
            if message['role'] == 'user':
                with st.chat_message("user"):
                    st.write(message['content'])
            else:
                with st.chat_message("assistant"):
                    st.write(message['content'])
        
        # Clear chat button
        if st.button("Clear Conversation"):
            st.session_state.chat_history = []
            st.rerun()

    def show_competitive_analysis(self):
        """Display competitive intelligence"""
        st.header("🏪 Competitive Intelligence")
        
        analyzer = CompetitiveAnalyzer()
        
        # Run analysis
        with st.spinner("Analyzing competitive landscape..."):
            analysis = analyzer.analyze_competitive_position(self.data)
        
        # Summary cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Products Losing Share", analysis['summary']['losing_share'])
        with col2:
            st.metric("Products Gaining Share", analysis['summary']['gaining_share'])
        with col3:
            st.metric("Avg Price Gap", f"{analysis['summary']['avg_price_gap']:.1f}%")
        
        # Display recommendations
        st.subheader("🎯 Top Recommendations")
        
        high_priority = [r for r in analysis['recommendations'] if r['priority'] == 'HIGH']
        
        for rec in high_priority[:3]:
            with st.expander(f"🚨 {rec['product']}: {rec['action']}", expanded=True):
                st.write(f"**Why:** {rec['reason']}")
                st.write(f"**Impact:** {rec['impact']}")
        
        # Price simulation tool
        st.subheader("💡 Competitor Price Simulation")
        
        col1, col2 = st.columns(2)
        with col1:
            sim_product = st.selectbox("Select Product", self.products, key="comp_sim_product")
        with col2:
            price_change = st.slider("Competitor Price Change %", -20, 20, 10, key="comp_price_change")
        
        if st.button("Simulate Competitor Move"):
            result = analyzer.simulate_competitor_price_change(sim_product, price_change)
            st.info(result['interpretation'])

    def show_seasonality_breaks(self):
        """Display seasonality break detection"""
        st.header("📅 Seasonality Break Detection")
        
        selected_product = st.selectbox("Select Product for Analysis", self.products, key="season_product")
        
        detector = SeasonalityDetector()
        product_data = self.data[self.data['product'] == selected_product].copy()
        
        with st.spinner(f"Analyzing {selected_product} seasonality..."):
            analysis = detector.detect_breaks(product_data, selected_product)
        
        # Display insights
        for insight in analysis['insights']:
            if insight['type'] == 'BREAK_DETECTED':
                st.warning(f"⚠️ {insight['message']}")
                st.write(insight['detail'])
            elif insight['type'] == 'ACTION':
                st.error(f"🚀 {insight['message']}")
                st.write(f"**Action:** {insight['detail']}")
                st.write(f"**Timing:** {insight.get('timing', 'Immediate')}")
        
        # Show breaks table
        if analysis['breaks']:
            st.subheader("📊 Detected Breaks")
            breaks_df = pd.DataFrame(analysis['breaks'])
            st.dataframe(breaks_df[['date', 'actual', 'expected', 'deviation_%', 'signal']], use_container_width=True)
        
        # Visualization
        if st.checkbox("Show Seasonality Comparison Chart"):
            fig = detector.plot_seasonality_comparison(product_data, selected_product)
            if fig:
                st.plotly_chart(fig, use_container_width=True)

    def show_product_synergies(self):
        """Display product synergy analysis"""
        st.header("🔄 Product Synergy Analysis")
        
        analyzer = SynergyAnalyzer()
        
        with st.spinner("Analyzing product relationships..."):
            analysis = analyzer.analyze_product_synergies(self.data)
        
        # Summary
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Strong Synergies Found", analysis['summary']['total_synergies'])
        with col2:
            st.metric("Top Synergy Pair", analysis['summary']['top_synergy'] or "None")
        with col3:
            st.metric("Avg Lift Potential", f"{analysis['summary']['avg_lift_potential']:.1f}%")
        
        # Recommendations
        st.subheader("🎁 Bundle Recommendations")
        
        for rec in analysis['recommendations'][:3]:
            if rec['type'] == 'BUNDLE_RECOMMENDATION':
                with st.expander(f"📦 {rec['message']}", expanded=True):
                    for detail in rec['details']:
                        st.write(f"• {detail}")
                    st.write(f"**Action:** {rec['action']}")
        
        # Ripple effects
        if analysis['ripple_effects']:
            st.subheader("🌊 Demand Ripple Effects")
            
            for effect in analysis['ripple_effects'][:2]:
                st.write(f"**{effect['trigger_product']}** trending {effect['trend']:+.1f}%:")
                for related in effect['related_products'][:2]:
                    st.write(f"  → {related['product']}: {related['predicted_change']:+.1f}% ({related['relationship']})")

    def show_demand_forecast(self, product, forecast_days):
        """Display demand forecast visualization"""
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"Demand Forecast: {product}")
            
            # Get product data
            product_data = self.data[self.data['product'] == product].copy()
            
            # Generate forecast
            forecast_result = self.forecaster.forecast(product, product_data, forecast_days)
            forecast_df = forecast_result['forecast_df']
            
            # Create Plotly figure
            fig = go.Figure()
            
            # Historical data (last 60 days)
            hist_data = product_data.tail(60)
            fig.add_trace(go.Scatter(
                x=hist_data['date'],
                y=hist_data['sales'],
                mode='lines+markers',
                name='Historical Sales',
                line=dict(color='#3B82F6', width=2),
                marker=dict(size=4)
            ))
            
            # Forecast
            fig.add_trace(go.Scatter(
                x=forecast_df['date'],
                y=forecast_df['forecast'],
                mode='lines',
                name='Forecast',
                line=dict(color='#EF4444', width=3, dash='dash')
            ))
            
            # Confidence interval
            fig.add_trace(go.Scatter(
                x=forecast_df['date'].tolist() + forecast_df['date'].tolist()[::-1],
                y=forecast_df['forecast_upper'].tolist() + forecast_df['forecast_lower'].tolist()[::-1],
                fill='toself',
                fillcolor='rgba(239, 68, 68, 0.2)',
                line=dict(color='rgba(255,255,255,0)'),
                hoverinfo='skip',
                showlegend=False
            ))
            
            fig.update_layout(
                title=f"{forecast_days}-Day Demand Forecast",
                xaxis_title="Date",
                yaxis_title="Units Sold",
                hovermode='x unified',
                template='plotly_white',
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Forecast Insights")
            
            # Key metrics
            metrics_data = [
                ("📈 Forecast Avg", f"{int(forecast_result['forecast_avg'])} units/day"),
                ("📊 Growth Trend", f"{forecast_result['growth_pct']:+.1f}%"),
                ("🎯 Peak Demand", forecast_result['peak_day'].strftime('%b %d')),
                ("📅 Confidence", "85%")
            ]
            
            for icon, value in metrics_data:
                st.metric(icon, value)
            
            st.divider()
            
            # Generate insight
            metrics = self.risk_engine.calculate_metrics(product_data)
            classification = self.risk_engine.classify_product_v2(metrics, forecast_result['growth_pct'])
            
            # Legacy shim for insight gen if it expects 'status' in a certain format
            # classification dict already has 'category' mapping to old 'status' values like "HIGH RISK"
            
            insight = self.insight_gen.generate_insight(
                {'status': classification['category'], 'reasons': [classification['recommended_action']], 'metrics': metrics}, # Wrap for compatibility
                forecast_result,
                product_data
            )
            
            card_class = 'opportunity-card' if 'HIGH OPPORTUNITY' in classification['category'] else \
                        'risk-card' if 'HIGH RISK' in classification['category'] else 'neutral-card'
            
            st.markdown(f'<div class="insight-card {card_class}">{insight}</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    app = RetailMindApp()
    app.run()