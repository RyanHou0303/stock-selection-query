from pandas.tseries.offsets import BDay
import numpy as np, pandas as pd, yfinance as yf
from typing import List, Optional, Dict
import math, time, warnings
from openpyxl import Workbook
from openpyxl.utils import get_column_letter

import time,math,warnings
#first, i will create a scoring metrics to track the 10 tickers that Eric mentioned
TICKERS = ["IBM","GE","GM","BA","T","DD","C","KO","XOM","MRK"]
t0 = pd.Timestamp("2025-09-07")

#############################################################################################################
#get the fundamentals
# since we try to predict future 4- 5 weeks return, we use previous 1 month historical price to analysis momentum, past 4 quarter's financial to analysis value, and carry

#value and carry of the stock(p/b, PEG, didvidend, FCF)
def get_value(info:dict,keys:List[str],default=np.nan):
        return

def latestprice(tk:yf.Ticker)->Optional[float]:
    p = None
    try:
        p=tk.fast_info.get("lastPrice")
    except Exception:
        pass
    if not p:
        h = tk.history(period="5d")
        if not h.empty:
            p = float(h["Close"].dropna().iloc[-1])
    return p

#we try to get the long term growth rate of the stock
def _safe_pct(x:Optional[float])->Optional[float]:
    if x is None or pd.isna(x):
        return None
    x = float(x)
    return x*100.0 if x<1.0 else x
def peg_from_yf(sym: str)->Optional[float]:
    tk = yf.Ticker(sym)
    info ={}
    try:
        info = tk.get_info()
    except Exception:
        info={}
    forward_pe = info.get("forwardPE")
    try:
        ge = tk.get_growth_estimates()
    except Exception:
        ge = None
    g_1y = None
    if isinstance(ge,pd.DataFrame):
        if "+1y" in ge.index and "stockTrend" in ge.columns:
            g_1y = _safe_pct(ge.loc["+1y", "stockTrend"])
    if forward_pe and forward_pe>0 and g_1y and g_1y>0:
        peg_1y_fwd = forward_pe/g_1y
        return peg_1y_fwd
    else:
        return None
def fetch_fundamentals(tickers:List[str])->pd.DataFrame:
    rows=[]
    for t in tickers:
        tk = yf.Ticker(t)
        try:
            info = tk.get_info()
        except Exception:
            info={}
        price = latestprice(tk)
        trailingPE = info.get("trailingPE")
        priceToBook = info.get("priceToBook")
        forwardPE = info.get("forwardPE")
        pegRatio = peg_from_yf(t)


        rows.append({
            "symbol":t,
            "latest price":price,
            "trailingPE":trailingPE,
            "forwardPE":forwardPE,
            "priceToBook":priceToBook,
            "pegRatio": pegRatio
        })
    df = pd.DataFrame(rows)
    return pd.DataFrame(rows)
a =fetch_fundamentals(TICKERS)


#######################################################
#consider the momentum factor

# we consider 2 month data,
def fetch_momentum(tickers:List[str],t0:pd.Timestamp,lookback:int =42)->pd.DataFrame:
    start_date = (t0-pd.offsets.Day(130)).date()
    end_date = t0.date()
    data = yf.download(
        tickers = " ".join(tickers),
        start = start_date,end= end_date,
        interval = "1d",
        auto_adjust = True,
        group_by = "ticker",
        progress = False
    )
    closes = {}
    for t in tickers:
        try:
            close = data[(t,"Close")] if isinstance(data.columns,pd.MultiIndex) else data["Close"]
        except Exception:
            close = data["Close"]
        closes[t] = pd.to_numeric(close,errors="coerce")
    prices = pd.DataFrame(closes).dropna(how="all").sort_index()
    prices = prices.loc[prices.index<=(t0-BDay(1))]
    ret1b = prices/prices.shift(lookback)-1.0
    latest = ret1b.iloc[-1].rename("momentum").reset_index()
    latest.columns = ["symbol", "momentum"]
    return latest
momentum = fetch_momentum(TICKERS, t0=t0, lookback=42)
df = a.merge(momentum, on="symbol", how="left")
df["rank_momentum"] =(-df["momentum"]).rank(method="min").astype(int)
df_sorted = df.sort_values(["rank_momentum","momentum"],ascending=[True,False])
print(df_sorted[["symbol", "momentum", "rank_momentum",
                 "priceToBook", "pegRatio", "trailingPE", "forwardPE", "latest price"]])





