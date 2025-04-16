#!/bin/bash
# send_demo_logs_rate.sh
# This script sends demo syslog messages read from a file to UDP port 514 at a specified target throughput (in KB/s).
# Usage: ./send_demo_logs_rate.sh [TARGET_KB]
# Example: ./send_demo_logs_rate.sh 10  # sends about 10 KB of data per second

# Set the target throughput in KB/s (default 1 KB/s if not provided)
TARGET_KB=${1:-1}
TARGET_BYTES=$((TARGET_KB * 1024))

# Define the demo log file
DEMO_LOG_FILE="demo_logs.txt"

# Create the demo log file if it does not exist
if [ ! -f "$DEMO_LOG_FILE" ]; then
  cat <<EOF > "$DEMO_LOG_FILE"
2025-03-19T10:18:19+00:00 tranhien-Virtual-Machine This is a test message 2706
2025-03-19T10:27:06+00:00 48806fc03cfc -- MARK --
2025-03-19T10:35:00+00:00 server01 Some other test log message
EOF
  echo "Demo log file created: $DEMO_LOG_FILE"
fi

# Calculate total bytes in the file (for planning purposes)
FILE_SIZE=$(wc -c < "$DEMO_LOG_FILE")
echo "Target throughput: ${TARGET_KB} KB/s (${TARGET_BYTES} bytes/s)"
echo "Log file size: ${FILE_SIZE} bytes"
echo "Contents of $DEMO_LOG_FILE:"
cat "$DEMO_LOG_FILE"
echo ""

# Function to send messages until target bytes are sent within one second
send_messages_for_one_second() {
  local bytes_sent=0
  local start_time=$(date +%s.%N)
  
  # Loop reading the file repeatedly until we've sent enough bytes
  while [ $bytes_sent -lt $TARGET_BYTES ]; do
    while IFS= read -r line; do
      # Send the line via UDP to port 514
      echo "$line" | nc -w0 -u localhost 514
      
      # Count bytes accurately - include newline character
      line_bytes=$((${#line} + 1))
      bytes_sent=$((bytes_sent + line_bytes))
      
      echo "Sent: $line (${line_bytes} bytes), total: $bytes_sent/$TARGET_BYTES bytes"
      
      # Check if we've reached the target
      if [ $bytes_sent -ge $TARGET_BYTES ]; then
        break
      fi
    done < "$DEMO_LOG_FILE"
    
    # If we've sent all the file contents but haven't reached the target,
    # we'll loop back and start reading the file again
  done
  
  # Calculate elapsed time more precisely
  local end_time=$(date +%s.%N)
  local elapsed=$(echo "$end_time - $start_time" | bc)
  local send_rate=$(echo "scale=2; $bytes_sent / $elapsed" | bc)
  
  echo "Sent $bytes_sent bytes in $elapsed seconds ($send_rate bytes/sec)"
  
  # Sleep for remaining time in the one-second interval
  if (( $(echo "$elapsed < 1" | bc -l) )); then
    local sleep_time=$(echo "1 - $elapsed" | bc)
    echo "Sleeping for $sleep_time seconds..."
    sleep $sleep_time
  fi
}

echo "Starting to send logs at ${TARGET_KB} KB/s. Press Ctrl+C to stop."

# Loop indefinitely, sending messages at the target rate each second
while true; do
  send_messages_for_one_second
done