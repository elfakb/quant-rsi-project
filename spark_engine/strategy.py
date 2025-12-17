import pandas as pd 
import numpy as np 
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import DoubleType,StringType

@pandas_udf(DoubleType())
def calculate_rsi(prices : pd.Series) -> pd.Series:

    def compute_rsi(price_list):
        if len(price_list) < 3:
            return None
        
        window = 14
        period = 1
        series = pd.Series(price_list)
        delta = series.diff()

        gain = (delta.where(delta>0,0)).rolling(window = window , min_periods=period).mean()
        loss = (-delta.where(delta <0,0)).rolling(window = window, min_periods=period).mean()

        last_loss = loss.iloc[-1]

        if last_loss == 0:
            return 100.0
        
        rs = gain.iloc[-1] / last_loss
        rsi = 100 - (100/ (1 + rs))
        return rsi
    return prices.apply(compute_rsi)

@pandas_udf(StringType())
def create_dashboard(rsi_series: pd.Series) -> pd.Series:

    def visualize(rsi):

        if rsi is None or pd.isna(rsi):
            return "No Data"
        
        filled_length = int(rsi/10)
        bar = "█" * filled_length + "░" * (10 - filled_length)
    
        if rsi >= 70:
            status = "OVERBOUGHT (SELL) 🔻"
        elif rsi <= 30:
            status = "DOWN PRICE (BUY) 🟢"
        else:
            status = "Neutral ⚪️"
            
        # ÇIKTI FORMATI: [████░░] RSI: 45.23 | Durum
        return f"[{bar}] RSI: {rsi:.2f} | {status}"
    return rsi_series.apply(visualize)