# Real-time Syslog Processing Pipeline

A scalable, containerized data pipeline for collecting, processing, and analyzing system logs in real-time using modern data engineering tools.

## 📋 Overview

This project implements three different real-time data processing scenarios for system logs:

1. **Scenario 1**: Syslog-ng → Kafka → PySpark → MongoDB
2. **Scenario 2**: Syslog-ng → Kafka → PySpark → Kafka → MongoDB
3. **Scenario 3**: Syslog-ng → Kafka → ksqlDB → Kafka → MongoDB

All components are orchestrated using Docker Compose, making it easy to deploy and experiment with different architectures.

## 🏗️ Architecture

**Scenario 1**:
![Scenario 1](./images/scenario1.jpg)

**Scenario 2**:
![Scenario 2](./images/scenario2.jpg)

**Scenario 3**:
![Scenario 3](./images/scenario3.jpg)

### Components

- **Syslog-ng**: Collects and forwards system logs
- **Apache Kafka**: Message broker for buffering and routing log data
- **PySpark**: Stream processing for log transformation
- **ksqlDB**: SQL-like stream processing inside Kafka ecosystem
- **MongoDB**: Storage for processed logs
- **Monitoring Stack**: Grafana, Prometheus, and a custom latency exporter

## 🔧 Configuration

### Switching Scenarios

Edit the `docker-compose.yml` file to enable/disable specific services for each scenario:

- **Scenario 1**: Enable syslog-ng, kafka, pyspark-direct, and mongodb
- **Scenario 2**: Enable syslog-ng, kafka, pyspark-kafka, kafka-connect, and mongodb
- **Scenario 3**: Enable syslog-ng, kafka, ksqldb, kafka-connect, and mongodb

### Syslog Configuration

The `syslog-ng.conf` file contains the configuration for syslog collection. By default, it listens on UDP port 514.

### Sending Test Logs

Use the provided script to send test logs at a specified rate:
```bash
./send_demo_logs_rate.sh [logs_per_second]
```

## 📊 Monitoring & Analysis

### Latency Dashboard

Access the Grafana dashboard to monitor pipeline latency:
1. Open http://localhost:3000 (default credentials: admin/admin)
2. Navigate to the "Message Latency" dashboard

### Performance Results

Our latency analysis shows:

| Scenario | Mean Latency | Median Latency | Min Latency | Max Latency |
|----------|--------------|----------------|-------------|-------------|
| Scenario 1 | 1.51 s | 1.68 s | 719 ms | 2.27 s |
| Scenario 2 | 501 ms | 438 ms | 212 ms | 736 ms |
| Scenario 3 | 753 ms | 753 ms | 750 ms | 882 ms |

Scenario 2 demonstrates the lowest overall latency, while Scenario 3 shows the most consistent performance.

## 🔍 Directory Structure

```
.
├── connectors/                    # Kafka Connect connectors
├── demo_logs.txt                  # Sample log data
├── docker-compose.yml             # Main orchestration file
├── Dockerfile.PySpark             # PySpark container definition
├── grafana/                       # Grafana dashboards and configuration
├── latency-exporter/              # Custom latency monitoring service
├── mongo-sink-connector.json      # Kafka Connect MongoDB sink configuration
├── prometheus/                    # Prometheus configuration
├── PySpark_requirements.txt       # Python dependencies for PySpark
├── spark_job/                     # PySpark processing scripts
│   ├── data_processing_kafka.py   # For scenario 2
│   └── data_processing.py         # For scenario 1
└── syslog-ng.conf                 # Syslog-ng configuration
```

## 🧪 Testing

To test the full pipeline:

1. Start the containers for your chosen scenario
2. Run the test log generator: `./send_demo_logs_rate.sh 5`
3. Check MongoDB for processed logs:
   ```bash
   docker exec -it mongodb mongosh
   use logdb
   db.logs.find().limit(10)
   ```
4. Monitor latency metrics in the Grafana dashboard

## 📝 License

This project is licensed under the terms included in the LICENSE file.

## 👤 Author

Created by Tran Dai Hien
