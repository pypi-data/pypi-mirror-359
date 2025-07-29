#!/bin/bash
# Run the training benchmark script

# Default values
BASE_URL="http://localhost:8000"
API_KEY="your-default-api-key"
API_PREFIX="/v1"
VECTOR_COUNT=1000
BATCH_SIZE=100
N_LISTS=4
INDEX_COUNT=3
DIMENSION=384
VUS=1

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -h|--help)
      echo "Usage: ./run-training-benchmark.sh [options]"
      echo ""
      echo "Options:"
      echo "  -k, --api-key KEY            API Key for authentication"
      echo "  -u, --url URL                Base URL of the service (default: http://localhost:8000)"
      echo "  -p, --prefix PREFIX          API prefix (default: /v1)"
      echo "  -v, --vectors NUM            Number of vectors per index (default: 1000)"
      echo "  -b, --batch-size NUM         Vectors per batch (default: 100)"
      echo "  -l, --n-lists NUM            Number of clusters/lists (default: 4)"
      echo "  -i, --index-count NUM        Number of indexes to create per VU (default: 3)"
      echo "  -d, --dimension NUM          Vector dimension (default: 384)"
      echo "  --vus NUM                    Number of virtual users (default: 1)"
      exit 0
      ;;
    -k|--api-key)
      API_KEY="$2"
      shift 2
      ;;
    -u|--url)
      BASE_URL="$2"
      shift 2
      ;;
    -p|--prefix)
      API_PREFIX="$2"
      shift 2
      ;;
    -v|--vectors)
      VECTOR_COUNT="$2"
      shift 2
      ;;
    -b|--batch-size)
      BATCH_SIZE="$2"
      shift 2
      ;;
    -l|--n-lists)
      N_LISTS="$2"
      shift 2
      ;;
    -i|--index-count)
      INDEX_COUNT="$2"
      shift 2
      ;;
    -d|--dimension)
      DIMENSION="$2"
      shift 2
      ;;
    --vus)
      VUS="$2"
      shift 2
      ;;
    *)
      echo "Unknown option: $1"
      echo "Use -h or --help for usage information"
      exit 1
      ;;
  esac
done

# Create logs directory
mkdir -p logs
LOG_FILE="logs/training_benchmark_$(date +%Y%m%d_%H%M%S).log"

echo "CyborgDB Training Benchmark"
echo "=========================="
echo "Base URL: $BASE_URL"
echo "API Prefix: $API_PREFIX"
echo "Vectors per index: $VECTOR_COUNT"
echo "Batch size: $BATCH_SIZE"
echo "N-lists (clusters): $N_LISTS"
echo "Index count per VU: $INDEX_COUNT"
echo "Vector dimension: $DIMENSION"
echo "Virtual users: $VUS"
echo "Log file: $LOG_FILE"
echo ""

# Export environment variables for the k6 script
export BASE_URL
export API_KEY
export API_PREFIX
export VECTOR_COUNT
export BATCH_SIZE
export N_LISTS
export INDEX_COUNT
export DIMENSION

# Run the training benchmark
echo "Starting training benchmark..."
k6 run --vus $VUS --iterations $((VUS * INDEX_COUNT)) k6-training-benchmark.js | tee -a "$LOG_FILE"

echo ""
echo "Training benchmark completed."
echo "Check $LOG_FILE for details."

# Extract training metrics from the log file
echo ""
echo "Training Metrics Summary:"
echo "========================"
if grep -q "training_success_rate" "$LOG_FILE"; then
  TRAINING_RATE=$(grep "training_success_rate" "$LOG_FILE" | head -1)
  TRAINING_DURATION=$(grep "trainingDuration" "$LOG_FILE" | head -1)
  echo "Success Rate: $TRAINING_RATE"
  echo "Duration: $TRAINING_DURATION"
else
  echo "No training metrics found in log. Check for errors."
fi