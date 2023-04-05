# distributed-banking-system

## Setup for mac
### Running Kafka Server
```
brew install kafka
zookeeper-server-start /usr/local/etc/kafka/zookeeper.properties
kafka-server-start /usr/local/etc/kafka/server.properties
```

### Running the banking system
```
python3 load_balancer.py
python3 server.py --topics read-only transaction --port 5001
python3 server.py --topics transaction --port 5002
```

### Remarks
- this project only supports ['BTC', 'ETH', 'USDT'] as acceptable currencies

### Demo video
- code explaination starts from 8:38