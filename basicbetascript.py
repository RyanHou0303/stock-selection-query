import pandas as pd
import numpy as np
import yfinance as yf
import statsmodels.api as sm
from datetime import datetime ,timedelta
TICKER = "JPM"
FACTOR =("TLT")
YEARS = 5
FREQ = "M"
end = pd.Timestamp.today().normalize()
start = end-pd.DateOffset(years=YEARS)
px = yf.download([TICKER,FACTOR],start=start,end=end,auto_adjust=True,progress=False)["Close"]
px = px if isinstance(px,pd.DataFrame) else px.to_frame()

ret = px.resample(FREQ).last().pct_change().dropna()
beta_cov = ret[TICKER].cov(ret[FACTOR])/ret[FACTOR].var()

print(f"[Cov/Var] beta_fin ({TICKER} vs {FACTOR}) = {beta_cov:.4f}")
start = pd.Timestamp.today() - pd.DateOffset(years=5)
end   = pd.Timestamp.today()

#####################################
c_px   = yf.download("C",   start=start, end=end, auto_adjust=True, progress=False)["Close"]
xlf_px = yf.download("XLF", start=start, end=end, auto_adjust=True, progress=False)["Close"]

ret = pd.concat([c_px, xlf_px], axis=1).rename(columns={"C":"C","XLF":"XLF"})
ret = ret.resample("M").last().pct_change().dropna()

# CAPM beta: Cov(C, XLF) / Var(XLF)
beta_c_xlf = ret["C"].cov(ret["XLF"]) / ret["XLF"].var()
print(f"Citigroup vs XLF beta (5Y monthly) : {beta_c_xlf:.4f}")