import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
from statsmodels.tsa.stattools import adfuller
from scipy.optimize import minimize

def get_ticker_data(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(auto_adjust=False, period="max")

    if hist.shape[0] != 0:
        log_price = np.log(hist["Close"])
        return [symbol, log_price]
    return None

def linear_reg(params, p2):
    return params[0]+params[1]*p2

def calculate_pairs():
    alpha = 0.01
    def least_squares(params, p1, p2):
        return np.sum((p1-linear_reg(params,p2))**2)
    
    ticker_data = []
    for symbol in np.array(st.session_state.ticker_df):
        ticker_data.append(get_ticker_data(symbol))

    st.session_state.pairs = []
    for i in ticker_data:
        for j in ticker_data:
            s1 = i[0]
            s2 = j[0]

            if s1 == s2:
                continue

            start_date = i[1].index[0] if i[1].index[0] > j[1].index[0] else j[1].index[0] 
            end_date = i[1].index[-1] if i[1].index[-1] < j[1].index[-1] else j[1].index[-1]

            p1 = np.array(i[1].loc[start_date:end_date])
            p2 = np.array(j[1].loc[start_date:end_date])

            try:
                params = minimize(least_squares, x0=(0,0), args=(p1, p2))["x"]
            except:
                print(f"Error with: {s1} and {s2}")
                break
            residuals = p1-linear_reg(params,p2)
            p_value = adfuller(residuals)[1]
            
            # Reject null hypothesis -> Stationary residuals
            if p_value < alpha:
                print(f"Appended pair: {s1}, {s2}")
                to_append = {
                    "Ticker 1": s1,
                    "Ticker 2": s2,
                    "Coefficient": params[1],
                    "Log Price 1": p1,
                    "Log Price 2": p2,
                    "Dates": i[1].loc[start_date:end_date].index
                }
                st.session_state.pairs.append(to_append)
