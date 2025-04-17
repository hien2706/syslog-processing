```markdown
# Real‑Time Syslog Processing Pipeline

**Data Engineer Project by Tran Dai Hien**  
---

## 🚀 Overview

A highly modular, Docker‑orchestrated real‑time logging pipeline built to collect, process, monitor and store syslog messages at scale. It showcases three processing scenarios—PySpark direct‑to‑MongoDB, PySpark→Kafka→MongoDB, and ksqlDB→Kafka→MongoDB—with end‑to‑end latency analysis and dashboards.

---

## 🔑 Key Features

- **Pluggable Processing Scenarios**  
  1. **Syslog‑ng → Kafka → PySpark → MongoDB**  
  2. **Syslog‑ng → Kafka → PySpark → Kafka → MongoDB**  
  3. **Syslog‑ng → Kafka → ksqlDB → Kafka → MongoDB**

- **Real‑Time Monitoring & Alerts**  
  - Prometheus for metrics scraping  
  - Grafana dashboards for latency, throughput and resource usage  

- **Scalable & Containerized**  
  - Docker Compose orchestrates all components  
  - Easily swap connectors, processing engines or storage back ends  

- **Detailed Latency Analysis**  
  - Mean, median, min/max measurements across scenarios  
  - Visualized in Grafana for quick performance comparisons  

---

## 📂 Repository Structure

```
.
├── connectors/                    # Kafka Connect plugins
│   └── mongo‑kafka‑connect‑1.15.0‑confluent.jar
├── demo_logs.txt                 # Sample syslog messages
├── docker‑compose.yml            # All‑in‑one orchestrator
├── Dockerfile.PySpark            # PySpark streaming image
├── grafana/                      # Grafana dashboards & provisioning
│   ├── dashboards/
│   │   ├── message_latency.json
│   │   └── message_latency_new.json
│   └── provisioning/
│       ├── dashboards/default.yml
│       └── datasources/prometheus.yml
├── hien_note.txt                 # Personal project notes
├── latency‑exporter/             # Custom exporter for latency metrics
│   ├── Dockerfile.latency_exporter
│   ├── latency_exporter.py
│   └── requirements.txt
├── LICENSE                       # MIT License
├── mongo‑sink‑connector.json     # Connector configuration
├── prometheus/                   # Prometheus config
│   └── prometheus.yml
├── PySpark_requirements.txt      # Python dependencies for Spark jobs
├── README.md                     # ← You are here
├── send_demo_logs_rate.sh        # Automated log‑send script
├── spark_job/                    # PySpark streaming applications
│   ├── data_processing.py
│   └── data_processing_kafka.py
└── syslog‑ng.conf                # Syslog‑ng collector configuration
```

---

## ⚙️ Tech Stack

- **Log Collection:** syslog‑ng  
- **Message Broker:** Apache Kafka  
- **Stream Processing:**  
  - PySpark Structured Streaming  
  - ksqlDB (Kafka native SQL engine)  
- **Storage:** MongoDB (via Kafka Connect)  
- **Monitoring:** Prometheus + Grafana  
- **Containerization:** Docker & Docker Compose  
- **Languages & Tools:** Python 3, Scala (Spark), Bash, JSON, YAML  

---

## 🚦 Getting Started

1. **Clone the repo**  
   ```bash
   git clone https://github.com/your‑username/syslog‑processing.git
   cd syslog‑processing
   ```

2. **Configure environment**  
   - Verify `syslog‑ng.conf` for your host  
   - Update `mongo‑sink‑connector.json` (MongoDB URI, database)

3. **Build & launch**  
   ```bash
   docker‑compose up --build
   ```

4. **Send demo logs**  
   ```bash
   ./send_demo_logs_rate.sh 100  # send 100 messages at default rate
   ```

5. **Explore dashboards**  
   - Grafana: `http://localhost:3000` (user/pass: admin/admin)  
   - Prometheus: `http://localhost:9090`  

---

## 🔄 Pipeline Scenarios & Latency

| Scenario                                                   | Mean Latency | Median | Min   | Max   |
|------------------------------------------------------------|-------------:|-------:|------:|------:|
| 1. syslog‑ng → Kafka → PySpark → MongoDB                   | 1.51 s       | 1.68 s | 0.72 s| 2.27 s|
| 2. syslog‑ng → Kafka → PySpark → Kafka → MongoDB          | 0.50 s       | 0.44 s | 0.21 s| 0.74 s|
| 3. syslog‑ng → Kafka → ksqlDB → Kafka → MongoDB           | 0.75 s       | 0.75 s | 0.75 s| 0.88 s|

**Observations:**  
- Scenario 2 (buffered via Kafka) achieved the lowest overall latency.  
- Scenario 3 (ksqlDB) closely trails Scenario 2 and simplifies deployment by pushing SQL processing into Kafka.  
- Scenario 1 is direct but impacted by PySpark micro‑batch overhead.

---

## 📄 License

This project is licensed under the **MIT License**. See [LICENSE](LICENSE) for details.

---

## 📬 Contact

**Tran Dai Hien**  
🌐 LinkedIn: [your‑profile]  
✉️ Email: hien2706@tran‑hien‑fedora  

> “Building scalable, observable data pipelines—one log at a time.”  
```
