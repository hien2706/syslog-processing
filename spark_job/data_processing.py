#!/usr/bin/env python
from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_extract, col

def process_batch(batch_df, batch_id):

    if batch_df.rdd.isEmpty():
        print(f"Batch {batch_id} is empty, skipping processing.")
        return
        
    # Print the micro-batch to the terminal for debugging
    print(f"Processing batch: {batch_id}")
    batch_df.show(truncate=False)

    
    # Write the batch to MongoDB using the batch write API
    batch_df.write \
        .format("mongodb") \
        .option("spark.mongodb.connection.uri", "mongodb://hien:hien@mongodb:27017") \
        .option("spark.mongodb.database", "logdb") \
        .option("spark.mongodb.collection", "logs") \
        .mode("append") \
        .save()

def main():
    # Create SparkSession
    spark = SparkSession.builder \
        .appName("KafkaSyslogStreaming") \
        .getOrCreate()

    # Set log level to WARN to reduce verbosity
    spark.sparkContext.setLogLevel("WARN")

    # Read the stream from Kafka topic "syslog"
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka1:29092,kafka2:29092,kafka3:29092") \
        .option("subscribe", "syslog") \
        .option("startingOffsets", "latest") \
        .load()

    # Convert binary key and value to strings
    logs_df = kafka_df.selectExpr(
        "CAST(key AS STRING) as key",
        "CAST(value AS STRING) as value",
        "topic",
        "partition",
        "offset"
    )

    # Parse the 'value' field.
    # The regex extracts:
    #   1. The first non-space sequence as "timestamp"
    #   2. The second non-space sequence as "hostname"
    #   3. Everything following as "content"
    parsed_df = logs_df.withColumn("timestamp", regexp_extract(col("value"), r"^(\S+)", 1)) \
        .withColumn("hostname", regexp_extract(col("value"), r"^\S+\s+(\S+)", 1)) \
        .withColumn("content", regexp_extract(col("value"), r"^\S+\s+\S+\s+(.+)", 1))

    # Select only the parsed columns for output
    output_df = parsed_df.select("timestamp", "hostname", "content")

    # Write the stream using foreachBatch to process each micro-batch:
    # This will both print the data to the terminal and write it to MongoDB.
    query = output_df.writeStream \
        .foreachBatch(process_batch) \
        .outputMode("append") \
        .start()

    query.awaitTermination()

if __name__ == "__main__":
    main()
