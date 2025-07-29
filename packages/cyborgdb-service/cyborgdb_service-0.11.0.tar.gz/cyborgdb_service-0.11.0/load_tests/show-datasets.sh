#!/bin/bash
# Show information about available datasets

echo "CyborgDB Load Testing - Available Datasets"
echo "=========================================="
echo ""

echo "Benchmark Datasets (downloaded automatically):"
echo ""

echo "📊 sift-128"
echo "   Description: SIFT 128-dimensional feature vectors"
echo "   Vectors: ~1M vectors"
echo "   Dimension: 128"
echo "   Metric: Euclidean distance"
echo "   Use case: Computer vision, image features"
echo "   URL: http://ann-benchmarks.com/sift-128-euclidean.hdf5"
echo ""

echo "📝 glove-angular"
echo "   Description: GloVe word embeddings"
echo "   Vectors: ~1.2M vectors"
echo "   Dimension: 25"
echo "   Metric: Angular/Cosine similarity"
echo "   Use case: Natural language processing, word similarity"
echo "   URL: http://ann-benchmarks.com/glove-25-angular.hdf5"
echo ""

echo "📚 wiki-all-1m [DEFAULT]"
echo "   Description: Wikipedia article embeddings"
echo "   Vectors: 1M vectors"
echo "   Dimension: 768"
echo "   Metric: Euclidean/Cosine"
echo "   Use case: Document similarity, semantic search"
echo "   URL: https://wiki-all.s3.us-east-1.amazonaws.com/wiki_all_1M.hdf5"
echo ""

echo "📖 wiki-all-10m"
echo "   Description: Wikipedia article embeddings (large)"
echo "   Vectors: 10M vectors"
echo "   Dimension: 768"
echo "   Metric: Euclidean/Cosine"
echo "   Use case: Large-scale document similarity, performance testing"
echo "   URL: https://wiki-all.s3.us-east-1.amazonaws.com/wiki_all_10M.hdf5"
echo ""

echo "Usage Examples:"
echo "==============="
echo ""
echo "# Use default dataset (wiki-all-1m)"
echo "./run-load-tests.sh -k your-api-key"
echo ""
echo "# Use SIFT dataset for computer vision workloads"
echo "./run-load-tests.sh -n sift-128 -c 100000"
echo ""
echo "# Use GloVe for NLP workloads with cosine similarity"
echo "./run-load-tests.sh -n glove-angular -c 50000 -m advanced"
echo ""
echo "# Large-scale testing with 10M Wikipedia vectors"
echo "./run-load-tests.sh -n wiki-all-10m -c 500000 -v 5 -d 10m"
echo ""
echo "# Custom dataset"
echo "./run-load-tests.sh -H /path/to/your/vectors.hdf5"
echo "./run-load-tests.sh -D /path/to/your/vectors.json"
echo ""

echo "Dataset Storage:"
echo "==============="
echo "- Downloaded HDF5 files are stored in: ./datasets/"
echo "- Converted JSON files are cached for faster subsequent runs"
echo "- File naming: {dataset-name}_{limit}.json"
echo ""

echo "Requirements:"
echo "============"
echo "- Python 3 with packages: h5py, numpy, tqdm"
echo "- curl or wget for downloads"
echo "- Sufficient disk space (datasets range from 500MB to 30GB)"
echo ""

# Show current dataset status
if [[ -d "datasets" ]]; then
    echo "Current Dataset Status:"
    echo "======================"
    echo "Datasets directory: $(pwd)/datasets"
    
    if [[ -n "$(ls -A datasets/ 2>/dev/null)" ]]; then
        echo "Downloaded files:"
        ls -lh datasets/ | grep -E '\.(hdf5|json)$' | awk '{print "  " $9 " (" $5 ")"}'
    else
        echo "No datasets downloaded yet."
    fi
    echo ""
fi

echo "For more information, run: ./run-load-tests.sh --help"