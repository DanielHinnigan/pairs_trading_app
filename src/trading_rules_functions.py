import streamlit as st
import numpy as np

def trading_rule(pair_id, upper_bound, lower_bound):
    """
        Strategy 1:
            If the spread is below the lower bound, then buy one of stock 1 and short beta of stock 2. The gain is w[t]=beta*P2[t]-P1[t]
            When the spread is above the upper bound, then unwind the trade: Sell stock 1 and close out the short position by buying beta of stock 2.
            The gain for unwinding is w[t+1]=P1[t+i]-beta*P2[t+i]

            The total gain is w[t+1]+w[t].

            Note that w[t] is the negative of the spread at time t, say s[t]. Also w[t+i]=s[t+i]. As such, the gain is equal to the difference in the spread: s[t+i]-s[t]

    """
    pair = st.session_state.pairs[pair_id]
    
    p1 = pair["Log Price 1"]
    p2 = pair["Log Price 2"]
    beta = pair["Coefficient"]

    in_trade = False
    profits = []
    trades = []
    profit = 0
    spread_t = 0

    for i in range(len(p1)):
        s = p1[i]-p2[i]*beta
    
        if s < lower_bound and in_trade == False:
            in_trade = True
            spread_t = np.exp(p1[i])-beta*np.exp(p2[i])
            trades.append({
                "Type":     "Going-in",
                "Price 1":  np.exp(p1[i]),
                "Price 2":  np.exp(p2[i]),
                "Spread":   spread_t,
                "Date":     pair["Dates"][i]
            })
        elif s>upper_bound and in_trade == True:
            in_trade = False
            spread = np.exp(p1[i])-beta*np.exp(p2[i])
            profit += spread-spread_t
            trades.append({
                "Type":     "Unwinding",
                "Price 1":  np.exp(p1[i]),
                "Price 2":  np.exp(p2[i]),
                "Spread":   spread,
                "Date":     pair["Dates"][i]
            })

        profits.append(profit)

    return profits, trades