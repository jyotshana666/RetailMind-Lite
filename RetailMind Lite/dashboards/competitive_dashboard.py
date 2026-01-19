# dashboards/competitive_dashboard.py
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

def display_competitive_dashboard(competitive_analysis):
    """Display competitive analysis dashboard"""
    
    st.header("🏪 Competitive Intelligence Dashboard")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Losing Share", competitive_analysis['summary']['losing_share'], delta=None)
    with col2:
        st.metric("Gaining Share", competitive_analysis['summary']['gaining_share'], delta=None)
    with col3:
        st.metric("Avg Price Gap", f"{competitive_analysis['summary']['avg_price_gap']:.1f}%")
    with col4:
        st.metric("Monitoring", "7 competitors")
    
    st.divider()
    
    # Competitive position chart
    st.subheader("Competitive Position Analysis")
    
    df = competitive_analysis['analysis_df']
    
    # Create scatter plot
    fig = px.scatter(df, x='price_gap_%', y='demand_shift_%',
                    color='position',
                    size='market_share',
                    hover_name='product',
                    hover_data=['your_price', 'competitor_price'],
                    labels={'price_gap_%': 'Price Gap % (You vs Competitor)',
                           'demand_shift_%': 'Demand Shift %'},
                    title='Competitive Position Matrix')
    
    # Add quadrants
    fig.add_hline(y=0, line_dash="dash", line_color="gray")
    fig.add_vline(x=0, line_dash="dash", line_color="gray")
    
    # Add quadrant labels
    fig.add_annotation(x=15, y=15, text="Advantage Zone", showarrow=False, font=dict(color="green"))
    fig.add_annotation(x=15, y=-15, text="Vulnerable Zone", showarrow=False, font=dict(color="red"))
    fig.add_annotation(x=-15, y=15, text="Opportunity Zone", showarrow=False, font=dict(color="orange"))
    fig.add_annotation(x=-15, y=-15, text="Risk Zone", showarrow=False, font=dict(color="purple"))
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.subheader("🏆 Action Recommendations")
    
    for rec in competitive_analysis['recommendations']:
        if rec['priority'] == 'HIGH':
            with st.expander(f"🚨 HIGH PRIORITY: {rec['product']} - {rec['action']}", expanded=True):
                st.write(f"**Reason:** {rec['reason']}")
                st.write(f"**Expected Impact:** {rec['impact']}")
                if st.button(f"Implement for {rec['product']}", key=f"btn_{rec['product']}"):
                    st.success(f"Action queued for {rec['product']}")
        
        elif rec['priority'] == 'MEDIUM':
            with st.expander(f"⚡ MEDIUM PRIORITY: {rec['product']} - {rec['action']}"):
                st.write(f"**Reason:** {rec['reason']}")
                st.write(f"**Expected Impact:** {rec['impact']}")
    
    # Price sensitivity table
    st.subheader("📊 Price Sensitivity Analysis")
    
    sensitivity_table = df[['product', 'price_gap_%', 'demand_shift_%', 'position']].copy()
    sensitivity_table['elasticity'] = sensitivity_table.apply(
        lambda row: 'HIGH' if abs(row['demand_shift_%']) > 8 else 'MEDIUM' if abs(row['demand_shift_%']) > 4 else 'LOW',
        axis=1
    )
    
    st.dataframe(sensitivity_table, use_container_width=True)
    
    return competitive_analysis