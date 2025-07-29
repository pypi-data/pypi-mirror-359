#!/usr/bin/env python
"""
HDF5 to JSON Converter for K6 Load Testing

This script converts vector data from an HDF5 file to a JSON format that can be loaded by k6.
It extracts actual vectors from benchmark datasets and generates synthetic text content for dual-mode testing.

Usage:
    python hdf5_to_json_converter.py input.hdf5 output.json [--limit N] [--dimension DIM]

Arguments:
    input.hdf5    Path to the input HDF5 file
    output.json   Path to the output JSON file
    --limit       Optional limit on the number of vectors to extract (default: 10000)
    --dimension   Optional dimension to resize vectors to (default: keep original)
"""

import os
import sys
import json
import argparse
import random
import numpy as np
import h5py
from tqdm import tqdm

# Metadata generation similar to integration tests
def generate_random_metadata(index):
    """Generate random metadata for a vector similar to the integration tests."""
    owners = ["John", "Alice", "Bob", "Sarah", "Mike", "Joseph"]
    tags_options = [
        ["pet", "cute"],
        ["animal", "friendly"],
        ["document", "important"],
        ["work", "urgent"],
        ["personal", "private"]
    ]
    
    return {
        "age": 25 + (index % 30),
        "owner": {
            "name": owners[index % len(owners)],
            "pets_owned": index % 5
        },
        "is_important": bool(index % 2),
        "priority": random.randint(1, 5),
        "tags": random.choice(tags_options),
        "source": "hdf5_dataset"
    }

def generate_random_content(index, length=50):
    """Generate random text content for embedding tests."""
    topics = ["machine learning", "artificial intelligence", "vector search", 
              "neural networks", "data science", "natural language processing",
              "computer vision", "robotics", "deep learning"]
    
    topic = topics[index % len(topics)]
    return f"Document {index} about {topic} with random content for semantic search testing."

def convert_hdf5_to_json(input_file, output_file, limit=10000, dimension=None):
    """
    Convert HDF5 vectors to JSON format suitable for k6 testing.
    
    Args:
        input_file: Path to the input HDF5 file
        output_file: Path to the output JSON file
        limit: Maximum number of vectors to extract
        dimension: Optional dimension to resize vectors to
    """
    print(f"Converting {input_file} to {output_file} (limit: {limit} vectors)")
    
    # Check if file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file {input_file} does not exist.")
        return False
    
    try:
        results = []
        with h5py.File(input_file, 'r') as f:
            # Get the dataset structure
            print("HDF5 file structure:")
            for key in f.keys():
                print(f"- {key}: {f[key].shape}")
            
            # Try to find vectors dataset - common names are 'train', 'vectors', 'embeddings'
            vectors_dataset = None
            potential_names = ['train', 'vectors', 'embeddings', 'data']
            
            for name in potential_names:
                if name in f:
                    vectors_dataset = f[name]
                    print(f"Found vectors dataset: {name} with shape {vectors_dataset.shape}")
                    break
            
            if vectors_dataset is None:
                # Try to use the first dataset found
                first_key = list(f.keys())[0]
                vectors_dataset = f[first_key]
                print(f"Using dataset: {first_key} with shape {vectors_dataset.shape}")
            
            # Get the total number of vectors
            total_vectors = min(vectors_dataset.shape[0], limit)
            original_dim = vectors_dataset.shape[1]
            
            print(f"Original vector dimension: {original_dim}")
            if dimension and dimension != original_dim:
                print(f"Will resize vectors from {original_dim}D to {dimension}D")
            
            # Process vectors
            print(f"Processing {total_vectors} vectors...")
            for i in tqdm(range(total_vectors)):
                # Get the actual vector from HDF5
                vector = vectors_dataset[i].astype(float).tolist()
                
                # Resize if needed
                if dimension and dimension != original_dim:
                    # Simple resizing - either truncate or pad with zeros
                    if dimension < original_dim:
                        vector = vector[:dimension]
                    else:
                        vector.extend([0.0] * (dimension - original_dim))
                
                # Create a JSON object with BOTH vector and contents
                vector_obj = {
                    "id": f"vec-{i}",
                    "vector": vector,  # ← FIXED: Actually include the vector data
                    "contents": generate_random_content(i),
                    "metadata": generate_random_metadata(i)
                }
                
                results.append(vector_obj)
                
                # Print progress occasionally
                if (i + 1) % 1000 == 0:
                    print(f"Processed {i + 1} vectors")
        
        # Write the JSON file
        print(f"Writing {len(results)} vectors to {output_file}")
        with open(output_file, 'w') as f:
            json.dump(results, f)
        
        # Verify the output
        print(f"Successfully converted {len(results)} vectors to JSON format")
        print(f"Each item contains: id, vector ({len(results[0]['vector']) if results else 'N/A'}D), contents, metadata")
        
        # Show sample structure
        if results:
            print("\nSample item structure:")
            sample = results[0].copy()
            sample['vector'] = f"[{len(sample['vector'])} floats]"  # Don't print full vector
            sample['contents'] = sample['contents'][:50] + "..." if len(sample['contents']) > 50 else sample['contents']
            print(json.dumps(sample, indent=2))
        
        return True
        
    except Exception as e:
        print(f"Error converting file: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Convert HDF5 vector data to JSON for k6 testing')
    parser.add_argument('input_file', help='Path to the input HDF5 file')
    parser.add_argument('output_file', help='Path to the output JSON file')
    parser.add_argument('--limit', type=int, default=10000, help='Maximum number of vectors to extract')
    parser.add_argument('--dimension', type=int, help='Dimension to resize vectors to (optional)')
    
    args = parser.parse_args()
    
    success = convert_hdf5_to_json(args.input_file, args.output_file, args.limit, args.dimension)
    if success:
        print("\nConversion completed successfully!")
        print(f"   Output: {args.output_file}")
        print(f"   Test with pre-computed vectors:")
        print(f"      ./run-load-tests.sh -D {args.output_file}")
        print(f"   Test with real embeddings:")
        print(f"      ./run-load-tests.sh -D {args.output_file} --real-embeddings --embedding-model all-MiniLM-L6-v2")
    else:
        print("\nConversion failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
