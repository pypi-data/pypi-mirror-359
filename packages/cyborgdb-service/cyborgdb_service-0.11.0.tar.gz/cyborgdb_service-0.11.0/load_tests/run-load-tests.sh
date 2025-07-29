#!/usr/bin/env bash
# Load Testing Script for CyborgDB Service

# Default values
BASE_URL="http://localhost:8000"
API_KEY="your-default-api-key"
API_PREFIX="/v1"
VU_MAX=10
DURATION="1m"
TEST_MODE="standard"
OUTPUT_FORMAT="json"
INFLUXDB_URL="http://localhost:8086/k6"
GRAFANA_URL="http://localhost:3000"
DEFAULT_REDIS_CONNECTION_STRING="host:localhost,port:6379,db:0"
DEFAULT_POSTGRES_CONNECTION_STRING="host=localhost port=5432 dbname=cyborg user=postgres password=''"

# Dataset-related defaults
DATASET_LIMIT=50000
DATASET_PATH=""
HDF5_PATH=""
LITE_MODE=false

# Concurrent upsert test defaults
USE_CONCURRENT_UPSERT=false
TARGET_UPSERTS_PER_MINUTE=60
BATCH_SIZE=100
RAMP_UP="2s"
RAMP_DOWN="30s"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to get dataset URL by name
get_dataset_url() {
  local dataset_name="$1"
  case "$dataset_name" in
    "sift-128")
      echo "http://ann-benchmarks.com/sift-128-euclidean.hdf5"
      ;;
    "glove-angular")
      echo "http://ann-benchmarks.com/glove-25-angular.hdf5"
      ;;
    "wiki-all-1m")
      echo "https://wiki-all.s3.us-east-1.amazonaws.com/wiki_all_1M.hdf5"
      ;;
    "wiki-all-10m")
      echo "https://wiki-all.s3.us-east-1.amazonaws.com/wiki_all_10M.hdf5"
      ;;
    *)
      echo ""
      ;;
  esac
}

# List of valid dataset names
VALID_DATASETS="sift-128 glove-angular wiki-all-1m wiki-all-10m"

# Function to display usage instructions
show_help() {
  echo "CyborgDB Load Tests"
  echo ""
  echo "Usage: ./run-load-tests.sh [options]"
  echo ""
  echo "Basic Options:"
  echo "  -h, --help                   Show this help message"
  echo "  -u, --url URL                Base URL of the service (default: http://localhost:8000)"
  echo "  -k, --api-key KEY            API Key for authentication"
  echo "  -p, --prefix PREFIX          API prefix (default: /v1)"
  echo "  -v, --vus NUM                Maximum number of virtual users (default: 10)"
  echo "  -d, --duration TIME          Test duration (default: 1m)"
  echo "  -m, --mode MODE              Test mode: standard, advanced, query_intense, metadata_filter"
  echo "  -o, --output FORMAT          Output format (json, csv, html, grafana, dashboard)"
  echo "  -s, --script SCRIPT          Test script to run (default: k6-load-tests.js)"
  echo "  --concurrent-upsert          Use concurrent upsert test script"
  echo "  --redis                      Use Redis for index, config, and items storage"
  echo "  --postgres                   Use PostgreSQL for index, config, and items storage"
  echo ""
  echo "Concurrent Upsert Options (when using --concurrent-upsert):"
  echo "  --target-upserts NUM         Target upserts per minute (default: 60)"
  echo "  --batch-size NUM             Vectors per upsert batch (default: 100)"
  echo "  --ramp-up TIME               Ramp up duration (default: 2s)"
  echo "  --ramp-down TIME             Ramp down duration (default: 30s)"
  echo ""
  echo "Dataset Options:"
  echo "  -n, --dataset-name NAME      Choose dataset: sift-128, glove-angular, wiki-all-1m, wiki-all-10m"
  echo "  -c, --dataset-limit NUM      Number of vectors to use from dataset (default: 50000)"
  echo "  -D, --dataset PATH           Path to existing JSON dataset file"
  echo "  -H, --hdf5 PATH              Path to existing HDF5 file to convert"
  echo "  --lite                       Use lite mode (reduced dataset size)"
  echo ""
  echo "Test Modes:"
  echo "  standard         - Balanced test (1K vectors, basic training)"
  echo "  advanced         - Comprehensive test (2K vectors, metadata filters)"
  echo "  query_intense    - Heavy query load (1.5K vectors, 10 queries per VU)"
  echo "  metadata_filter  - Focus on complex metadata filtering"
  echo "  stress           - High stress test (for concurrent upsert only)"
  echo ""
  echo "Examples:"
  echo "  # Basic test"
  echo "  ./run-load-tests.sh -k your-api-key -v 5 -d 2m"
  echo ""
  echo "  # Advanced test"
  echo "  ./run-load-tests.sh -k your-api-key -m advanced -v 10 -d 5m"
  echo ""
  echo "  # Query focused test"
  echo "  ./run-load-tests.sh -k your-api-key -m query_intense -v 8 -d 3m"
  echo ""
  echo "  # Concurrent upsert test"
  echo "  ./run-load-tests.sh --concurrent-upsert -k your-api-key -v 5 -d 30s"
  echo ""
  echo "  # High-rate concurrent upsert test"
  echo "  ./run-load-tests.sh --concurrent-upsert -k your-api-key --target-upserts 120 --batch-size 200 -v 10 -d 1m"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  key="$1"
  case $key in
    -h|--help)
      show_help
      exit 0
      ;;
    -u|--url)
      BASE_URL="$2"
      shift 2
      ;;
    -k|--api-key)
      API_KEY="$2"
      shift 2
      ;;
    -p|--prefix)
      API_PREFIX="$2"
      shift 2
      ;;
    -v|--vus)
      VU_MAX="$2"
      shift 2
      ;;
    -d|--duration)
      DURATION="$2"
      shift 2
      ;;
    -m|--mode)
      TEST_MODE="$2"
      shift 2
      ;;
    -o|--output)
      OUTPUT_FORMAT="$2"
      shift 2
      ;;
    -s|--script)
      TEST_SCRIPT="$2"
      shift 2
      ;;
    --concurrent-upsert)
      USE_CONCURRENT_UPSERT=true
      shift
      ;;
    --target-upserts)
      TARGET_UPSERTS_PER_MINUTE="$2"
      shift 2
      ;;
    --batch-size)
      BATCH_SIZE="$2"
      shift 2
      ;;
    --ramp-up)
      RAMP_UP="$2"
      shift 2
      ;;
    --ramp-down)
      RAMP_DOWN="$2"
      shift 2
      ;;
    -n|--dataset-name)
      DATASET_NAME="$2"
      shift 2
      ;;
    -c|--dataset-limit)
      DATASET_LIMIT="$2"
      shift 2
      ;;
    -D|--dataset)
      DATASET_PATH="$2"
      shift 2
      ;;
    -H|--hdf5)
      HDF5_PATH="$2"
      shift 2
      ;;
    --lite)
      LITE_MODE=true
      shift
      ;;
    --real-embeddings)
      USE_REAL_EMBEDDINGS=true
      shift
      ;;
    --embedding-model)
      EMBEDDING_MODEL="$2"
      USE_REAL_EMBEDDINGS=true
      shift 2
      ;;
    --influxdb)
      INFLUXDB_URL="$2"
      shift 2
      ;;
    --grafana)
      GRAFANA_URL="$2"
      shift 2
      ;;
    --redis)
      export INDEX_LOCATION="redis"
      export CONFIG_LOCATION="redis"
      export ITEMS_LOCATION="redis"
      export INDEX_CONNECTION_STRING="${REDIS_CONNECTION_STRING:-$DEFAULT_REDIS_CONNECTION_STRING}"
      export CONFIG_CONNECTION_STRING="${REDIS_CONNECTION_STRING:-$DEFAULT_REDIS_CONNECTION_STRING}"
      export ITEMS_CONNECTION_STRING="${REDIS_CONNECTION_STRING:-$DEFAULT_REDIS_CONNECTION_STRING}"
      shift
      ;;
    --postgres)
      export INDEX_LOCATION="postgres"
      export CONFIG_LOCATION="postgres"
      export ITEMS_LOCATION="postgres"
      export INDEX_CONNECTION_STRING="${POSTGRES_CONNECTION_STRING:-$DEFAULT_POSTGRES_CONNECTION_STRING}"
      export CONFIG_CONNECTION_STRING="${POSTGRES_CONNECTION_STRING:-$DEFAULT_POSTGRES_CONNECTION_STRING}"
      export ITEMS_CONNECTION_STRING="${POSTGRES_CONNECTION_STRING:-$DEFAULT_POSTGRES_CONNECTION_STRING}"
      shift
      ;;
    *)
      echo "Unknown option: $1"
      show_help
      exit 1
      ;;
  esac
done

# Pre-test validation and setup
echo "Load Testing Script for CyborgDB Service"
echo "========================================"

# Set default test script if not provided
if [ -z "$TEST_SCRIPT" ]; then
  if [ "$USE_CONCURRENT_UPSERT" = true ]; then
    TEST_SCRIPT="k6-concurrent-upsert-test.js"
  else
    TEST_SCRIPT="k6-load-tests.js"
  fi
fi

# Validate test mode
if [[ "$USE_CONCURRENT_UPSERT" = false && "$TEST_SCRIPT" == "k6-load-tests.js" && ! "$TEST_MODE" =~ ^(standard|advanced|query_intense|metadata_filter)$ ]]; then
  log_error "Invalid test mode: $TEST_MODE"
  echo "Valid options are: standard, advanced, query_intense, metadata_filter"
  exit 1
fi

# For concurrent upsert tests, allow additional test modes
if [[ "$USE_CONCURRENT_UPSERT" = true && ! "$TEST_MODE" =~ ^(standard|advanced|stress)$ ]]; then
  log_error "Invalid test mode for concurrent upsert: $TEST_MODE"
  echo "Valid options for concurrent upsert are: standard, advanced, stress"
  exit 1
fi

# API key validation
if [[ "$API_KEY" == "your-default-api-key" ]]; then
  log_warning "Using default API key. For production testing, use a real API key."
  read -p "Continue with default key? (y/n): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Ensure K6 is installed
if ! command -v k6 &> /dev/null; then
  log_error "k6 is not installed. Please install k6 first."
  echo "Visit https://k6.io/docs/getting-started/installation/ for installation instructions."
  exit 1
fi

# Python and package checking
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
  log_error "Python 3 is required for dataset processing and embedding models."
  exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
  PYTHON_CMD="python"
fi

log_success "Python found: $($PYTHON_CMD --version)"

# Check required Python packages
log_info "Checking required Python packages..."
required_packages=("tqdm" "numpy" "h5py" "sentence_transformers")
missing_packages=()

for package in "${required_packages[@]}"; do
  if ! $PYTHON_CMD -c "import $package" &> /dev/null; then
    missing_packages+=("$package")
  fi
done

if [ ${#missing_packages[@]} -ne 0 ]; then
  log_error "Missing required packages: ${missing_packages[*]}"
  echo "Install with: pip install ${missing_packages[*]}"
  
  read -p "Install missing packages now? (y/n): " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    log_info "Installing missing packages..."
    pip install "${missing_packages[@]}"
    if [[ $? -eq 0 ]]; then
      log_success "Packages installed successfully"
    else
      log_error "Failed to install packages"
      exit 1
    fi
  else
    log_error "Cannot proceed without required packages"
    exit 1
  fi
else
  log_success "All required Python packages are installed"
fi

# Embedding model pre-download (only if using real embeddings)
if [[ "$TEST_SCRIPT" == "k6-load-tests.js" && "$USE_REAL_EMBEDDINGS" == "true" ]]; then
  log_info "Real embeddings enabled - pre-downloading embedding model..."
  
  # Check HuggingFace token
  if [[ -n "$HUGGINGFACE_HUB_TOKEN" ]]; then
    log_success "HuggingFace token is set"
  else
    log_warning "HUGGINGFACE_HUB_TOKEN not set - may encounter rate limiting during tests"
    echo "  Set with: export HUGGINGFACE_HUB_TOKEN=your_token_here"
  fi
  
  # Pre-download with error handling
  $PYTHON_CMD -c "
import sys
try:
    from sentence_transformers import SentenceTransformer
    print('[INFO] Downloading/verifying $EMBEDDING_MODEL model...')
    model = SentenceTransformer('$EMBEDDING_MODEL')
    
    # Test the model
    test_embedding = model.encode('Test sentence for verification.')
    print(f'[SUCCESS] Model ready! Embedding dimension: {len(test_embedding)}')
    print(f'[INFO] Model max sequence length: {model.max_seq_length}')
except Exception as e:
    print(f'[ERROR] Failed to download embedding model: {e}')
    print('[WARNING] This may cause issues during load tests')
    sys.exit(1)
  "
  
  if [[ $? -eq 0 ]]; then
    log_success "Embedding model pre-downloaded successfully"
  else
    log_warning "Failed to pre-download embedding model"
    
    read -p "Continue anyway? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      exit 1
    fi
  fi
else
  log_info "Using pre-computed vectors - no embedding model download needed"
fi

# Dataset processing logic - Skip for concurrent upsert tests
if [[ "$USE_CONCURRENT_UPSERT" = true ]]; then
  log_info "Concurrent upsert test selected - skipping dataset processing"
  log_info "This test generates synthetic vectors during execution"
else
  # Enhanced dataset processing with interactive selection
  echo ""
  log_info "Setting up dataset..."

# Create datasets directory
mkdir -p datasets

# Dataset processing logic
USING_DATASET=true
ORIGINAL_HDF5_PATH=""

# Interactive dataset selection if not specified
if [[ -z "$DATASET_PATH" && -z "$HDF5_PATH" && -z "$DATASET_NAME" ]]; then
  
  log_info "No dataset specified via command line - showing interactive selection"
  
  # Show existing datasets
  if [[ -d "datasets" ]] && [[ -n "$(ls -A datasets/*.json 2>/dev/null)" ]]; then
    existing_datasets=$(ls datasets/*.json 2>/dev/null)
    echo ""
    log_info "Found existing datasets in datasets/ folder:"
    for dataset in $existing_datasets; do
      dataset_name=$(basename "$dataset" .json)
      dataset_size=$(du -h "$dataset" 2>/dev/null | cut -f1)
      echo "  - $dataset_name (${dataset_size:-"unknown size"})"
    done
    echo ""
    log_info "You can use an existing dataset or download a new one"
  fi
  
  # Interactive menu for dataset selection
  echo ""
  log_info "Choose a dataset for load testing:"
  echo ""
  echo "1) wiki-all-1m     - Wikipedia embeddings (1M vectors, 768-dim) [RECOMMENDED]"
  echo "2) sift-128        - SIFT visual features (1M vectors, 128-dim)"  
  echo "3) glove-angular   - GloVe word embeddings (1.2M vectors, 25-dim)"
  echo "4) wiki-all-10m    - Large Wikipedia dataset (10M vectors, 768-dim)"
  echo ""
  read -p "Select dataset (1-4) or press Enter for default [1]: " -r dataset_choice
  
  case "${dataset_choice:-1}" in
    1)
      DATASET_NAME="wiki-all-1m"
      DEFAULT_LIMIT=50000
      log_info "Selected: Wikipedia 1M dataset (recommended for general testing)"
      ;;
    2) 
      DATASET_NAME="sift-128"
      DEFAULT_LIMIT=75000
      log_info "Selected: SIFT 128-dimensional dataset (good for computer vision workloads)"
      ;;
    3)
      DATASET_NAME="glove-angular"
      DEFAULT_LIMIT=60000
      log_info "Selected: GloVe word embeddings (good for NLP workloads)"
      ;;
    4)
      DATASET_NAME="wiki-all-10m"
      DEFAULT_LIMIT=100000
      log_info "Selected: Large Wikipedia dataset (intensive testing)"
      log_warning "This is a large dataset - will take longer to download and process"
      ;;
    *)
      DATASET_NAME="wiki-all-1m"
      DEFAULT_LIMIT=50000
      log_info "Using default: Wikipedia 1M dataset"
      ;;
  esac
  
  # Ask about dataset limit
  echo ""
  read -p "How many vectors to use from dataset? Press Enter for default [${DEFAULT_LIMIT}]: " -r limit_input
  
  if [[ -z "$limit_input" ]]; then
    DATASET_LIMIT=$DEFAULT_LIMIT
    log_info "Using default: $DATASET_LIMIT vectors"
  else
    DATASET_LIMIT=$limit_input
    log_info "Using custom size: $DATASET_LIMIT vectors"
  fi
  
  if [[ $DATASET_LIMIT -gt 200000 ]]; then
    log_warning "Large dataset size selected - this will require significant memory and time"
    read -p "Continue with $DATASET_LIMIT vectors? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
      DATASET_LIMIT=$DEFAULT_LIMIT
      log_info "Reduced to default: $DATASET_LIMIT vectors"
    fi
  fi
  
  # Check for existing converted dataset
  potential_existing="datasets/${DATASET_NAME}_${DATASET_LIMIT}.json"
  if [[ -f "$potential_existing" ]]; then
    dataset_size=$(du -h "$potential_existing" 2>/dev/null | cut -f1)
    echo ""
    log_info "Found existing dataset that matches your selection:"
    echo "  $potential_existing (${dataset_size:-"unknown size"})"
    read -p "Use existing dataset or re-download/re-process? (e)xisting/(r)e-process: " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Ee]$ ]]; then
      DATASET_PATH="$potential_existing"
      log_success "Using existing dataset: $(basename "$DATASET_PATH")"
    else
      log_info "Will re-download and re-process the dataset"
      rm -f "$potential_existing"
    fi
  fi
  
else
  log_info "Dataset was specified via command line parameters"
fi

# Validate dataset name if provided
if [[ -n "$DATASET_NAME" ]]; then
  VALID_DATASET=false
  for valid_name in $VALID_DATASETS; do
    if [[ "$DATASET_NAME" == "$valid_name" ]]; then
      VALID_DATASET=true
      break
    fi
  done
  
  if [[ "$VALID_DATASET" == false ]]; then
    log_error "Invalid dataset name: $DATASET_NAME"
    echo "Valid options are: $VALID_DATASETS"
    exit 1
  fi
fi

# Ensure required tools are available for dataset processing
if ! command -v curl &> /dev/null && ! command -v wget &> /dev/null; then
  log_error "Either curl or wget is required to download datasets."
  exit 1
fi

# Check Python packages for dataset processing
for package in tqdm numpy h5py; do
  if ! $PYTHON_CMD -c "import $package" &> /dev/null; then
    log_error "Python package '$package' is required for dataset processing."
    echo "Please install with: pip install $package"
    exit 1
  fi
done

# Determine which dataset to use and process it
if [[ -n "$DATASET_PATH" ]]; then
  # User provided a specific JSON dataset path
  if [[ ! -f "$DATASET_PATH" ]]; then
    log_error "Dataset file not found: $DATASET_PATH"
    exit 1
  fi
  log_success "Using existing dataset: $DATASET_PATH"
elif [[ -n "$HDF5_PATH" ]]; then
  # User provided a specific HDF5 file
  if [[ ! -f "$HDF5_PATH" ]]; then
    log_error "HDF5 file not found: $HDF5_PATH"
    exit 1
  fi
  ORIGINAL_HDF5_PATH="$HDF5_PATH"
  log_info "Converting provided HDF5 file: $HDF5_PATH"
else
  # Download the specified dataset
  DATASET_URL=$(get_dataset_url "$DATASET_NAME")
  if [[ -z "$DATASET_URL" ]]; then
    log_error "Unknown dataset: $DATASET_NAME"
    exit 1
  fi
  
  HDF5_FILENAME=$(basename "$DATASET_URL")
  HDF5_FILEPATH="datasets/$HDF5_FILENAME"
  
  # Check if we already have this HDF5 file
  if [[ -f "$HDF5_FILEPATH" ]]; then
    log_success "Found existing HDF5 file: $HDF5_FILEPATH"
  else
    echo ""
    log_info "Downloading $DATASET_NAME dataset..."
    log_info "Source: $DATASET_URL"
    log_info "This may take a few minutes depending on dataset size and connection speed..."
    echo ""
    
    # Download with progress bar
    if command -v curl &> /dev/null; then
      curl -L --progress-bar "$DATASET_URL" -o "$HDF5_FILEPATH"
    else
      wget --progress=bar:force "$DATASET_URL" -O "$HDF5_FILEPATH"
    fi
    
    # Check if download was successful
    if [[ $? -ne 0 || ! -f "$HDF5_FILEPATH" ]]; then
      log_error "Failed to download dataset from $DATASET_URL"
      exit 1
    fi
    
    log_success "Successfully downloaded: $HDF5_FILEPATH"
  fi
  
  ORIGINAL_HDF5_PATH="$HDF5_FILEPATH"
fi

# Convert HDF5 to JSON if needed
if [[ -n "$ORIGINAL_HDF5_PATH" ]]; then
  # Generate JSON filename based on dataset name and limit
  if [[ -n "$DATASET_NAME" ]]; then
    JSON_FILENAME="${DATASET_NAME}_${DATASET_LIMIT}.json"
  else
    JSON_FILENAME="$(basename "$ORIGINAL_HDF5_PATH" .hdf5)_${DATASET_LIMIT}.json"
  fi
  
  DATASET_PATH="datasets/$JSON_FILENAME"
  
  # Check if we already have this JSON conversion
  if [[ -f "$DATASET_PATH" ]]; then
    log_success "Found existing converted dataset: $DATASET_PATH"
  else
    echo ""
    log_info "Converting HDF5 to JSON format..."
    log_info "Extracting $DATASET_LIMIT vectors from $(basename "$ORIGINAL_HDF5_PATH")"
    
    # Check if the converter script exists
    if [[ ! -f "hdf5_to_json_converter.py" ]]; then
      log_error "hdf5_to_json_converter.py not found!"
      echo "Please make sure the converter script is in the current directory."
      exit 1
    fi
    
    # Adjust dimension based on known datasets
    DIMENSION_ARG=""
    case "$DATASET_NAME" in
      "sift-128")
        DIMENSION_ARG="--dimension 128"
        ;;
      "glove-angular")
        DIMENSION_ARG="--dimension 25"
        ;;
      "wiki-all-1m"|"wiki-all-10m")
        DIMENSION_ARG="--dimension 768"
        ;;
    esac
    
    echo ""
    $PYTHON_CMD hdf5_to_json_converter.py "$ORIGINAL_HDF5_PATH" "$DATASET_PATH" --limit "$DATASET_LIMIT" $DIMENSION_ARG
    
    if [[ $? -ne 0 ]]; then
      log_error "Failed to convert HDF5 dataset to JSON."
      exit 1
    fi
    
    log_success "Successfully converted to JSON: $DATASET_PATH"
    
    # Show dataset info
    vector_count=$(grep -o '"id"' "$DATASET_PATH" | wc -l | xargs)
    log_info "Dataset ready: $vector_count vectors available for testing"
  fi
fi

# Ensure we have a dataset path set
if [[ -z "$DATASET_PATH" ]]; then
  log_error "No dataset path was set."
  exit 1
fi

# Final dataset verification and dimension auto-detection
if [[ ! -f "$DATASET_PATH" ]]; then
  log_error "Dataset file does not exist: $DATASET_PATH"
  exit 1
fi

# Auto-detect vector dimension from dataset
if [[ -f "$DATASET_PATH" ]]; then
  log_info "Auto-detecting vector dimension from dataset..."
  DETECTED_DIMENSION=$($PYTHON_CMD -c "
import json
import sys
try:
    with open('$DATASET_PATH', 'r') as f:
        data = json.load(f)
        if data and len(data) > 0:
            first_item = data[0]
            if 'vector' in first_item and isinstance(first_item['vector'], list):
                print(len(first_item['vector']))
            elif 'metadata' in first_item and 'dimension' in first_item['metadata']:
                print(first_item['metadata']['dimension'])
            else:
                print('384')  # default fallback
        else:
            print('384')  # default fallback
except Exception as e:
    print('384')  # default fallback on any error
  " 2>/dev/null || echo "384")
  
  # Update the vector dimension environment variable
  export VECTOR_DIMENSION=$DETECTED_DIMENSION
  log_success "Auto-detected vector dimension: $DETECTED_DIMENSION"
  
  # Validate detected dimension is reasonable
  if [[ $DETECTED_DIMENSION -lt 16 || $DETECTED_DIMENSION -gt 4096 ]]; then
    log_warning "Unusual vector dimension detected: $DETECTED_DIMENSION"
    log_warning "This may indicate an issue with the dataset format"
  fi
else
  log_warning "No dataset file found for dimension detection, using default: 384"
  export VECTOR_DIMENSION=384
fi

# Show final dataset info
dataset_size=$(du -h "$DATASET_PATH" 2>/dev/null | cut -f1)
log_success "Dataset ready for testing: $(basename "$DATASET_PATH") (${dataset_size:-"unknown size"})"

fi  # End of dataset processing section

# Service health check
log_info "Checking service health..."
if curl -s "${BASE_URL}/v1/health" > /dev/null; then
  health_response=$(curl -s "${BASE_URL}/v1/health")
  if echo "$health_response" | grep -q "healthy"; then
    log_success "Service is healthy and ready for load testing"
  else
    log_warning "Service responded but status unclear: $health_response"
  fi
else
  log_error "Service is not responding at $BASE_URL"
  echo "Make sure your CyborgDB service is running before starting load tests"
  
  read -p "Continue anyway? (y/n): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
  fi
fi

# Create results directory
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULTS_DIR="k6_results_${TIMESTAMP}"
mkdir -p $RESULTS_DIR

# Set up environment variables
export BASE_URL=$BASE_URL
export API_KEY=$API_KEY
export API_PREFIX=$API_PREFIX
export VU_MAX=$VU_MAX
export DURATION=$DURATION
export TEST_MODE=$TEST_MODE
export LITE_MODE=$LITE_MODE

# Set dataset path only if not using concurrent upsert
if [[ "$USE_CONCURRENT_UPSERT" = false ]]; then
  export DATASET_PATH=$DATASET_PATH
fi

# Set concurrent upsert specific variables
if [[ "$USE_CONCURRENT_UPSERT" = true ]]; then
  export TARGET_UPSERTS_PER_MINUTE=$TARGET_UPSERTS_PER_MINUTE
  export BATCH_SIZE=$BATCH_SIZE
  export RAMP_UP=$RAMP_UP
  export RAMP_DOWN=$RAMP_DOWN
fi

# Print test configuration
echo ""
log_info "Load Test Configuration:"
echo "  Base URL: $BASE_URL"
echo "  API Prefix: $API_PREFIX"  
echo "  Virtual Users: $VU_MAX"
echo "  Duration: $DURATION"
echo "  Test Mode: $TEST_MODE"
echo "  Test Script: $TEST_SCRIPT"

if [[ "$USE_CONCURRENT_UPSERT" = true ]]; then
  echo "  Test Type: Concurrent Upsert"
  echo "  Target Upserts/Min: $TARGET_UPSERTS_PER_MINUTE"
  echo "  Batch Size: $BATCH_SIZE"
  echo "  Ramp Up: $RAMP_UP"
  echo "  Ramp Down: $RAMP_DOWN"
else
  echo "  Test Type: Standard Load Test"
  echo "  Dataset: ${DATASET_PATH:-'No dataset'}"
  echo "  Vector Dimension: $VECTOR_DIMENSION (auto-detected)"
fi
echo ""

# Prepare output options
OUTPUT_OPTIONS=""
if [[ -n "$OUTPUT_FORMAT" ]]; then
  case $OUTPUT_FORMAT in
    json)
      OUTPUT_OPTIONS="--out json=$RESULTS_DIR/results.json"
      ;;
    csv)
      OUTPUT_OPTIONS="--out csv=$RESULTS_DIR/results.csv"
      ;;
    html)
      OUTPUT_OPTIONS=""
      ;;
    dashboard)
      OUTPUT_OPTIONS="--out dashboard"
      ;;
    grafana)
      if curl -s "$INFLUXDB_URL" &>/dev/null; then
        OUTPUT_OPTIONS="--out influxdb=$INFLUXDB_URL"
        echo "Results will be sent to InfluxDB for Grafana visualization"
      else
        log_warning "Could not connect to InfluxDB at $INFLUXDB_URL"
        OUTPUT_OPTIONS="--out json=$RESULTS_DIR/results.json"
      fi
      ;;
  esac
fi

# Check if test script exists
if [[ ! -f "$TEST_SCRIPT" ]]; then
  log_error "Test script '$TEST_SCRIPT' not found in current directory."
  exit 1
fi

# Run the test
log_info "Starting load test..."
echo ""

# Run k6 test
k6 run $OUTPUT_OPTIONS $TEST_SCRIPT 2>&1 | tee "$RESULTS_DIR/k6.log"
K6_EXIT_CODE=${PIPESTATUS[0]}

echo ""
log_info "Load test completed."

# Create summary file
cat << EOF > $RESULTS_DIR/test_summary.txt
CyborgDB Load Test Summary
==========================
Date: $(date)
Configuration:
  Base URL: $BASE_URL
  API Prefix: $API_PREFIX
  Virtual Users: $VU_MAX
  Duration: $DURATION
  Test Mode: $TEST_MODE
  Test Script: $TEST_SCRIPT
  Test Type: $([ "$USE_CONCURRENT_UPSERT" = true ] && echo "Concurrent Upsert" || echo "Standard Load Test")
  
$(if [ "$USE_CONCURRENT_UPSERT" = true ]; then
echo "Concurrent Upsert Settings:
  Target Upserts/Min: $TARGET_UPSERTS_PER_MINUTE
  Batch Size: $BATCH_SIZE
  Ramp Up: $RAMP_UP
  Ramp Down: $RAMP_DOWN"
else
echo "Standard Load Test Settings:
  Dataset: ${DATASET_PATH:-'No dataset'}
  Vector Dimension: $VECTOR_DIMENSION (auto-detected)"
fi)
  
Results Directory: $RESULTS_DIR
Log File: $RESULTS_DIR/k6.log
EOF

echo ""
log_success "Test complete! Results stored in $RESULTS_DIR"

if [[ $K6_EXIT_CODE -ne 0 ]]; then
  log_warning "Test had some failures - check the logs for details"
fi

exit $K6_EXIT_CODE