# Pairs Trading Platform
A local web-based platform used for simple analysis of pairs of stocks. This project was developed as a personal project. As such, the platform is not fully developed, has poor performance, and needs refining with regards to documentation. 

The platform can pull historical price data from several user-defined ticker symbols using yahoo finance. A series of pairs of two stocks are then found by iterating over every possible pair of stocks, then constructing a linear regression of one log price as a function of the other log price using least-squares for minimization. The residuals are then tested for stationarity using the Augmented Dickey–Fuller test. If the Null Hypothesis is rejected, we regard the two stocks to be cointegrated, and as such, can be used for pairs trading. 

A (for now) fixed trading strategy can then be tested by "buying" the spread and unwinding the position based on user-defined upper and lower bounds. This trading strategy is back tested such that the profitability of the strategy can be judged.


## Prerequisities
- Python Version: 3.13
- [uv](https://docs.astral.sh/uv/getting-started/installation/) package manager installed. Install using
```bash
pip install uv
```

## Installation
- Clone the repository
- Install the dependencies by writing the following in the terminal
```bash
uv sync
```

## Launching the application
Use 
```bash
uv run streamlit run main.py
```
to run the application
