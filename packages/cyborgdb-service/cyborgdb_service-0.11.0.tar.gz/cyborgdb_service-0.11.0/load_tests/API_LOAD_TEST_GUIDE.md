# CyborgDB Load Testing Suite

A comprehensive load testing suite for CyborgDB, a high-performance vector search database service. This suite evaluates the performance, reliability, and scalability of the service under various load conditions and with different testing scenarios.

## Overview

The test suite consists of:

1. **Standard Load Tests** - General performance testing of all API endpoints
2. **Advanced Load Tests** - Comprehensive testing with various scenarios and load patterns
3. **Query-Specific Tests** - Focused tests on query performance under high load
4. **Training Benchmark Tests** - Specialized tests focusing on index training performance
5. **Concurrent Upsert Tests** - Specialized tests for concurrent vector insertion performance
6. **Dataset-Based Tests** - Tests using real or synthetic vector datasets
7. **Run Scripts** - Utilities to execute the tests with various parameters

## Prerequisites

- [k6](https://k6.io/docs/getting-started/installation/) - Load testing tool
- Python 3 with numpy, tqdm, and h5py (for dataset processing)
- A running instance of CyborgDB service

## Test Files

| File | Description |
|------|-------------|
| `k6-load-tests.js` | Main load testing script with multiple test modes |
| `k6-specific-scenarios.js` | Vector query performance tests with spike scenarios |
| `k6-training-benchmark.js` | Specialized script for benchmarking index training performance |
| `k6-concurrent-upsert-test.js` | Concurrent vector upsert performance testing |
| `run-load-tests.sh` | Main script to run tests with configurable parameters |
| `run-training-benchmark.sh` | Script for running training-specific performance tests |
| `hdf5_to_json_converter.py` | Utility to convert HDF5 vector files to JSON |

## Test Modes

### Standard Load Tests (`k6-load-tests.js`)

| Mode | Description | Vectors | Queries | Filters |
|------|-------------|---------|---------|---------|
| **standard** | Basic test with balanced load | 5,000 | 5 | No |
| **advanced** | Comprehensive test with higher load | 10,000 | 8 | Yes |
| **query_intense** | Heavy query load | 7,500 | 15 | Yes |
| **metadata_filter** | Focus on metadata filtering | 8,000 | 10 | Complex |

### Concurrent Upsert Tests (`k6-concurrent-upsert-test.js`)

| Mode | Description | Vectors | Iterations | Focus |
|------|-------------|---------|------------|-------|
| **standard** | Basic concurrent upsert test | 20,000 | 10 | Balanced load |
| **advanced** | Higher concurrent load | 30,000 | 15 | Increased concurrency |
| **stress** | Maximum stress test | 50,000 | 20 | Performance limits |

## Basic Usage

### Quick Start

```bash
# Run a basic test with default parameters
./run-load-tests.sh

# Run an advanced test with more users and longer duration
./run-load-tests.sh --mode advanced --vus 20 --duration 2m

# Run a training-specific benchmark
./run-training-benchmark.sh --api-key YOUR_API_KEY

# Run concurrent upsert test
./run-load-tests.sh --concurrent-upsert --api-key YOUR_API_KEY

# Run high-rate concurrent upsert test
./run-load-tests.sh --concurrent-upsert --target-upserts 120 --batch-size 200 -v 10 -d 1m
```

### Configuration Options

The test scripts support various configuration options:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--url` | Base URL of the CyborgDB service | http://localhost:8000 |
| `--api-key` | API Key for authentication | your-default-api-key |
| `--prefix` | API prefix | /v1 |
| `--vus` | Maximum number of virtual users | 10 |
| `--duration` | Test duration | 1m |
| `--mode` | Test mode | standard |
| `--output` | Output format (json, csv, html, grafana, dashboard) | json |
| `--script` | Test script to run | k6-load-tests.js |
| `--concurrent-upsert` | Use concurrent upsert test | false |

### Concurrent Upsert Options

When using `--concurrent-upsert`, additional options are available:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--target-upserts` | Target upserts per minute | 60 |
| `--batch-size` | Vectors per upsert batch | 100 |
| `--ramp-up` | Ramp up duration | 2s |
| `--ramp-down` | Ramp down duration | 30s |

### Training Benchmark Options

The training benchmark supports additional options:

| Parameter | Description | Default |
|-----------|-------------|---------|
| `--vectors` | Number of vectors per index | 1000 |
| `--batch-size` | Vectors per batch when upserting | 100 |
| `--n-lists` | Number of clusters/lists for IVF index | 4 |
| `--index-count` | Number of indexes to create per VU | 3 |
| `--dimension` | Vector dimension | 384 |

### Examples

```bash
# Run a query-focused test with HTML output
./run-load-tests.sh --mode query_intense --output html

# Run the query-specific test with spike scenarios
./run-load-tests.sh --script k6-specific-scenarios.js --vus 30

# Run a training benchmark with 5000 vectors per index
./run-training-benchmark.sh --api-key YOUR_API_KEY --vectors 5000

# Run with custom API endpoint
./run-load-tests.sh --url https://your-cyborgdb-instance.com --api-key YOUR_API_KEY

# Basic concurrent upsert test
./run-load-tests.sh --concurrent-upsert --api-key YOUR_API_KEY

# High-throughput concurrent upsert test
./run-load-tests.sh --concurrent-upsert --api-key YOUR_API_KEY \
  --target-upserts 240 --batch-size 500 --vus 20 --duration 2m

# Stress test with extended ramp periods
./run-load-tests.sh --concurrent-upsert --api-key YOUR_API_KEY \
  --mode stress --ramp-up 30s --ramp-down 60s --vus 25 --duration 5m
```

## Dataset-Based Testing

For more realistic testing with actual vector datasets:

**Note:** Dataset-based testing is only available for standard load tests. Concurrent upsert tests use synthetic vector generation for optimal performance testing.

```bash
# Using a pre-defined dataset
./run-load-tests.sh --dataset-name wiki-all-1m --dataset-limit 50000

# Using your own JSON dataset
./run-load-tests.sh --dataset /path/to/your/vectors.json

# Converting and using HDF5 files
./run-load-tests.sh --hdf5 /path/to/vectors.hdf5 --dataset-limit 100000
```

### Dataset Options

The dataset-based tests support several data sources:

| Dataset Name | Description |
|--------------|-------------|
| **wikipedia** | Wikipedia article embeddings |
| **sift-128** | SIFT 128-dimensional feature vectors |
| **glove-angular** | GloVe word embeddings |
| **wiki-all-1m** | Wikipedia 1M vectors (768-dim) |
| **wiki-all-10m** | Wikipedia 10M vectors (768-dim) |

### Dataset Test Configuration

Additional options for dataset-based testing:

| Parameter | Description |
|-----------|-------------|
| `--dataset-name` | Name of the dataset to download |
| `--dataset-limit` | Number of items to use from dataset |
| `--dataset` | Path to an existing JSON dataset file |
| `--hdf5` | Path to an HDF5 dataset file to convert |
| `--lite` | Use lite mode (less memory intensive) |

## Manual Execution with k6

You can also run the tests directly with k6:

```bash
# Set environment variables for standard load tests
export BASE_URL=http://localhost:8000
export API_KEY=your-api-key
export API_PREFIX=/v1
export TEST_MODE=standard

# Run the main load tests
k6 run k6-load-tests.js

# Run specific scenarios
k6 run k6-specific-scenarios.js

# Run training benchmark
k6 run --vus 1 --iterations 3 k6-training-benchmark.js

# Run concurrent upsert test
export VU_MAX=10
export DURATION=30s
export TARGET_UPSERTS_PER_MINUTE=120
export BATCH_SIZE=200
k6 run k6-concurrent-upsert-test.js
```

## Visualizing Test Results

There are several ways to visualize the results from your load tests:

### 1. Built-in k6 Dashboard

The simplest option is to use k6's built-in web dashboard:

```bash
# Run with built-in dashboard
./run-load-tests.sh --output dashboard

# Or directly with k6
k6 run --out dashboard k6-load-tests.js
```

This opens a real-time dashboard in your browser showing metrics as the test runs.

### 2. Grafana + InfluxDB Visualization

For more advanced visualization, you can use Grafana with InfluxDB:

#### Setup Options:

**A. Using Docker (if installed):**
```bash
# Create a docker-compose.yml file:
cat > docker-compose.yml << 'EOL'
version: '3'
services:
  influxdb:
    image: influxdb:1.8
    ports:
      - "8086:8086"
    environment:
      - INFLUXDB_DB=k6
      - INFLUXDB_ADMIN_USER=admin
      - INFLUXDB_ADMIN_PASSWORD=admin
    volumes:
      - influxdb-data:/var/lib/influxdb
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      - GF_AUTH_ANONYMOUS_ENABLED=true
      - GF_AUTH_ANONYMOUS_ORG_ROLE=Admin
    volumes:
      - grafana-data:/var/lib/grafana
    networks:
      - monitoring
    depends_on:
      - influxdb

networks:
  monitoring:

volumes:
  influxdb-data:
  grafana-data:
EOL

# Start the services
docker-compose up -d
```

**B. Direct Installation:**

- **InfluxDB:**
  ```bash
  # On Ubuntu/Debian
  sudo apt-get update
  sudo apt-get install influxdb
  sudo systemctl start influxdb
  
  # On macOS
  brew install influxdb
  brew services start influxdb
  ```

- **Grafana:**
  ```bash
  # On Ubuntu/Debian
  sudo apt-get install -y apt-transport-https software-properties-common
  wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
  echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee -a /etc/apt/sources.list.d/grafana.list
  sudo apt-get update
  sudo apt-get install grafana
  sudo systemctl start grafana-server
  
  # On macOS
  brew install grafana
  brew services start grafana
  ```

#### Running Tests with Grafana Output:

```bash
# Run tests with Grafana output
./run-load-tests.sh --output grafana

# Run training benchmark with Grafana output
./run-training-benchmark.sh --api-key YOUR_API_KEY --output grafana

# Specify custom InfluxDB URL if needed
./run-load-tests.sh --output grafana --influxdb http://localhost:8086/k6
```

### 3. HTML Reports

For static HTML reports:

```bash
# Run with HTML output
./run-load-tests.sh --output html
```

This generates an HTML report with test results that can be viewed in any browser.

### 4. JSON/CSV Output for Custom Processing

```bash
# JSON output
./run-load-tests.sh --output json

# CSV output
./run-load-tests.sh --output csv
```

These formats can be imported into data analysis tools like Python (pandas) or Excel.

## Test Details

### Standard Load Tests

The standard test exercises all core API functionality:

1. **Health Check** - Verifies service availability
2. **Index Operations** - Tests creating, listing, describing, and deleting indexes
3. **Vector Operations** - Tests vector upsert, query, get, and delete operations

### Advanced Load Tests

The advanced test includes everything from the standard test plus:

1. **Rich Metadata** - Tests using complex metadata and filters
2. **Varied Load Patterns** - Tests different load profiles and request patterns
3. **Error Handling** - Tests how the system responds to invalid inputs

### Query-Specific Tests

The query-specific tests focus exclusively on query performance:

1. **Sustained Query Load** - Constant load of vector queries
2. **Query Spikes** - Simulates sudden spikes in query traffic

### Training Benchmark Tests

The training benchmark focuses specifically on index training performance:

1. **Multiple Indexes** - Creates and trains multiple indexes sequentially
2. **Configurable Vectors** - Tests with different vector counts and dimensions
3. **Cluster Variations** - Tests with different n_lists (cluster) configurations
4. **Performance Metrics** - Detailed metrics on training success rate and duration

### Concurrent Upsert Tests

The concurrent upsert test focuses specifically on concurrent vector insertion performance:

1. **Rate-Limited Upserts** - Controls upsert rate to test sustained throughput
2. **Concurrent Writers** - Multiple virtual users inserting vectors simultaneously
3. **Batch Processing** - Configurable batch sizes for optimal performance testing
4. **Real-time Verification** - Validates vector counts during and after test execution
5. **Synthetic Data Generation** - Creates realistic test vectors without external datasets

### Dataset-Based Tests

Dataset-based tests provide more realistic testing scenarios:

1. **Real-World Vectors** - Uses actual vector embeddings from various sources
2. **Scalability Testing** - Tests performance with large datasets
3. **Diverse Content** - Tests with diverse text content and vector patterns

## Test Metrics

The tests collect and report various performance metrics:

| Metric | Description |
|--------|-------------|
| **HTTP Request Duration** | Response time for API requests |
| **Error Rate** | Percentage of failed requests |
| **Throughput** | Requests per second |
| **Vector Operation Times** | Duration of vector operations |
| **Training Success Rate** | Success rate of index training operations |
| **Training Duration** | Time to train indexes |
| **Vector Query Duration** | Time to execute vector similarity queries |
| **Index Creation Duration** | Time to create new indexes |
| **Metadata Query Duration** | Performance of metadata-filtered queries |
| **Concurrent Upsert Rate** | Vectors upserted per minute under concurrent load |
| **Upsert Failure Rate** | Percentage of failed upsert operations |
| **Active Upserts Gauge** | Number of concurrent upsert operations |

## Example Output

### General Load Test Output
```
Running load tests with configuration:
  Base URL: http://localhost:8000
  API Prefix: /v1
  Virtual Users: 10
  Duration: 1m
  Test Mode: standard

Starting load test...
data_received.............: 1.2 MB  20 kB/s
data_sent.................: 268 kB  4.5 kB/s
http_req_blocked..........: avg=1.85ms   min=1µs      med=4µs      max=158.21ms p(90)=8µs      p(95)=10µs     
http_req_connecting.......: avg=910.8µs  min=0s       med=0s       max=77.98ms  p(90)=0s       p(95)=0s       
http_req_duration.........: avg=85.09ms  min=1.11ms   med=6.13ms   max=2.66s    p(90)=135.46ms p(95)=447.95ms 
http_req_failed...........: 0.00%   ✓ 0        ✗ 1022  
http_req_receiving........: avg=188.98µs min=33µs     med=105µs    max=12.53ms  p(90)=229µs    p(95)=457.74µs 
http_req_sending..........: avg=102.22µs min=16µs     med=54µs     max=7.36ms   p(90)=131µs    p(95)=267µs    
http_req_waiting..........: avg=84.8ms   min=925µs    med=5.95ms   max=2.66s    p(90)=134.71ms p(95)=447.5ms  
http_reqs.................: 1022    17.025765/s
success_rate..............: 100%    ✓ 1022     ✗ 0
training_success_rate.....: 100%    ✓ 60       ✗ 0
index_creation_duration...: avg=245.32ms min=150.23ms med=210.45ms max=450.67ms
vector_upsert_duration....: avg=42.16ms  min=25.78ms  med=38.92ms  max=120.34ms
vector_query_duration.....: avg=34.98ms  min=12.56ms  med=30.45ms  max=85.23ms
```

### Training Benchmark Output
```
CyborgDB Training Benchmark
==========================
Base URL: http://localhost:8000
API Prefix: /v1
Vectors per index: 1000
Batch size: 100
N-lists (clusters): 4
Index count per VU: 3
Vector dimension: 384
Virtual users: 1

Starting training benchmark...
vus........................: 1       1/s
iterations.................: 3       0.5/s
success_rate...............: 100%    ✓ 18       ✗ 0
training_success_rate......: 100%    ✓ 3        ✗ 0
trainingDuration...........: avg=389.24ms min=289.43ms med=375.97ms max=502.33ms p(90)=502.33ms p(95)=502.33ms

Training Metrics Summary:
========================
Success Rate: training_success_rate: 100.00% ✓ 3 ✗ 0
Duration: trainingDuration: avg=389.24ms min=289.43ms med=375.97ms max=502.33ms p(90)=502.33ms p(95)=502.33ms
```

### Concurrent Upsert Test Output
```
================================================================================
CONCURRENT UPSERT TEST SUMMARY
================================================================================
📊 Test Statistics:
   • Total upsert calls: 150
   • Total vectors upserted: 15000
   • Setup vectors: 2000
   • Expected total in index: 17000

🔍 Verification: ✅ Backend count matches expected: 17000 vectors (Δ=0)

📈 Performance:
   • Overall success rate: 100.00%
   • Upsert failure rate: 0.00%
   • Average upsert duration: 245.32ms
   • P95 upsert duration: 1205.67ms
================================================================================
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| **API Key Issues** | Ensure the API key matches what's configured in your CyborgDB service |
| **Connection Errors** | Verify the BASE_URL is correct and the service is running |
| **High Error Rates** | Check for network issues or service overload |
| **Slow Response Times** | Consider reducing the load or optimizing your service configuration |
| **Training Failures** | Check vector count vs. n_lists ratio; ensure you have more vectors than clusters |
| **Dataset Issues** | For dataset-based tests, ensure Python dependencies are installed |
| **HuggingFace Rate Limiting** | If you see 429 errors, consider pre-downloading embedding models |
| **Out of Memory** | Try using the `--lite` option with dataset tests or reduce dataset size |
| **Grafana/InfluxDB Connection** | Check that both services are running and accessible |
| **Docker Compose Not Found** | Install Docker Compose or use alternative visualization options |
| **Concurrent Upsert Failures** | Reduce `--target-upserts` or `--batch-size` to find sustainable rate |
| **Vector Count Mismatches** | Check for network timeouts or partial failures during concurrent operations |

## Advanced Configuration

### Test Thresholds

The tests include built-in thresholds for success criteria:

- 95% of requests must complete below 2s (10s for training operations)
- At least 80% success rate overall
- Training operations success rate above 70%

### Load Test Patterns

The test scripts use the following load patterns:

1. **Ramping Load**: Gradually increases the number of virtual users
2. **Constant Load**: Maintains a steady number of virtual users
3. **Spike Testing**: Sudden increases in load to test system resilience
4. **Per-VU Iterations**: Used in training benchmark to run specific number of iterations per VU

## Contributing

To extend or modify these tests:

1. Add new test modes in `k6-load-tests.js` by extending the `testScenarios` object
2. Create new scenario-specific test scripts for special cases
3. Add support for new datasets in `run-load-tests.sh`
4. Modify training parameters in `k6-training-benchmark.js` for specialized training tests
5. Extend concurrent upsert tests in `k6-concurrent-upsert-test.js` for different concurrency patterns
6. Add new metrics and thresholds for specific performance testing needs

## QA Integration

This load testing suite is designed to integrate with existing QA processes:

### Integration with Unit and Integration Tests

- **Unit Tests**: Run unit tests first to ensure individual components work
- **Integration Tests**: Run integration tests to verify API endpoints work correctly
- **Load Tests**: Run these load tests to verify performance under stress
- **Concurrent Tests**: Use concurrent upsert tests to verify system behavior under high concurrent load

### CI/CD Integration

The scripts can be integrated into CI/CD pipelines:

```bash
# Example CI/CD steps
./run-load-tests.sh --api-key $API_KEY --mode standard --duration 2m --output json

# For concurrent write performance validation
./run-load-tests.sh --concurrent-upsert --api-key $API_KEY --target-upserts 60 --duration 1m --output json

# For training performance validation
./run-training-benchmark.sh --api-key $API_KEY --vectors 1000 --index-count 2
```

### Test Data Management

- Use the provided dataset conversion tools to create consistent test data
- Store converted datasets in your test environment for repeatable tests
- Use the `--lite` mode for faster CI/CD execution
- Concurrent upsert tests generate synthetic data automatically for consistent performance testing

### Performance Regression Testing

- Establish baseline performance metrics using these tests
- Run tests regularly to detect performance regressions
- Compare results over time to track performance trends
- Use concurrent upsert tests to validate write performance under different load patterns