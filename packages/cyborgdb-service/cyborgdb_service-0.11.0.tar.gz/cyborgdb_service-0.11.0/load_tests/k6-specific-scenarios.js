// Specific scenario for stress testing vector queries
import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Trend, Rate, Counter } from 'k6/metrics';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';

// Custom metrics for this test
const queryResponseTime = new Trend('query_response_time');
const queryErrorRate = new Rate('query_error_rate');
const concurrentQueries = new Counter('concurrent_queries');
const slowQueries = new Counter('slow_queries');

// Configuration via environment variables
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_KEY = __ENV.API_KEY || 'your-default-api-key';
const API_PREFIX = __ENV.API_PREFIX || '/v1';
const INDEX_NAME = __ENV.INDEX_NAME || 'test-index'; // Use a pre-created index
const INDEX_KEY = __ENV.INDEX_KEY || 'your-index-key';
const QUERY_INTENSITY = parseInt(__ENV.QUERY_INTENSITY || '10'); // Number of queries per iteration

// Test options for stress testing query performance
export const options = {
  scenarios: {
    // Scenario 1: Sustained query load
    sustained_queries: {
      executor: 'constant-vus',
      vus: 20,
      duration: '2m',
      tags: { scenario: 'sustained_queries' }
    },
    
    // Scenario 2: Query spikes
    query_spikes: {
      executor: 'ramping-arrival-rate',
      startRate: 5,
      timeUnit: '1s',
      preAllocatedVUs: 50,
      maxVUs: 100,
      stages: [
        { duration: '30s', target: 5 },   // Baseline
        { duration: '20s', target: 50 },  // Spike
        { duration: '30s', target: 10 },  // Settle
        { duration: '20s', target: 80 },  // Larger spike
        { duration: '30s', target: 5 }    // Return to baseline
      ],
      tags: { scenario: 'query_spikes' }
    }
  },
  thresholds: {
    'query_response_time': ['p(95)<500', 'p(99)<1000'],
    'query_error_rate': ['rate<0.05'],
    'http_req_duration': ['p(95)<1000'],
  },
};

// Generate a diverse set of query patterns
const queryPatterns = [
  "technology AI machine learning",
  "database vector search",
  "neural networks embeddings",
  "information retrieval systems",
  "computer science algorithms",
  "data processing techniques",
  "language models NLP",
  "machine vision recognition",
  "robotics automation systems",
  "cloud computing infrastructure",
  "data analytics visualization",
  "security encryption methods",
  "blockchain distributed ledger"
];

function generateQueryVariation(basePattern) {
  const pattern = basePattern.split(' ');
  // Randomly keep, remove, or reorder parts of the query
  const shuffled = pattern
    .filter(() => Math.random() > 0.2) // Randomly drop some terms
    .sort(() => Math.random() - 0.5);  // Shuffle remaining terms
    
  // Add some random noise occasionally
  if (Math.random() > 0.7) {
    shuffled.push(randomString(5));
  }
  
  return shuffled.join(' ');
}

export function setup() {
  // Check if the specified index exists
  const headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  };
  
  const listIndexUrl = `${BASE_URL}${API_PREFIX}/indexes/list`;
  const res = http.get(listIndexUrl, { headers });
  
  if (res.status !== 200) {
    throw new Error(`Failed to list indexes. Status: ${res.status}, Response: ${res.body}`);
  }
  
  const indexExists = res.json().indexes.includes(INDEX_NAME);
  if (!indexExists) {
    console.warn(`Index '${INDEX_NAME}' does not exist. This test assumes a pre-populated index.`);
    console.warn('Please create and populate an index before running this test or specify a valid INDEX_NAME environment variable.');
  }
  
  return {
    baseUrl: BASE_URL,
    apiKey: API_KEY,
    apiPrefix: API_PREFIX,
    indexName: INDEX_NAME,
    indexKey: INDEX_KEY,
    headers: headers
  };
}

export default function(data) {
  const { baseUrl, apiPrefix, indexName, indexKey, headers } = data;
  
  group('Vector Query Performance Test', function() {
    // Perform multiple queries in sequence to simulate high query load
    for (let i = 0; i < QUERY_INTENSITY; i++) {
      // Select a base query pattern and generate a variation
      const basePattern = queryPatterns[Math.floor(Math.random() * queryPatterns.length)];
      const queryText = generateQueryVariation(basePattern);
      
      // Mix up the query parameters
      const topK = Math.floor(Math.random() * 20) + 1; // Random top_k between 1 and 20
      const includeMetadata = Math.random() > 0.3; // Sometimes exclude metadata
      
      const queryUrl = `${baseUrl}${apiPrefix}/vectors/query`;
      
      // Match the query format used in k6-load-tests.js
      // The API supports both query_vector and query_contents
      const queryPayload = {
        index_name: indexName,
        index_key: indexKey,
        query_contents: queryText,  // Using text-based query
        top_k: topK,
        include_metadata: includeMetadata
      };
      
      // Track concurrent queries
      concurrentQueries.add(1);
      
      // Perform the query and measure response time
      const startTime = new Date();
      const res = http.post(queryUrl, JSON.stringify(queryPayload), {
        headers: headers,
        tags: { 
          query_type: 'vector_search',
          top_k: topK.toString(),
          include_metadata: includeMetadata.toString()
        }
      });
      const duration = new Date() - startTime;
      
      // Record metrics
      queryResponseTime.add(duration);
      queryErrorRate.add(res.status !== 200);
      
      // Track slow queries
      if (duration > 500) {
        slowQueries.add(1, { query: queryText, duration: duration.toString() });
      }
      
      // Validate response
      check(res, {
        'query status is 200': (r) => r.status === 200,
        'query results are returned': (r) => Array.isArray(r.json().results),
        'results count matches or is less than top_k': (r) => {
          const results = r.json().results;
          return Array.isArray(results) && results.length <= topK;
        }
      });
      
      // Short delay between queries in the same VU
      sleep(Math.random() * 0.2);
    }
  });
  
  // Vary sleep time to create more realistic request patterns
  sleep(Math.random() * 2);
}