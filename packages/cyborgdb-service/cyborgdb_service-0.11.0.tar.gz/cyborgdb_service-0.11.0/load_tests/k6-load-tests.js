import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend, Gauge } from 'k6/metrics';

import { randomString } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';
import { SharedArray } from 'k6/data';


const errorRate = new Rate('error_rate');
const successRate = new Rate('success_rate');
const indexCreationDuration = new Trend('index_creation_duration');
const vectorUpsertDuration = new Trend('vector_upsert_duration');
const vectorQueryDuration = new Trend('vector_query_duration');
const metadataQueryDuration = new Trend('metadata_query_duration');
const trainingDuration = new Trend('training_duration');
const trainingSuccessRate = new Rate('training_success_rate');

// Performance monitoring metrics
const concurrentRequests = new Gauge('concurrent_requests');
const embeddingLatency = new Trend('embedding_latency');
const retryAttempts = new Counter('retry_attempts');

// Configuration via environment variables with defaults
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_KEY = __ENV.API_KEY || 'your-default-api-key';
const API_PREFIX = __ENV.API_PREFIX || '/v1';
const VU_MAX = parseInt(__ENV.VU_MAX || '10');
const DURATION = __ENV.DURATION || '1m';
const TEST_MODE = __ENV.TEST_MODE || 'standard';
const DATASET_PATH = __ENV.DATASET_PATH;
const LITE_MODE = __ENV.LITE_MODE === 'true';

// Vector configuration
const VECTOR_DIMENSION = parseInt(__ENV.VECTOR_DIMENSION || '384');
const INDEX_METRIC = __ENV.INDEX_METRIC || 'euclidean';
const EMBEDDING_MODEL = __ENV.EMBEDDING_MODEL || '';
const USE_REAL_EMBEDDINGS = __ENV.USE_REAL_EMBEDDINGS === 'true';

console.log(`Vector config: ${VECTOR_DIMENSION}D vectors, ${INDEX_METRIC} metric`);
console.log(`Embedding mode: ${USE_REAL_EMBEDDINGS ? 'Real embeddings from ' + EMBEDDING_MODEL : 'Pre-computed vectors'}`);

// Load vector data from dataset
const vectorData = new SharedArray('vector_data', function() {
  if (DATASET_PATH) {
    console.log(`Loading data from dataset: ${DATASET_PATH}`);
    try {
      const fileContent = open(DATASET_PATH, 'r');
      const dataset = JSON.parse(fileContent);
      console.log(`Successfully loaded ${dataset.length} items from ${DATASET_PATH}`);
      
      // Validate dataset format
      if (dataset.length > 0) {
        const firstItem = dataset[0];
        
        if (USE_REAL_EMBEDDINGS) {
          if (!firstItem.contents) {
            console.log(`Warning: Real embeddings enabled but first item missing 'contents' field`);
            console.log(`Available fields: ${Object.keys(firstItem).join(', ')}`);
          } else {
            console.log(`Real embeddings: Will generate embeddings from text content`);
            console.log(`Sample text: "${firstItem.contents.substring(0, 100)}..."`);
          }
        } else {
          if (!firstItem.vector) {
            console.log(`Warning: Pre-computed mode but first item missing 'vector' field`);
            console.log(`Available fields: ${Object.keys(firstItem).join(', ')}`);
          } else {
            console.log(`Pre-computed vectors: Using ${firstItem.vector.length}D vectors from dataset`);
            if (firstItem.vector.length !== VECTOR_DIMENSION) {
              console.log(`Warning: Vector dimension mismatch. Expected ${VECTOR_DIMENSION}, got ${firstItem.vector.length}`);
            }
          }
        }
      }
      
      return dataset;
    } catch (error) {
      console.log(`Failed to load dataset ${DATASET_PATH}: ${error}`);
      throw new Error(`Cannot load dataset file: ${DATASET_PATH}. Make sure the file exists and is readable.`);
    }
  } else {
    throw new Error('No dataset path provided - dataset is required for load testing');
  }
});

// Performance tracking
let currentConcurrentRequests = 0;

// Request wrapper with retry logic and performance tracking
function makeRequest(url, payload, headers, requestType, timeout = '120s', maxRetries = 3) {
  currentConcurrentRequests++;
  concurrentRequests.add(currentConcurrentRequests);
  
  let lastResponse;
  let attempt = 0;
  
  while (attempt <= maxRetries) {
    const startTime = new Date();
    
    const response = http.post(url, payload, {
      headers: headers,
      timeout: timeout,
      tags: { 
        type: requestType,
        vu: __VU.toString(),
        attempt: attempt.toString(),
        concurrent_level: currentConcurrentRequests.toString(),
        vector_dim: VECTOR_DIMENSION.toString()
      }
    });
    
    currentConcurrentRequests--;
    const duration = new Date() - startTime;
    lastResponse = response;
    
    // Track embedding performance if available
    if (requestType.includes('upsert') && response.body) {
      try {
        const body = JSON.parse(response.body);
        if (body.embedding_time) {
          embeddingLatency.add(body.embedding_time);
        }
      } catch (e) {
        // Body not JSON or missing timing info
      }
    }
    
    // Success case
    if (response.status === 200) {
      if (attempt > 0) {
        console.log(`[RETRY-SUCCESS] VU${__VU}: ${requestType} succeeded on attempt ${attempt + 1}`);
      }
      break;
    }
    
    // Rate limit case - wait and retry with exponential backoff
    if (response.status === 429 && attempt < maxRetries) {
      retryAttempts.add(1);
      const waitTime = Math.min(60, (2 ** attempt) * 5);
      console.log(`[RETRY] VU${__VU}: ${requestType} rate limited, waiting ${waitTime}s (attempt ${attempt + 1})`);
      sleep(waitTime);
      attempt++;
      continue;
    }
    
    // Timeout case - retry with longer timeout
    if (response.status === 0 && response.error && response.error.includes('timeout') && attempt < maxRetries) {
      retryAttempts.add(1);
      console.log(`[RETRY] VU${__VU}: ${requestType} timeout, retrying with longer timeout (attempt ${attempt + 1})`);
      timeout = '240s';
      attempt++;
      continue;
    }
    
    // Log other errors but don't retry
    if (response.status !== 200) {
      console.log(`[ERROR] VU${__VU}: ${requestType} failed with status ${response.status}: ${response.body}`);
    }
    
    break;
  }
  
  return lastResponse;
}

// Helper function to generate a random index key (hex format)
function generateIndexKey() {
  let hexKey = '';
  const hexChars = '0123456789abcdef';
  for (let i = 0; i < 64; i++) {
    hexKey += hexChars.charAt(Math.floor(Math.random() * hexChars.length));
  }
  return hexKey;
}

// Generate metadata filters for testing
function generateMetadataFilter(complexity = 'simple') {
  const filters = {
    simple: [
      { "category": "technology" },
      { "priority": {"$gt": 3} },
      { "tags": "important" }
    ],
    medium: [
      { "$and": [{"category": "science"}, {"priority": {"$gt": 2}}] },
      { "tags": {"$in": ["important", "reviewed"]} }
    ],
    complex: [
      { "$and": [
          {"priority": {"$gt": 2}},
          {"$or": [
            {"category": "technology"},
            {"category": "science"}
          ]}
        ]
      }
    ]
  };
  
  const filterGroup = filters[complexity] || filters.simple;
  return filterGroup[Math.floor(Math.random() * filterGroup.length)];
}

// Test scenarios
const testScenarios = {
  standard: {
    vectorsPerIndex: 5000,
    trainingDelay: 15,
    queryCount: 5,
    useFilters: false,
    deletePercent: 100,
    batchSize: 100
  },
  advanced: {
    vectorsPerIndex: 10000,
    trainingDelay: 20,
    queryCount: 8,
    useFilters: true,
    deletePercent: 70,
    batchSize: 150
  },
  query_intense: {
    vectorsPerIndex: 7500,
    trainingDelay: 25,
    queryCount: 15,
    useFilters: true,
    deletePercent: 50,
    batchSize: 100
  },
  metadata_filter: {
    vectorsPerIndex: 8000,
    trainingDelay: 20,
    queryCount: 10,
    useFilters: true,
    complexFilters: true,
    deletePercent: 60,
    batchSize: 120
  }
};

const activeScenario = testScenarios[TEST_MODE] || testScenarios.standard;

// Teardown with cleanup
export function teardown(data) {
  if (!data || !data.sharedIndexName) {
    console.log('[TEARDOWN] No shared index to clean up');
    return;
  }
  
  const { sharedIndexName, sharedIndexKey, headers, baseUrl, apiPrefix } = data;
  
  console.log(`[TEARDOWN] Processing shared index: ${sharedIndexName}`);
  
  // Generate performance summary
  console.log('\n=== TEST SUMMARY ===');
  console.log(`Test Scenario: ${TEST_MODE}`);
  console.log(`Dataset used: ${DATASET_PATH || 'No dataset'}`);
  console.log(`Test duration: ${DURATION} with ${VU_MAX} VUs`);
  console.log(`Vectors per index: ${activeScenario.vectorsPerIndex}`);
  
  // Clean up the index
  console.log('\n[TEARDOWN] Deleting shared index...');
  const deleteIndexUrl = `${baseUrl}${apiPrefix}/indexes/delete`;
  const deletePayload = JSON.stringify({
    index_name: sharedIndexName,
    index_key: sharedIndexKey
  });
  
  const res = http.post(deleteIndexUrl, deletePayload, { headers: headers });
  
  if (res.status === 200) {
    console.log(`[TEARDOWN] Shared index ${sharedIndexName} deleted successfully`);
  } else {
    console.log(`[TEARDOWN] Failed to delete shared index: ${res.status}, ${res.body}`);
  }
}

export const options = {
  scenarios: {
    ramping_load: {
      executor: 'ramping-vus',
      startVUs: 1,
      stages: [
        { duration: '60s', target: Math.ceil(VU_MAX * 0.3) },
        { duration: '120s', target: Math.ceil(VU_MAX * 0.7) },
        { duration: DURATION, target: VU_MAX },
        { duration: '60s', target: 0 }
      ],
      gracefulRampDown: '30s',
    },
  },
  thresholds: {
    http_req_duration: ['p(95)<120000'],
    success_rate: ['rate>0.8'],
    'training_success_rate': ['rate>0.7'],
  },
};

// Test setup - creates and trains one shared index
export function setup() {
  const healthUrl = `${BASE_URL}${API_PREFIX}/health`;
  const healthRes = http.get(healthUrl);
  
  if (healthRes.status !== 200) {
    throw new Error(`Service is not healthy! Status: ${healthRes.status}, Response: ${healthRes.body}`);
  }
  
  console.log(`Service is healthy. Test mode: ${TEST_MODE}`);
  console.log(`Using dataset: ${DATASET_PATH || 'No dataset path set'}`);
  console.log(`Dataset config: ${VECTOR_DIMENSION}D vectors, ${INDEX_METRIC} metric`);
  console.log(`Vectors per index: ${activeScenario.vectorsPerIndex}`);
  
  const sharedIndexName = `k6-test-${TEST_MODE}-${Date.now()}`;
  const sharedIndexKey = generateIndexKey();
  
  const headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  };
  
  console.log(`[SETUP] Creating shared index: ${sharedIndexName}`);
  
  // Create the shared index
  const createIndexUrl = `${BASE_URL}${API_PREFIX}/indexes/create`;
  const createPayload = {
    "index_name": sharedIndexName,
    "index_key": sharedIndexKey,
    "index_config": {
      "type": "ivfflat",
      "n_lists": 8,
      "metric": INDEX_METRIC,
      "dimension": VECTOR_DIMENSION
    }
  };
  
  // Add embedding model if using real embeddings
  if (USE_REAL_EMBEDDINGS) {
    createPayload.embedding_model = EMBEDDING_MODEL;
    console.log(`[SETUP] Creating index with real embeddings: ${EMBEDDING_MODEL} → ${VECTOR_DIMENSION}D`);
  } else {
    console.log(`[SETUP] Creating index for pre-computed ${VECTOR_DIMENSION}D vectors`);
  }
  
  let res = http.post(createIndexUrl, JSON.stringify(createPayload), { headers: headers });
  
  if (res.status !== 200) {
    throw new Error(`Failed to create shared index: ${res.status}, ${res.body}`);
  }
  
  console.log(`[SETUP] Shared index created successfully`);
  
  // Upsert initial vectors for training
  const SETUP_BATCH_SIZE = 50;
  const SETUP_VECTORS = Math.min(200, vectorData.length);
  
  console.log(`[SETUP] Upserting ${SETUP_VECTORS} vectors for initial training...`);
  
  const upsertUrl = `${BASE_URL}${API_PREFIX}/vectors/upsert`;
  const itemsToUpsert = [];
  
  for (let i = 0; i < SETUP_VECTORS; i++) {
    const item = vectorData[i];
    
    const upsertItem = {
      id: `setup-${i}`,
      metadata: { 
        phase: 'setup',
        original_id: item.id || `vec-${i}`
      }
    };
    
    // Use appropriate data format based on embedding mode
    if (USE_REAL_EMBEDDINGS) {
      upsertItem.contents = item.contents || `Setup document ${i} for training`;
    } else {
      if (item.vector && Array.isArray(item.vector)) {
        upsertItem.vector = item.vector;
      } else {
        console.log(`[SETUP] Warning: Item ${i} missing vector data, skipping`);
        continue;
      }
    }
    
    itemsToUpsert.push(upsertItem);
  }
  
  const upsertPayload = JSON.stringify({
    index_name: sharedIndexName,
    index_key: sharedIndexKey,
    items: itemsToUpsert
  });
  
  res = http.post(upsertUrl, upsertPayload, {
    headers: headers,
    timeout: '180s'
  });
  
  if (res.status === 200) {
    console.log(`[SETUP] Setup vectors upserted successfully`);
  } else {
    console.log(`[SETUP] Setup upsert failed: ${res.status}, ${res.body}`);
    console.log(`[SETUP] Continuing anyway - test will add more vectors...`);
  }
  
  // Train the index
  if (SETUP_VECTORS >= 50) {
    console.log(`[SETUP] Training shared index...`);
    sleep(5);
    
    const trainUrl = `${BASE_URL}${API_PREFIX}/indexes/train`;
    const trainPayload = JSON.stringify({
      index_name: sharedIndexName,
      index_key: sharedIndexKey,
      batch_size: 32,
      max_iters: 10,
      tolerance: 1e-4
    });
    
    res = http.post(trainUrl, trainPayload, {
      headers: headers,
      timeout: '300s'
    });
    
    if (res.status === 200) {
      console.log(`[SETUP] Training completed successfully`);
    } else {
      console.log(`[SETUP] Training failed: ${res.status}, ${res.body}`);
      console.log(`[SETUP] Continuing with untrained index...`);
    }
  }
  
  console.log(`[SETUP] Setup complete! Ready for load testing.`);
  
  return {
    baseUrl: BASE_URL,
    apiKey: API_KEY,
    apiPrefix: API_PREFIX,
    sharedIndexName: sharedIndexName,
    sharedIndexKey: sharedIndexKey,
    headers: headers
  };
}

// Main test function
export default function(data) {
  const { baseUrl, apiPrefix, headers, sharedIndexName, sharedIndexKey } = data;
  const vuId = __VU;
  
  console.log(`[VU ${vuId}] Starting load test using shared index: ${sharedIndexName}`);
  
  group('Health Check', function() {
    const healthUrl = `${baseUrl}${apiPrefix}/health`;
    const res = http.get(healthUrl, { tags: { type: 'health' } });
    
    check(res, {
      'health status is 200': (r) => r.status === 200,
    });
    
    errorRate.add(res.status !== 200);
    successRate.add(res.status === 200);
  });
  
  group('Vector Operations', function() {
    const upsertUrl = `${baseUrl}${apiPrefix}/vectors/upsert`;
    const BATCH_SIZE = activeScenario.batchSize || 100;
    const VU_VECTORS = Math.floor(activeScenario.vectorsPerIndex / VU_MAX);
    const batches = Math.ceil(VU_VECTORS / BATCH_SIZE);
    
    console.log(`[VU ${vuId}] Adding ${VU_VECTORS} vectors in ${batches} batches`);
    
    let vuTotalVectors = 0;
    
    for (let batchIdx = 0; batchIdx < batches; batchIdx++) {
      const dataOffset = (vuId * VU_VECTORS) + (batchIdx * BATCH_SIZE);
      const endIdx = Math.min(dataOffset + BATCH_SIZE, dataOffset + (VU_VECTORS - (batchIdx * BATCH_SIZE)));
      const batchSize = endIdx - dataOffset;
      
      if (batchSize <= 0) break;
      
      const itemsToUpsert = [];
      for (let i = 0; i < batchSize; i++) {
        const dataIdx = (dataOffset + i) % vectorData.length;
        const item = vectorData[dataIdx];
        
        const upsertItem = {
          id: `test-vu${vuId}-batch${batchIdx}-${i}-${Date.now()}`,
          metadata: {
            ...item.metadata,
            vu_id: vuId,
            batch_id: batchIdx,
            phase: 'load_test',
            test_scenario: TEST_MODE
          }
        };
        
        // Use appropriate data format based on embedding mode
        if (USE_REAL_EMBEDDINGS) {
          upsertItem.contents = item.contents || `Load test document ${dataIdx}`;
        } else {
          if (item.vector && Array.isArray(item.vector)) {
            upsertItem.vector = item.vector;
          } else {
            console.log(`[VU ${vuId}] Warning: Item ${dataIdx} missing vector data, using fallback`);
            upsertItem.vector = Array(VECTOR_DIMENSION).fill(0).map(() => (Math.random() * 2 - 1));
          }
        }
        
        itemsToUpsert.push(upsertItem);
      }
      
      const upsertPayload = JSON.stringify({
        index_name: sharedIndexName,
        index_key: sharedIndexKey,
        items: itemsToUpsert
      });
      
      let startTime = new Date();
      let res = makeRequest(upsertUrl, upsertPayload, headers, 'vector_upsert', '120s', 3);
      vectorUpsertDuration.add(new Date() - startTime);
      
      const success = res.status === 200;
      check(res, {
        [`[VU ${vuId}] vector upsert batch ${batchIdx+1} successful`]: (r) => success
      });
      
      errorRate.add(!success);
      successRate.add(success);
      
      if (success) {
        vuTotalVectors += itemsToUpsert.length;
        if (batchIdx % 5 === 0 || batchIdx === batches - 1) {
          console.log(`[VU ${vuId}] Progress: ${vuTotalVectors}/${VU_VECTORS} vectors upserted`);
        }
      } else {
        console.log(`[VU ${vuId}] Failed upsert batch ${batchIdx+1}: ${res.status}`);
      }
      
      sleep(Math.random() * 3 + 1);
    }
    
    console.log(`[VU ${vuId}] Completed upserts: ${vuTotalVectors} vectors added`);
  });
  
  group('Vector Queries', function() {
    const queryCount = activeScenario.queryCount;
    const useFilters = activeScenario.useFilters;
    
    console.log(`[VU ${vuId}] Running ${queryCount} queries`);
    
    for (let queryIdx = 0; queryIdx < queryCount; queryIdx++) {
      const currentQueryUsesFilter = useFilters && (queryIdx % 2 === 1);
      const queryUrl = `${baseUrl}${apiPrefix}/vectors/query`;
      
      const randomItem = vectorData[Math.floor(Math.random() * vectorData.length)];
      
      const queryPayload = {
        index_name: sharedIndexName,
        index_key: sharedIndexKey,
        top_k: 10,
        include_metadata: true
      };
      
      // Use appropriate query format based on embedding mode
      if (USE_REAL_EMBEDDINGS) {
        if (randomItem.contents && typeof randomItem.contents === 'string') {
          queryPayload.query_contents = randomItem.contents;
        } else {
          console.log(`[VU ${vuId}] Warning: No valid contents found, using fallback text`);
          queryPayload.query_contents = `Fallback query text for test ${queryIdx}`;
        }
      } else {
        if (randomItem.vector && Array.isArray(randomItem.vector)) {
          queryPayload.query_vector = randomItem.vector;
        } else {
          console.log(`[VU ${vuId}] Warning: No valid vector found in dataset item, skipping query`);
          continue;
        }
      }
      
      // Add metadata filter for some queries
      if (currentQueryUsesFilter) {
        const filterComplexity = activeScenario.complexFilters ? 
                                 ['simple', 'medium', 'complex'][queryIdx % 3] :
                                 'simple';
        queryPayload.filters = generateMetadataFilter(filterComplexity);
      }
      
      let startTime = new Date();
      let res = makeRequest(queryUrl, JSON.stringify(queryPayload), headers, 
                           currentQueryUsesFilter ? 'metadata_query' : 'vector_query', '60s', 2);
      
      const queryDuration = new Date() - startTime;
      vectorQueryDuration.add(queryDuration);
      
      // Track metadata query duration separately
      if (currentQueryUsesFilter) {
        metadataQueryDuration.add(queryDuration);
      }
      
      const success = res.status === 200;
      check(res, {
        [`[VU ${vuId}] vector query ${queryIdx+1} successful`]: (r) => success
      });
      
      errorRate.add(!success);
      successRate.add(success);
      
      if (!success) {
        console.log(`[VU ${vuId}] Query ${queryIdx+1} failed: ${res.status}`);
      }
      
      sleep(Math.random() * 2 + 0.5);
    }
  });
  
  console.log(`[VU ${vuId}] Load test iteration complete`);
  sleep(Math.random() * 2 + 1);
}
