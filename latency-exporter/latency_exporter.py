from prometheus_client import start_http_server, Gauge, Counter, Histogram
import time
import threading
import pymongo
import socket
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Prometheus metrics
MESSAGE_LATENCY = Histogram('message_processing_latency_seconds', 
                            'Latency between message sent and stored in MongoDB', 
                            buckets=[0.1, 0.5, 1, 2, 5, 10, 20, 50, 100])  # Histogram to track latency with buckets
MESSAGES_SENT = Counter('messages_sent_total', 'Total number of messages sent')
MESSAGES_STORED = Counter('messages_stored_total', 'Total number of messages stored in MongoDB')
LATEST_LATENCY = Gauge('latest_message_latency_seconds', 'Latest message latency in seconds')
MESSAGES_NOT_FOUND = Counter('messages_not_found_total', 'Total number of messages not found in MongoDB')

# Additional metrics for min, max, and standard deviation
MIN_LATENCY = Gauge('min_message_latency_seconds', 'Minimum message latency in seconds')
MAX_LATENCY = Gauge('max_message_latency_seconds', 'Maximum message latency in seconds')
STDDEV_LATENCY = Gauge('stddev_message_latency_seconds', 'Standard deviation of message latency in seconds')

# MongoDB connection
MONGODB_URI = os.environ.get('MONGODB_URI', 'mongodb://hien:hien@mongodb:27017/logdb?authSource=admin')
client = pymongo.MongoClient(MONGODB_URI)
db = client.logdb
collection = db.logs

# Function to send a test message
def send_test_message():
    try:
        # Generate a unique message ID
        message_id = f"test-id-{datetime.now().timestamp()}"
        timestamp_sent = datetime.now().timestamp()
        
        # Send message via UDP
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Format the message to match your syslog-ng setup
        message = f"test message - unique id {message_id} - sent at {timestamp_sent}"
        sock.sendto(message.encode(), ('syslog-ng', 514))
        sock.close()
        
        MESSAGES_SENT.inc()
        logger.info(f"Sent test message with ID: {message_id}")
        
        # Check MongoDB for the message arrival
        monitor_message_arrival(message_id, timestamp_sent)
    except Exception as e:
        logger.error(f"Error sending test message: {e}")

# Function to monitor when message appears in MongoDB
def monitor_message_arrival(message_id, timestamp_sent):
    max_retries = 50  # Increased retries
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Query MongoDB - search in content field which is where your message appears to be stored
            query = {"content": {"$regex": message_id}}
            result = collection.find_one(query)
            
            if result:
                timestamp_received = datetime.now().timestamp()
                latency = timestamp_received - timestamp_sent
                
                # Record the latency value
                MESSAGE_LATENCY.observe(latency)  # Histogram to track latency
                LATEST_LATENCY.set(latency)

                # Dynamically track min/max latency
                current_min = MIN_LATENCY._value.get() if MIN_LATENCY._value.get() is not None else latency
                current_max = MAX_LATENCY._value.get() if MAX_LATENCY._value.get() is not None else latency

                # Exclude 0 as a valid min latency
                if latency > 0:
                    # Ensure we don't set 0 as min latency
                    if current_min > 0:
                        MIN_LATENCY.set(min(current_min, latency))
                    elif current_min == 0:
                        MIN_LATENCY.set(latency)  # Set the first valid latency greater than 0

                if latency > 0:
                    MAX_LATENCY.set(max(current_max, latency))


                # Collect latencies for standard deviation calculation
                latencies = [current_min, current_max, latency]
                STDDEV_LATENCY.set((sum((x - latency)**2 for x in latencies) / len(latencies))**0.5)  # Standard deviation calculation
                
                MESSAGES_STORED.inc()
                
                logger.info(f"Message {message_id} found in MongoDB. Latency: {latency:.4f} seconds")
                logger.info(f"Document found: {result}")
                return
                
        except Exception as e:
            logger.error(f"Error querying MongoDB: {e}, full error: {str(e)}")
        
        retry_count += 1
        time.sleep(0.2)  # Check every 200ms - giving more time per retry
    
    # Message not found after all retries
    MESSAGES_NOT_FOUND.inc()
    logger.warning(f"MESSAGE NOT FOUND IN MONGODB: Message {message_id} not found after {max_retries} retries")
    logger.warning(f"PIPELINE BREAKDOWN: Message was sent to syslog-ng but never reached MongoDB")
    logger.warning(f"MongoDB collection schema: {list(collection.find_one().keys()) if collection.find_one() else 'No documents found'}")

# Periodically send test messages
def periodic_message_sender():
    while True:
        send_test_message()
        time.sleep(10)  # Send a message every 10 seconds

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    
    # Print the collection schema at startup to help with debugging
    try:
        doc = collection.find_one()
        if doc:
            logger.info(f"MongoDB document structure: {list(doc.keys())}")
            logger.info(f"Sample document: {doc}")
        else:
            logger.warning("No documents found in MongoDB collection")
    except Exception as e:
        logger.error(f"Error checking MongoDB structure: {e}")
    
    # Start the message sender thread
    sender_thread = threading.Thread(target=periodic_message_sender, daemon=True)
    sender_thread.start()
    
    logger.info("Latency exporter started. Metrics available at :8000")
    
    # Keep the main thread alive
    while True:
        time.sleep(1)
