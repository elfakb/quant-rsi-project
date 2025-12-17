

 # Dosya: producers/crypto_producer.py
import time 
import json 
import random 
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic # Admin modülü eklendi

KAFKA_TOPIC = "crypto-prices" 
KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

def create_topic_if_not_exists():
    try:
        admin_client = KafkaAdminClient(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS, 
            client_id='crypto_admin'
        )
        existing_topics = admin_client.list_topics()
        
        if KAFKA_TOPIC not in existing_topics:
            print(f"⚠️ Topic '{KAFKA_TOPIC}' is not exists. Creating...")
            topic_list = [NewTopic(name=KAFKA_TOPIC, num_partitions=1, replication_factor=1)]
            admin_client.create_topics(new_topics=topic_list, validate_only=False)
            print(f"✅ Topic '{KAFKA_TOPIC}' created!")
        else:
            print(f"✅ Topic '{KAFKA_TOPIC}' already exists.")
            
        admin_client.close()
    except Exception as e:
        print(f"topic creation error: {e}")

def json_serializer(data):
    return json.dumps(data).encode('utf-8')

def get_kafka_producer():
    producer = None 
    while producer is None:
        try:
            producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=json_serializer
            )
        except:
            print("kafka producer connection failed...")
            time.sleep(1)
    return producer

def main():
    create_topic_if_not_exists()
    
    print("producer srtating...")
    producer = get_kafka_producer()

    price = 50000.0
    while True:
        change = random.uniform(-50, 50)
        price = price + change
        
        msg = {
            "timestamp" : time.strftime("%Y-%m-%d %H:%M:%S"),
            "symbol": "BTC/USDT",
            "price_a" : round(price,2)
        }
        producer.send(KAFKA_TOPIC, msg)

        flag = "🟢" if change > 0 else "🔴"
        print(f"{flag} Price: {price:.2f} $ (Change: {change:.2f})")
        
        time.sleep(0.5)

if __name__ == "__main__":
    main()