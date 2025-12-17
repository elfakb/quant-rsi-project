# ⚡ QuantRSI: Real-Time Crypto Momentum Scanner

![Python](https://img.shields.io/badge/Python-3.9%2B-blue)
![Apache Kafka](https://img.shields.io/badge/Apache_Kafka-Streaming-black)
![Apache Spark](https://img.shields.io/badge/Apache_Spark-Structured_Streaming-orange)
![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-red)
![Docker](https://img.shields.io/badge/Docker-Containerized-blue)

**QuantRSI** is a  real-time big data pipeline designed to simulate (not real) algorithmic trading strategies. It gets high-frequency cryptocurrency price data calculates technical indicators (RSI) using **Apache Spark Structured Streaming** and visualizes the signals on a live **Streamlit** dashboard.

---


##  Project Overview

QuantRSI is a real-time data pipeline built to simulate algorithmic trading. It processes high-frequency cryptocurrency data to detect trading opportunities instantly.

The system stages:
1.  **Ingestion:** Streaming raw price data using **Kafka**.
2.  **Processing:** Calculating RSI indicators on the data with **Spark Structured Streaming**.
3.  **Visualization:** Displaying live "Buy/Sell" signals on a **Streamlit** dashboard.

---

## 🏗 System Architecture

The pipeline is designed as a decoupled, microservices-oriented architecture running entirely within a **Docker** environment.

```mermaid
graph LR
    subgraph Docker_Host [🐳 Docker Compose Environment]
        style Docker_Host fill:#f9f9f9,stroke:#333,stroke-width:2px,color:black
        
        subgraph Ingestion [1. Ingestion Layer]
            style Ingestion fill:#e3f2fd,stroke:#1565c0,color:black
            A[🐍 Market Sim<br/>(Producer)]
        end

        subgraph Message_Bus [2. Messaging Layer]
            style Message_Bus fill:#fff3e0,stroke:#ef6c00,color:black
            B[(Kafka: Prices)]
            D[(Kafka: Analysis)]
        end

        subgraph Processing [3. Processing Layer]
            style Processing fill:#e8f5e9,stroke:#2e7d32,color:black
            C[⚡ Spark Engine<br/>(Structured Streaming)]
        end

        subgraph Visualization [4. Presentation Layer]
            style Visualization fill:#f3e5f5,stroke:#7b1fa2,color:black
            E[ QuantGrid<br/>(Streamlit)]
        end

        A -->|JSON Stream| B
        B -->|Subscribe| C
        C -->|Windowed Aggregation| D
        D -->|Consume Signals| E
    end


### What is RSI?
The **Relative Strength Index (RSI)** is a momentum indicator used in technical analysis. It measures the speed and magnitude of a security's recent price changes to evaluate overvalued or undervalued conditions.

* **Range:** 0 to 100.
* **Overbought Zone (Signal: SELL):** When RSI > 70. This suggests the asset may be overvalued and a price correction (drop) is likely.
* **Oversold Zone (Signal: BUY):** When RSI < 30. This suggests the asset may be undervalued and a price rebound (rise) is likely.
* **Neutral Zone:** Between 30 and 70.


### Synthetic Data Simulation
**⚠️ Important Note:** This project is a **simulation** intended for educational and engineering purposes.

---

## Running


````markdown
##  Running the Pipeline

To run the full simulation, you will need **4 separate terminal windows**. Follow this specific order to ensure all components connect correctly.

### 1️⃣ Terminal 1
Start the Kafka, Zookeeper, and Spark containers in the background.
```bash
docker-compose up -d
````

### 2️⃣ Terminal 2: 

Start generating synthetic crypto data. This will also automatically create the necessary Kafka topics.

```bash
python producers/crypto_producer.py
```

### 3️⃣ Terminal 3: 

Start the Spark Structured Streaming job to calculate RSI in real-time.

```bash
python spark_engine/main_processor.py
```

### 4️⃣ Terminal 4: Dashboard (Consumer)

Launch the web interface to visualize the data.

```bash
streamlit run dashboard_app.py
```

-----

### Stopping the Project

To stop the simulation and remove the containers (cleaning up resources):

```bash
docker-compose down
```




