#  dashboard_app.py
import streamlit as st
import pandas as pd
import json
from kafka import KafkaConsumer
import time

st.set_page_config(page_title="QuantFlow Monitor", layout="wide", page_icon="📊")
st.title("QuantRSI: Algorithmic Trading Monitor ")


st.markdown("""
<style>
    [data-testid="stMetricValue"] {
        font-size: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Kafka Consumer
@st.cache_resource
def get_consumer():
    return KafkaConsumer(
        "crypto-analysis",
        bootstrap_servers="localhost:9092",
        value_deserializer=lambda m: json.loads(m.decode('utf-8')),
        auto_offset_reset='latest'
    )

consumer = get_consumer()


if 'data' not in st.session_state:
    st.session_state['data'] = pd.DataFrame(columns=["Time", "Symbol", "Price ($)", "RSI", "Signal", "Status"])

col1, col2, col3, col4 = st.columns(4)
with col1: metric_price = st.empty()
with col2: metric_rsi = st.empty()
with col3: metric_signal = st.empty()
with col4: metric_count = st.empty()

st.divider() # Araya çizgi


table_placeholder = st.empty()

try:
    for message in consumer:
        record = message.value
        

        price = record.get('last_price', 0.0)
        

        rsi = record.get('rsi_value')
        if rsi is None:
            rsi = 50.0
            
        timestamp = pd.to_datetime(record.get('timestamp', time.strftime("%Y-%m-%d %H:%M:%S"))).strftime('%H:%M:%S')
        

        if rsi >= 70:
            signal = "SELL"
            status = "🔴 OVERBOUGHT"
            rsi_delta_color = "inverse"
        elif rsi <= 30:
            signal = "BUY"
            status = "🟢 OVERSOLD"
            rsi_delta_color = "off"
        else:
            signal = "WAIT"
            status = "⚪ NEUTRAL"
            rsi_delta_color = "normal"

   
        new_row = {
            "Time": timestamp,
            "Symbol": "BTC/USDT",
            "Price ($)": price,
            "RSI": rsi,
            "Signal": signal,
            "Status": status
        }
        

        df_new = pd.DataFrame([new_row])
        st.session_state['data'] = pd.concat([st.session_state['data'], df_new], ignore_index=True)
        
        # Son 15 veriyi tut 
        df_display = st.session_state['data'].tail(15)
      
        df_display = df_display.iloc[::-1]



        metric_price.metric("Current Price", f"${price:,.2f}")
        metric_rsi.metric("RSI Momentum", f"{rsi:.2f}", delta_color=rsi_delta_color)
        
        if signal == "SELL":
            metric_signal.error(f"{status}")
        elif signal == "BUY":
            metric_signal.success(f"{status}")
        else:
            metric_signal.info(f"{status}")
            
        metric_count.metric("Processed Data", f"{len(st.session_state['data'])} items")

        
        def color_rows(row):
            if row['Signal'] == 'BUY':
                return ['background-color: rgba(0, 255, 0, 0.1); color: lightgreen'] * len(row)
            elif row['Signal'] == 'SELL':
                return ['background-color: rgba(255, 0, 0, 0.1); color: pink'] * len(row)
            else:
                return [''] * len(row)

        styled_df = df_display.style.apply(color_rows, axis=1).format({
            "Price ($)": "${:,.2f}",
            "RSI": "{:.2f}"
        })

        table_placeholder.dataframe(
            styled_df, 
            use_container_width=True, 
            hide_index=True,
            height=600
        )
        
        time.sleep(0.3)

except KeyboardInterrupt:
    print("EXİT.")