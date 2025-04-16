#!/usr/bin/env python
from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_extract, trim, to_json, struct, col

def main():
    # Create SparkSession
    spark = SparkSession.builder \
            .appName("KafkaSyslogToJSON") \
            .getOrCreate()

    spark.sparkContext.setLogLevel("WARN")
    
    # Read the stream from Kafka topic "syslog"
    kafka_df = spark.readStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka1:29092,kafka2:29092,kafka3:29092") \
        .option("subscribe", "syslog") \
        .option("startingOffsets", "latest") \
        .load()
    
    # Convert binary value to string
    logs_df = kafka_df.selectExpr("CAST(value AS STRING) as value")
    
    # Parse the 'value' field (assumes format: "timestamp hostname message")
    parsed_df = logs_df.withColumn("timestamp", regexp_extract(trim(col("value")), r"^(\S+)", 1)) \
                       .withColumn("hostname", regexp_extract(trim(col("value")), r"^\S+\s+(\S+)", 1)) \
                       .withColumn("content", regexp_extract(trim(col("value")), r"^\S+\s+\S+\s+(.+)", 1))
    
    # Convert parsed fields to JSON format with the desired keys
    json_df = parsed_df.select(
        to_json(
            struct(
                col("timestamp").alias("TIMESTAMP"),
                col("hostname").alias("HOSTNAME"),
                col("content").alias("MESSAGE")
            )
        ).alias("value")
    )
    
    # Write the JSON output to Kafka topic "SyslogProcessed"
    kafka_query = json_df.writeStream \
        .format("kafka") \
        .option("kafka.bootstrap.servers", "kafka1:29092,kafka2:29092,kafka3:29092") \
        .option("topic", "SyslogProcessed") \
        .option("checkpointLocation", "/tmp/kafka-syslog-checkpoint") \
        .outputMode("append") \
        .start()
    
    # Also, write the JSON output to the console for debugging
    console_query = json_df.writeStream \
        .outputMode("append") \
        .format("console") \
        .option("truncate", "false") \
        .start()
    
    # Await termination for both queries
    kafka_query.awaitTermination()
    console_query.awaitTermination()

if __name__ == "__main__":
    main()
