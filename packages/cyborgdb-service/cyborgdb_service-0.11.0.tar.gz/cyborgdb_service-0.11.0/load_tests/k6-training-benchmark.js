import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';
import { SharedArray } from 'k6/data';

// Define metrics focused on training
const errorRate = new Rate('error_rate');
const successRate = new Rate('success_rate');
const indexCreationDuration = new Trend('index_creation_duration');
const vectorUpsertDuration = new Trend('vector_upsert_duration');
const trainingDuration = new Trend('training_duration');
const trainingSuccessRate = new Rate('training_success_rate');
const successfulRequests = new Counter('successful_requests');

// Configuration via environment variables with defaults
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_KEY = __ENV.API_KEY || 'your-default-api-key';
const API_PREFIX = __ENV.API_PREFIX || '/v1';
const VECTOR_COUNT = parseInt(__ENV.VECTOR_COUNT || '1000');
const BATCH_SIZE = parseInt(__ENV.BATCH_SIZE || '100');
const N_LISTS = parseInt(__ENV.N_LISTS || '4');
const INDEX_COUNT = parseInt(__ENV.INDEX_COUNT || '3'); // Number of indexes to train per VU
const DIMENSION = parseInt(__ENV.DIMENSION || '384');

// Generate vector data
function generateVectorData(count, dimension) {
  console.log(`Generating ${count} random vectors of dimension ${dimension}...`);
  const data = [];
  
  // Define categories for more realistic data
  const categories = ['technology', 'science', 'art', 'business', 'health'];
  const priorities = [1, 2, 3, 4, 5];
  const names = ['John', 'Alice', 'Bob', 'Sarah', 'Michael', 'Emma', 'David', 'Olivia'];
  
  for (let i = 0; i < count; i++) {
    // Create realistic metadata
    const category = categories[i % categories.length];
    const priority = priorities[Math.floor(Math.random() * priorities.length)];
    const ownerName = names[Math.floor(Math.random() * names.length)];
    const tags = [category];
    
    if (i % 3 === 0) tags.push('important');
    if (i % 2 === 0) tags.push('reviewed');
    
    // Generate vector item with id, explicit vector, and rich metadata
    data.push({
      id: `gen-${i}`,
      vector: Array(dimension).fill(0).map(() => (Math.random() * 2 - 1)),
      metadata: {
        category: category,
        priority: priority,
        created_at: new Date().toISOString(),
        tags: tags,
        views: Math.floor(Math.random() * 1000),
        owner: {
          name: ownerName,
          level: Math.floor(Math.random() * 5) + 1,
          active: Math.random() > 0.2
        }
      }
    });
  }
  return data;
}

// Create a dataset with pre-generated vectors
const vectorData = new SharedArray('vector_data', function() {
  return generateVectorData(VECTOR_COUNT, DIMENSION);
});

export const options = {
  scenarios: {
    training_test: {
      executor: 'per-vu-iterations',
      vus: 1,
      iterations: INDEX_COUNT,
      maxDuration: '10m',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<10000'],
    success_rate: ['rate>0.7'],
    'training_success_rate': ['rate>0.8'],
  },
};

export default function() {
  // Headers for requests
  const headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  };
  
  // Generate a unique index name for this iteration
  const indexName = `training-test-${__VU}-${__ITER}-${randomString(6)}`;
  const indexKey = "1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef";
  
  console.log(`[Iteration ${__ITER + 1}/${INDEX_COUNT}] Starting training test with index ${indexName}`);
  
  // STEP 1: Create index
  console.log(`Creating index ${indexName}...`);
  let startTime = new Date();
  let res = http.post(`${BASE_URL}${API_PREFIX}/indexes/create`, JSON.stringify({
    "index_name": indexName,
    "index_key": indexKey,
    "index_config": {
      "type": "ivfflat",
      "n_lists": N_LISTS,
      "metric": "euclidean",
      "dimension": DIMENSION
    }
  }), { headers: headers });
  indexCreationDuration.add(new Date() - startTime);
  
  check(res, {
    'index creation successful': (r) => r.status === 200
  });
  
  errorRate.add(res.status !== 200);
  successRate.add(res.status === 200);
  
  if (res.status !== 200) {
    console.log(`Failed to create index: ${res.status}, ${res.body}`);
    return;
  }
  
  console.log(`Index ${indexName} created successfully`);
  
  // STEP 2: Upsert vectors
  console.log(`Upserting ${VECTOR_COUNT} vectors to ${indexName}...`);
  const batches = Math.ceil(VECTOR_COUNT / BATCH_SIZE);
  
  for (let batchIdx = 0; batchIdx < batches; batchIdx++) {
    const startIdx = batchIdx * BATCH_SIZE;
    const endIdx = Math.min(startIdx + BATCH_SIZE, VECTOR_COUNT);
    const itemsToUpsert = vectorData.slice(startIdx, endIdx).map((item, idx) => ({
      id: `${item.id}-${batchIdx}-${idx}`,
      vector: item.vector,
      metadata: item.metadata
    }));
    
    startTime = new Date();
    res = http.post(`${BASE_URL}${API_PREFIX}/vectors/upsert`, JSON.stringify({
      index_name: indexName,
      index_key: indexKey,
      items: itemsToUpsert
    }), { 
      headers: headers,
      timeout: '30s'
    });
    vectorUpsertDuration.add(new Date() - startTime);
    
    check(res, {
      [`vector upsert batch ${batchIdx+1}/${batches} successful`]: (r) => r.status === 200
    });
    
    errorRate.add(res.status !== 200);
    successRate.add(res.status === 200);
    
    if (res.status !== 200) {
      console.log(`Failed to upsert batch ${batchIdx+1}/${batches}: ${res.status}, ${res.body}`);
    }
    
    // Small delay between batches
    sleep(0.5);
  }
  
  console.log(`Completed upserting vectors to ${indexName}`);
  
  // STEP 3: Wait before training
  console.log(`Waiting 5 seconds before training...`);
  sleep(5);
  
  // STEP 4: Train the index
  console.log(`TRAINING INDEX ${indexName}...`);
  startTime = new Date();
  res = http.post(`${BASE_URL}${API_PREFIX}/indexes/train`, JSON.stringify({
    index_name: indexName,
    index_key: indexKey,
    batch_size: 32,
    max_iters: 5,
    tolerance: 1e-3
  }), { 
    headers: headers,
    timeout: '60s'
  });
  trainingDuration.add(new Date() - startTime);
  
  const trainingSuccessful = res.status === 200;
  
  // Important: Record training metrics
  trainingSuccessRate.add(trainingSuccessful);
  errorRate.add(!trainingSuccessful);
  successRate.add(trainingSuccessful);
  
  check(res, {
    'index training successful': (r) => r.status === 200
  });
  
  if (trainingSuccessful) {
    successfulRequests.add(1);
    console.log(`Training successful: ${res.status}, ${res.body}`);
  } else {
    console.log(`Training failed: ${res.status}, ${res.body}`);
  }
  
  // STEP 5: Run a test query
  console.log(`Running a test query on ${indexName}...`);
  const randomVector = vectorData[Math.floor(Math.random() * vectorData.length)].vector;
  
  res = http.post(`${BASE_URL}${API_PREFIX}/vectors/query`, JSON.stringify({
    index_name: indexName,
    index_key: indexKey,
    query_vector: randomVector,
    top_k: 5,
    include_metadata: true
  }), { headers: headers });
  
  check(res, {
    'query successful': (r) => r.status === 200
  });
  
  if (res.status === 200) {
    console.log(`Query successful, found ${res.json().results.length} results`);
  } else {
    console.log(`Query failed: ${res.status}, ${res.body}`);
  }
  
  // STEP 6: Delete the index
  console.log(`Cleaning up - deleting index ${indexName}...`);
  res = http.post(`${BASE_URL}${API_PREFIX}/indexes/delete`, JSON.stringify({
    index_name: indexName,
    index_key: indexKey
  }), { headers: headers });
  
  check(res, {
    'index deletion successful': (r) => r.status === 200
  });
  
  if (res.status === 200) {
    console.log(`Index ${indexName} deleted successfully`);
  } else {
    console.log(`Failed to delete index ${indexName}: ${res.status}, ${res.body}`);
  }
  
  console.log(`Training test iteration ${__ITER + 1}/${INDEX_COUNT} completed\n`);
  
  // Small delay between iterations
  sleep(2);
}