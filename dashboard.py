import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

# Set page config
st.set_page_config(
    page_title="Trading Dashboard",
    page_icon="📈",
    layout="wide"
)

# Load trade data
@st.cache_data(ttl=30)  # Cache for 30 seconds
def load_trade_data():
    try:
        df = pd.read_csv('trade_log.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    except Exception as e:
        st.error(f"Error loading trade data: {e}")
        return pd.DataFrame()

# Calculate metrics for a specific strategy
def calculate_strategy_metrics(df, strategy):
    strategy_df = df[df['strategy'] == strategy]
    total_trades = len(strategy_df)
    total_pnl = strategy_df['pnl'].sum()
    win_rate = len(strategy_df[strategy_df['pnl'] > 0]) / total_trades * 100 if total_trades > 0 else 0
    return total_trades, total_pnl, win_rate

# Main dashboard
def main():
    st.title("Trading Dashboard")
    
    # Load data
    df = load_trade_data()
    
    if df.empty:
        st.warning("No trade data available")
        return
    
    # Get unique strategies
    strategies = df['strategy'].unique()
    
    # Create tabs for each strategy
    tabs = st.tabs(["All Strategies"] + [f"Strategy: {s}" for s in strategies])
    
    # All Strategies Tab
    with tabs[0]:
        st.header("All Strategies Overview")
        
        # Key metrics for all strategies
        col1, col2, col3 = st.columns(3)
        
        with col1:
            total_trades = len(df)
            st.metric("Total Trades", total_trades)
        
        with col2:
            total_pnl = df['pnl'].sum()
            st.metric("Total P&L", f"${total_pnl:.2f}")
        
        with col3:
            win_rate = len(df[df['pnl'] > 0]) / len(df) * 100 if len(df) > 0 else 0
            st.metric("Overall Win Rate", f"{win_rate:.1f}%")
        
        # Strategy comparison
        st.subheader("Strategy Performance Comparison")
        strategy_performance = df.groupby('strategy').agg({
            'pnl': 'sum',
            'pnl_pct': 'mean',
            'pair': 'count'
        }).reset_index()
        strategy_performance.columns = ['Strategy', 'Total P&L', 'Avg P&L %', 'Number of Trades']
        st.dataframe(strategy_performance)
        
        # Overall P&L chart
        st.subheader("Overall Cumulative P&L")
        df['cumulative_pnl'] = df['pnl'].cumsum()
        fig = px.line(df, x='timestamp', y='cumulative_pnl', 
                     title="Cumulative Profit/Loss (All Strategies)")
        st.plotly_chart(fig, use_container_width=True)
    
    # Individual Strategy Tabs
    for i, strategy in enumerate(strategies, 1):
        with tabs[i]:
            st.header(f"Strategy: {strategy}")
            
            # Filter data for this strategy
            strategy_df = df[df['strategy'] == strategy]
            
            # Key metrics for this strategy
            col1, col2, col3 = st.columns(3)
            
            with col1:
                total_trades = len(strategy_df)
                st.metric("Total Trades", total_trades)
            
            with col2:
                total_pnl = strategy_df['pnl'].sum()
                st.metric("Total P&L", f"${total_pnl:.2f}")
            
            with col3:
                win_rate = len(strategy_df[strategy_df['pnl'] > 0]) / total_trades * 100 if total_trades > 0 else 0
                st.metric("Win Rate", f"{win_rate:.1f}%")
            
            # Recent trades for this strategy
            st.subheader("Recent Trades")
            st.dataframe(strategy_df.head(10))
            
            # Strategy P&L chart
            st.subheader("Strategy Cumulative P&L")
            strategy_df['cumulative_pnl'] = strategy_df['pnl'].cumsum()
            fig = px.line(strategy_df, x='timestamp', y='cumulative_pnl', 
                         title=f"Cumulative Profit/Loss ({strategy})")
            st.plotly_chart(fig, use_container_width=True)
            
            # Performance by pair for this strategy
            st.subheader("Performance by Trading Pair")
            pair_performance = strategy_df.groupby('pair').agg({
                'pnl': 'sum',
                'pnl_pct': 'mean'
            }).reset_index()
            fig = px.bar(pair_performance, x='pair', y='pnl', 
                        title=f"P&L by Trading Pair ({strategy})")
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()