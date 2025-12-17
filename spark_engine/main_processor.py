
# Dosya: spark_engine/main_processor.py
import os
import sys
import uuid 
from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col, window, collect_list, element_at, to_json, struct
from pyspark.sql.types import StructType, StructField, StringType, DoubleType, TimestampType
from strategy import calculate_rsi, create_dashboard 

os.environ["JAVA_HOME"] = "/opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk/Contents/Home"
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

def main():
    print("Streaming processor starting...")
    

    unique_checkpoint = f"/tmp/spark_checkpoint_{uuid.uuid4().hex}"
    print(f"Yeni Checkpoint Konumu: {unique_checkpoint}")

    spark = SparkSession.builder.appName("RealTimeQuant").master("local[*]").config("spark.driver.host", "127.0.0.1").config("spark.sql.shuffle.partitions", "2").config("spark.jars.packages", "org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.3").getOrCreate()

    spark.sparkContext.setLogLevel("WARN") 

    schema = StructType([
        StructField("timestamp", TimestampType(), True),
        StructField("symbol", StringType(), True),
        StructField("price_a", DoubleType(), True),
    ])


    processed_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("subscribe", "crypto-prices") \
        .option("startingOffsets", "latest") \
        .load() \
        .select(from_json(col("value").cast("string"), schema, options={"timestampFormat": "yyyy-MM-dd HH:mm:ss"}).alias("data")) \
        .select("data.*") \
        .withWatermark("timestamp", "0 seconds") \
        .groupBy(window("timestamp", "30 seconds", "5 seconds"), "symbol") \
        .agg(collect_list("price_a").alias("prices")) \
        .select(
            col("window.start").alias("timestamp"),
            col("symbol"),
            element_at("prices", -1).alias("last_price"),
            calculate_rsi("prices").alias("rsi_value") 
        )

    kafka_output = processed_df.select(
        to_json(struct("timestamp", "symbol", "last_price", "rsi_value")).alias("value")
    )


    query = kafka_output.writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "localhost:9092") \
        .option("topic", "crypto-analysis") \
        .option("checkpointLocation", unique_checkpoint) \
        .outputMode("update") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()