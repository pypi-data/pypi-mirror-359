#!/usr/bin/env python3
import json
import sys
import random
import argparse
from datetime import datetime, timedelta

def generate_synthetic_dataset(output_path, count=10000):
    """Generate a synthetic dataset with realistic structure"""
    
    categories = ['technology', 'science', 'business', 'health', 'arts']
    names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry']
    
    data = []
    for i in range(count):
        category = random.choice(categories)
        
        # Generate realistic content based on category
        content_map = {
            'technology': f"Advanced technology research document {i} discussing AI, machine learning, and software development methodologies in modern computing systems.",
            'science': f"Scientific research paper {i} exploring findings in physics, chemistry, and biological sciences with experimental data and analysis.",
            'business': f"Business analysis document {i} covering market trends, financial strategies, and corporate governance in the modern economy.",
            'health': f"Medical research publication {i} addressing healthcare innovations, treatment protocols, and patient care methodologies.",
            'arts': f"Creative arts document {i} featuring artistic expression, cultural analysis, and aesthetic principles in contemporary society."
        }
        
        # Create realistic metadata
        created_date = datetime.now() - timedelta(days=random.randint(1, 365))
        
        item = {
            'id': f'synthetic-{i}',
            'contents': content_map[category],
            'metadata': {
                'category': category,
                'priority': random.randint(1, 5),
                'created_at': created_date.isoformat(),
                'views': random.randint(10, 1000),
                'tags': [category] + random.sample(['important', 'reviewed', 'archived', 'featured'], random.randint(0, 2)),
                'owner': {
                    'name': random.choice(names),
                    'level': random.randint(1, 5),
                    'active': random.choice([True, False])
                }
            }
        }
        data.append(item)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"Generated {len(data)} synthetic items to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate synthetic dataset')
    parser.add_argument('output', help='Output JSON file path')
    parser.add_argument('--count', type=int, default=10000, help='Number of items to generate')
    
    args = parser.parse_args()
    generate_synthetic_dataset(args.output, args.count)
