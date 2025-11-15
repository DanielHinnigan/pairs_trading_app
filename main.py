import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

from src.pairs_functions import calculate_pairs
from src.trading_rules_functions import trading_rule


# --------------------------- INITIALIZE PAGE ---------------------
if 'ticker_df' not in st.session_state:
    st.session_state.ticker_df = pd.Series()
if "pairs" not in st.session_state:
    st.session_state.pairs = []
if "pair_to_visualize" not in st.session_state:
    st.session_state.pair_to_visualize = None
if "ticker_data" not in st.session_state:
    st.session_state.ticker_data = {}
st.set_page_config(
    layout="wide"
)

# ---------------------------- ADD TICKERS SECTION .--------------------------------

st.title("Control Tickers to Check")

# Display the table with embedded controls
st.subheader("Tickers")

file_tickers = st.file_uploader("Upload file containing tickers. The tickers need to be in a column labelled 'Ticker'. For example, use the example_symbols.csv file located under the data folder")
if file_tickers is not None:
        df = pd.read_csv(file_tickers)["Ticker"]
        st.session_state.ticker_df = pd.concat([st.session_state.ticker_df, df], ignore_index=True)
        st.session_state.ticker_df.drop_duplicates(inplace=True) # Maybe not the most effective method?

# Create a container for the table
table_container = st.container(height=500)

with table_container:
    if st.button("Delete all entries"):
        st.session_state.ticker_df = st.session_state.ticker_df.iloc[:0]
        st.rerun()

    # Display headers
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Ticker**")
    with col2:
        st.write("**Action**")
    st.divider()
    
    # Display existing rows with edit/delete controls
    rows_to_delete = []
    for idx in range(len(st.session_state.ticker_df)):
        row = st.session_state.ticker_df.iloc[idx]
        col1, col2 = st.columns(2)
        
        with col1:
            # Editable name field
            new_ticker = st.text_input(
                "Ticker", 
                value=row,
                key=f"name_{idx}",
                label_visibility="collapsed"
            )
            st.session_state.ticker_df.iloc[idx] = new_ticker

        with col2:
            # Delete button
            if st.button("🗑️", key=f"delete_{idx}", help="Delete row"):
                rows_to_delete.append(idx)
    
    # Add new row section (embedded in the table)
    st.divider()
st.write("**Add New Row**")
col1, col2 = st.columns([2, 1])

with col1:
    new_ticker = st.text_input(
        "New Ticker", 
        value="",
        key="new_ticker",
        placeholder="Enter ticker...",
        label_visibility="collapsed"
    )

with col2:
    add_disabled = not (new_ticker.strip())
    if st.button("➕", key="add_row", disabled=add_disabled, help="Add new row"):
        new_row = pd.Series(data=new_ticker)
        st.session_state.ticker_df = pd.concat([st.session_state.ticker_df, new_row], ignore_index=True)
        st.session_state.ticker_df.drop_duplicates(inplace=True)
        st.rerun()

# Process deletions
if rows_to_delete:
    st.session_state.ticker_df = st.session_state.ticker_df.drop(rows_to_delete).reset_index(drop=True)
    st.rerun()

# -------------------------------- CALCULATE PAIRS SECTION ----------------------------------------

st.title("Find Pairs")
st.button("Calculate Pairs", on_click=calculate_pairs)
pairs_container = st.container(height=500)
with pairs_container:
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.write("**Pair ID**")
    with col2:
        st.write("**Ticker 1**")
    with col3:
        st.write("**Ticker 2**")
    with col4:
        st.write("**Coefficient**")
    with col5:
        st.write("**Visualize**")
    st.divider()

    for idx in range(len(st.session_state.pairs)):
        row = st.session_state.pairs[idx]
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            id = st.text_input(
                "id",
                value=idx,
                key=f"pair_pairid_{idx}",
                label_visibility="collapsed"
            )
        with col2:
            ticker1 = st.text_input(
                "ticker1",
                value=row["Ticker 1"],
                key=f"pair_ticker1_{row["Ticker 1"]}_{idx}",
                label_visibility="collapsed"
            )
        with col3:
            ticker2 = st.text_input(
                "ticker2",
                value=row["Ticker 2"],
                key=f"pair_ticker2_{row["Ticker 2"]}_{idx}",
                label_visibility="collapsed"
            )
        with col4:
            coefficient = st.text_input(
                "coefficient",
                value=np.round(row["Coefficient"],5),
                key=f"pair_coefficient_{row["Coefficient"]}_{idx}",
                label_visibility="collapsed"
            )
        with col5:
            if st.button("Visualize", key=f"pair_visualize_{idx}", use_container_width=True):
                st.session_state.pair_to_visualize = idx



# ---------------------------------- VISUALIZATION SECTION -------------------------
st.title("Visualization")
if st.session_state.pair_to_visualize is not None:
    # Get data corresponding to the pair that the user wants to visualize
    idx = st.session_state.pair_to_visualize
    pair = st.session_state.pairs[idx]

    # First plot: Plot of log prices as a function of time
    prices = pd.DataFrame({
        pair["Ticker 1"]: pair["Log Price 1"],
        pair["Ticker 2"]: pair["Log Price 2"]
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=pair["Dates"],
        y=pair["Log Price 1"],
        name=pair["Ticker 1"],
        mode="lines"
    ))
    fig.add_trace(go.Scatter(
        x=pair["Dates"],
        y=pair["Log Price 2"],
        name=pair["Ticker 2"],
        mode="lines"
    ))

    fig.update_layout(
        title=f"Log Prices of {pair['Ticker 1']} and {pair['Ticker 2']}",
        xaxis_title="Date",
        yaxis_title="Log Prices"
    )

    st.plotly_chart(fig)

    # Second plot: Spread
    spread = pair["Log Price 1"] - pair["Coefficient"]*pair["Log Price 2"]
    fig = px.line(y=spread, x=pair["Dates"])
    fig.update_layout(
        title=f"Spread between {pair['Ticker 1']} and {pair['Ticker 2']} using Log Prices",
        xaxis_title="Date",
        yaxis_title="Spread"
    )

    st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------- BACK TESTING SECTION --------------------------------
st.title("Trading Rules & Back Testing")
upper_bound = float(st.text_input("Upper Bound", value=0))
lower_bound = float(st.text_input("Lower Bound", value=0))
pair_id = int(st.text_input("Pair ID to trade", value=-1))

if st.button("Try Trading Rule"):
    profits, trades = trading_rule(pair_id, upper_bound, lower_bound)
    pair = st.session_state.pairs[pair_id]

    # ----------- Profits Chart
    fig = go.Figure()
    fig.add_trace(go.Bar(x=pair["Dates"], y=profits))

    fig.update_layout(
        title="Profits",
        xaxis_title="Date",
        yaxis_title="Profit (USD)"
    )

    st.plotly_chart(fig, use_container_width=True)

    # ------------ Plot showing positions on price plot
    fig1 = go.Figure()
    fig2 = go.Figure()


    # Initial data
    end_date = trades[0]["Date"]
    end_idx = pair["Dates"].get_loc(end_date)
    data_to_plot = {
            "Dates": pair["Dates"][:end_idx],
            "Log Price 1": pair["Log Price 1"][:end_idx],
            "Log Price 2": pair["Log Price 2"][:end_idx],
            "Spread": pair["Log Price 1"][:end_idx]-pair["Coefficient"]*pair["Log Price 2"][:end_idx]
    }
    fig1.add_trace(go.Scatter(
                x=data_to_plot["Dates"],
                y=data_to_plot["Log Price 1"],
                mode="lines",
                name="No Position",
                line=dict(color="grey", width=1)
    ))
    fig1.add_trace(go.Scatter(
        x=data_to_plot["Dates"],
        y=data_to_plot["Log Price 2"],
        mode="lines",
        name="No Position",
        line=dict(color="grey", width=1)
    ))
    fig2.add_trace(go.Scatter(
        x=data_to_plot["Dates"],
        y=data_to_plot["Spread"],
        mode="lines",
        name="No Position",
        line=dict(color="grey", width=1)
    ))

    # Start of trading strategy data
    for idx in range(len(trades)-1):
        start_date = trades[idx]["Date"]
        end_date = trades[idx+1]["Date"]

        start_idx = pair["Dates"].get_loc(start_date)
        end_idx = pair["Dates"].get_loc(end_date)

        data_to_plot = {
            "Dates": pair["Dates"][start_idx:end_idx],
            "Log Price 1": pair["Log Price 1"][start_idx:end_idx],
            "Log Price 2": pair["Log Price 2"][start_idx:end_idx],
            "Spread": pair["Log Price 1"][start_idx:end_idx]-pair["Coefficient"]*pair["Log Price 2"][start_idx:end_idx]
        }

        if trades[idx]["Type"] == "Going-in":
            fig1.add_trace(go.Scatter(
                x=data_to_plot["Dates"],
                y=data_to_plot["Log Price 1"],
                mode="lines",
                name="Going-in",
                line=dict(color="orange", width=1)
            ))
            fig1.add_trace(go.Scatter(
                x=data_to_plot["Dates"],
                y=data_to_plot["Log Price 2"],
                mode="lines",
                name="Going-in",
                line=dict(color="orange", width=1)
            ))
            fig2.add_trace(go.Scatter(
                x=data_to_plot["Dates"],
                y=data_to_plot["Spread"],
                mode="lines",
                name="Going-in",
                line=dict(color="orange", width=1)
            ))

        elif trades[idx]["Type"] == "Unwinding":
            fig1.add_trace(go.Scatter(
                x=data_to_plot["Dates"],
                y=data_to_plot["Log Price 1"],
                mode="lines",
                name="Unwinding",
                line=dict(color="blue", width=1)
            ))
            fig1.add_trace(go.Scatter(
                x=data_to_plot["Dates"],
                y=data_to_plot["Log Price 2"],
                mode="lines",
                name="Unwinding",
                line=dict(color="blue", width=1)
            ))
            fig2.add_trace(go.Scatter(
                x=data_to_plot["Dates"],
                y=data_to_plot["Spread"],
                mode="lines",
                name="Unwinding",
                line=dict(color="blue", width=1)
            ))

    fig2.add_hline(upper_bound, line_width=1, line_color="red")
    fig2.add_hline(lower_bound,line_width=1, line_color="green")

    fig1.update_layout(
        title=f"Log Prices of {pair["Ticker 1"]} and {pair["Ticker 2"]}",
        showlegend=False,
        xaxis_title="Date",
        yaxis_title="Log Price"
    )
    fig2.update_layout(
        title=f"Spread of {pair["Ticker 1"]} and {pair["Ticker 2"]} using log prices",
        showlegend=False,
        xaxis_title="Date",
        yaxis_title="Spread"
    )
    st.plotly_chart(fig1, use_container_width=True)
    st.plotly_chart(fig2, use_container_width=True)

    # ----------------- Table showing positions
    table = st.container(border=True)
    with table:
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.write("**Order Type**")
        with col2:
            st.write(f"**Price of {pair['Ticker 1']} (USD)**")
        with col3:
            st.write(f"**Price of {pair['Ticker 2']} (USD)**")
        with col4:
            st.write(f"**Spread (USD)**")
        with col5:
            st.write(f"**Date**")

        for idx in range(len(trades)):
            with col1:
                st.text_input(
                    "Order Type",
                    value=trades[idx]["Type"],
                    key=f"order_type_{idx}",
                    label_visibility="collapsed"
                )
            with col2:
                st.text_input(
                    "Price 1",
                    value=np.round(trades[idx]["Price 1"],5),
                    key=f"price_1_trade_strategy_{idx}",
                    label_visibility="collapsed"
                )
            with col3:
                st.text_input(
                    "Price 2",
                    value=np.round(trades[idx]["Price 2"],5),
                    key=f"price_2_trade_strategy_{idx}",
                    label_visibility="collapsed"
                )
            with col4:
                st.text_input(
                    "Spread",
                    value=np.round(trades[idx]["Spread"],5),
                    key=f"spread_trade_strategy_{idx}",
                    label_visibility="collapsed"
                )
            with col5:
                st.text_input(
                    "Date",
                    value=trades[idx]["Date"],
                    key=f"Date_trade_strategy_{idx}",
                    label_visibility="collapsed"
                )