import http from 'k6/http';
import { check, sleep, group } from 'k6';
import { Rate, Trend, Counter } from 'k6/metrics';
import { randomString } from 'https://jslib.k6.io/k6-utils/1.1.0/index.js';
import { SharedArray } from 'k6/data';
import { htmlReport } from "https://raw.githubusercontent.com/benc-uk/k6-reporter/main/dist/bundle.js";

// Declare variable to track if index is created
let indexCreated = false;

// Custom metrics specifically for upsert operations
const upsertDuration = new Trend('upsert_duration');
const upsertFailRate = new Rate('upsert_fail_rate');
const upsertRequestCount = new Counter('upsert_request_count');
const vectorsUpsertedCount = new Counter('vectors_upserted_count');
const indexCreationDuration = new Trend('index_creation_duration');
const concurrentUpsertGauge = new Counter('concurrent_upsert_gauge');
const successRate = new Rate('success_rate');
const concurrentUpsertCount = new Trend('concurrent_upsert_count');
const spikeUpsertDuration = new Trend('spike_upsert_duration');
const constantUpsertDuration = new Trend('constant_upsert_duration');

// Configuration via environment variables with defaults
const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_KEY = __ENV.API_KEY || 'your-default-api-key';
const API_PREFIX = __ENV.API_PREFIX || '/v1';
const INDEX_NAME_PREFIX = 'upsert-test-';

// Upsert control parameters
const UPSERTS_PER_MINUTE = parseInt(__ENV.UPSERTS_PER_MINUTE || '60'); // Default: 1 per second
const VECTORS_PER_BATCH = parseInt(__ENV.VECTORS_PER_BATCH || '100');  // Vectors per upsert request
const DIMENSION = parseInt(__ENV.DIMENSION || '384');
const VU_MAX = parseInt(__ENV.VU_MAX || '10');  // Max concurrent upsert requests
const INDEXED_VECTORS_PER_USER = parseInt(__ENV.INDEXED_VECTORS_PER_USER || '5000'); // Total vectors per index
const USE_EXPLICIT_VECTORS = __ENV.USE_EXPLICIT_VECTORS === 'true';  // Use explicit vectors instead of text

// Dynamic calculation for sleep time between requests to achieve target rate
const SLEEP_TIME = (60 / UPSERTS_PER_MINUTE); // in seconds

// Track active concurrent upserts and update metrics
function trackConcurrency() {
  // This function is called regularly to track concurrent VUs
  const activeVUs = Math.max(1, __VU || 1);
  concurrentUpsertCount.add(activeVUs);
}

// Setup interval for tracking if we're in the init context
if (typeof __VU === 'undefined') {
  setInterval(trackConcurrency, 1000);
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

// Generate vector data with either explicit vectors or text content
function generateVectorData(count, dimension, useExplicitVectors) {
  const data = [];
  const topics = ['AI', 'databases', 'vector search', 'machine learning', 'embeddings'];
  
  for (let i = 0; i < count; i++) {
    const item = {
      id: `vec-${i}-${randomString(6)}`,
      metadata: {
        timestamp: new Date().toISOString(),
        category: topics[i % topics.length],
        batch_number: Math.floor(i / VECTORS_PER_BATCH),
        priority: (i % 5) + 1,
        tags: [(i % 2 === 0) ? 'important' : 'standard', topics[i % topics.length]]
      }
    };
    
    if (useExplicitVectors) {
      // Generate explicit random vector
      item.vector = Array(dimension).fill(0).map(() => (Math.random() * 2 - 1));
    } else {
      // Generate text content
      item.contents = `Document ${i} about ${topics[i % topics.length]} with random content for embedding generation. This is batch ${Math.floor(i / VECTORS_PER_BATCH)}.`;
    }
    
    data.push(item);
  }
  return data;
}

// Create shared array of pregenerated vector data
const vectorData = new SharedArray('vector_data', function() {
  return generateVectorData(INDEXED_VECTORS_PER_USER, DIMENSION, USE_EXPLICIT_VECTORS);
});

export const options = {
  scenarios: {
    // Scenario 1: Constant Load - maintains steady upsert pressure
    constant_upserts: {
      executor: 'constant-vus',
      vus: Math.ceil(VU_MAX * 0.7), // Use 70% of VUs for constant load
      duration: '120s', // Run for 2 minutes
      tags: { type: 'constant_load' },
    },
    
    // Scenario 2: Concurrent Spikes - test how system handles sudden concurrent upserts
    concurrent_spikes: {
      executor: 'ramping-arrival-rate',
      startRate: 1,
      timeUnit: '2s',
      preAllocatedVUs: VU_MAX,
      maxVUs: VU_MAX * 2,
      stages: [
        { target: 1, duration: '10s' },        // Baseline
        { target: VU_MAX * 2, duration: '30s'}, // Concurrent upsert spike
        { target: 1, duration: '30s' },        // Recovery
        { target: VU_MAX * 3, duration: '20s'}, // Larger spike
        { target: 1, duration: '10s' },        // Back to baseline
      ],
      tags: { type: 'concurrent_spikes' },
    }
  },
  thresholds: {
    'upsert_duration': ['p(95)<5000'], // 95% of upserts should complete within 5s
    'upsert_fail_rate': ['rate<0.05'],  // Less than 5% failures
    'http_req_duration': ['p(95)<5000'],
  },
};

// Test setup - create indexes for each VU before starting test
export function setup() {
  console.log(`
Upsert Load Test Configuration:
-------------------------------
Base URL: ${BASE_URL}
Upsert Rate: ${UPSERTS_PER_MINUTE} upserts/minute
Vectors Per Batch: ${VECTORS_PER_BATCH}
Vector Dimension: ${DIMENSION}
Max Virtual Users: ${VU_MAX}
Using Explicit Vectors: ${USE_EXPLICIT_VECTORS}
-------------------------------
`);

  const headers = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
  };
  
  // Check service health before starting
  const healthUrl = `${BASE_URL}${API_PREFIX}/health`;
  const healthRes = http.get(healthUrl);
  
  if (healthRes.status !== 200) {
    throw new Error(`Service is not healthy! Status: ${healthRes.status}, Response: ${healthRes.body}`);
  }
  
  return {
    baseUrl: BASE_URL,
    apiKey: API_KEY,
    apiPrefix: API_PREFIX,
    headers: headers
  };
}

// Main test function
export default function(data) {
  const { baseUrl, apiPrefix, headers } = data;
  
  // Generate a unique index per VU
  const uniqueId = `${__VU}-${randomString(6)}`;
  const indexName = `${INDEX_NAME_PREFIX}${uniqueId}`;
  const indexKey = generateIndexKey();
  
  // Track scenario type for metrics
  const isSpike = __ITER > 0 || (__ENV.SCENARIO && __ENV.SCENARIO.includes('concurrent'));
  const scenarioTag = isSpike ? 'spike' : 'constant';
  
  group('Create Index', function() {
    // Only create the index once per VU
    if ((__ITER === 0 && !indexCreated) || (isSpike && __ITER % 10 === 0)) {
      const createIndexUrl = `${baseUrl}${apiPrefix}/indexes/create`;
      const createPayload = JSON.stringify({
        "index_name": indexName,
        "index_key": indexKey,
        "index_config": {
          "type": "ivfflat",
          "n_lists": 4,
          "metric": "euclidean",
          "dimension": DIMENSION
        }
      });
      
      let startTime = new Date();
      let res = http.post(createIndexUrl, createPayload, { 
        headers: headers,
        tags: { scenario: scenarioTag }
      });
      indexCreationDuration.add(new Date() - startTime);
      
      check(res, {
        'index creation successful': (r) => r.status === 200
      });
      
      if (res.status === 200) {
        console.log(`VU ${__VU}: Created index ${indexName}`);
        // Flag to avoid creating again
        indexCreated = true;
      } else {
        console.log(`VU ${__VU}: Failed to create index: ${res.status}, ${res.body}`);
      }
      
      // Give the system a moment to process the creation
      sleep(1);
    }
  });
  
  group('Upsert Vectors', function() {
    // Get a batch of vectors for this request
    const batchStart = (__ITER * VECTORS_PER_BATCH) % (INDEXED_VECTORS_PER_USER - VECTORS_PER_BATCH);
    const batchEnd = batchStart + VECTORS_PER_BATCH;
    const itemsToUpsert = vectorData.slice(batchStart, batchEnd);
    
    // Prepare upsert payload
    const upsertUrl = `${baseUrl}${apiPrefix}/vectors/upsert`;
    const upsertPayload = JSON.stringify({
      index_name: indexName,
      index_key: indexKey,
      items: itemsToUpsert
    });
    
    // Track concurrent upserts - increment counter
    concurrentUpsertGauge.add(1, { scenario: scenarioTag });
    
    // Perform upsert
    let startTime = new Date();
    let res = http.post(upsertUrl, upsertPayload, {
      headers: headers,
      timeout: '30s',
      tags: { 
        batch_size: VECTORS_PER_BATCH,
        vu: __VU,
        iteration: __ITER,
        scenario: scenarioTag
      }
    });
    const duration = new Date() - startTime;
    
    // Record metrics
    upsertDuration.add(duration, { scenario: scenarioTag });
    upsertRequestCount.add(1, { scenario: scenarioTag });
    upsertFailRate.add(res.status !== 200, { scenario: scenarioTag });
    successRate.add(res.status === 200, { scenario: scenarioTag });
    
    // Track number of vectors upserted
    if (res.status === 200) {
      vectorsUpsertedCount.add(VECTORS_PER_BATCH, { scenario: scenarioTag });
    }
    
    // Log detailed info for first few requests and any failures
    if (__ITER < 3 || res.status !== 200) {
      console.log(`VU ${__VU} Upsert ${__ITER+1} (${scenarioTag}): status=${res.status}, duration=${duration}ms, vectors=${VECTORS_PER_BATCH}`);
      if (res.status !== 200) {
        console.log(`Failed upsert response: ${res.body}`);
      }
    }
    
    // Check if upsert was successful
    check(res, {
      'upsert successful': (r) => r.status === 200,
      'upsert duration < 2s': (r) => duration < 2000,
    });
    
    // Done with this concurrent upsert - decrement counter
    concurrentUpsertGauge.add(-1, { scenario: scenarioTag });
    
    // Use different sleep strategies based on whether we're in constant or spike
    if (!isSpike) {
      // For constant load, control rate with sleep
      sleep(SLEEP_TIME);
    } else {
      // For spike tests, use smaller random sleeps
      sleep(Math.random() * 0.5 + 0.1);
    }
  });
}

// Define the HTML reporter output
export function handleSummary(data) {
  const now = new Date();
  const timestamp = `${now.getFullYear()}-${now.getMonth()+1}-${now.getDate()}_${now.getHours()}-${now.getMinutes()}`;
  
  return {
    [`upsert_benchmark_${timestamp}.html`]: htmlReport(data),
    stdout: textSummary(data, { indent: ' ', enableColors: true }),
  };
}

// Text summary for console output
function textSummary(data, options) {
  const upsertData = data.metrics.upsert_duration || {};
  const spikeData = data.metrics.spike_upsert_duration || {};
  const constantData = data.metrics.constant_upsert_duration || {};
  const failRate = data.metrics.upsert_fail_rate || {};
  const requestCount = data.metrics.upsert_request_count || {};
  const vectorCount = data.metrics.vectors_upserted_count || {};
  const concurrentCount = data.metrics.concurrent_upsert_count || {};
  
  const summary = [
    'UPSERT BENCHMARK SUMMARY',
    '==============================================',
    `Date: ${new Date().toISOString()}`,
    `Duration: ${data.state.testRunDurationMs / 1000} seconds`,
    `Target Upsert Rate: ${UPSERTS_PER_MINUTE} per minute`,
    `Vectors Per Batch: ${VECTORS_PER_BATCH}`,
    `Max Virtual Users: ${VU_MAX}`,
    '----------------------------------------------',
    `Total Upsert Requests: ${requestCount.count || 0}`,
    `Actual Upsert Rate: ${(requestCount.count || 0) / (data.state.testRunDurationMs / 60000)} per minute`,
    `Total Vectors Upserted: ${vectorCount.count || 0}`,
    `Upsert Failure Rate: ${((failRate.true || 0) / (failRate.count || 1) * 100).toFixed(2)}%`,
    `Concurrent Upserts: avg=${concurrentCount.avg?.toFixed(2) || 'N/A'}, max=${concurrentCount.max || 'N/A'}`,
    '----------------------------------------------',
    'Overall Upsert Duration (ms):',
    `  Avg: ${upsertData.avg !== undefined ? upsertData.avg.toFixed(2) : 'N/A'}`,
    `  Min: ${upsertData.min !== undefined ? upsertData.min.toFixed(2) : 'N/A'}`,
    `  Max: ${upsertData.max !== undefined ? upsertData.max.toFixed(2) : 'N/A'}`,
    `  p(50): ${upsertData.med !== undefined ? upsertData.med.toFixed(2) : 'N/A'}`,
    `  p(90): ${upsertData['p(90)'] !== undefined ? upsertData['p(90)'].toFixed(2) : 'N/A'}`,
    `  p(95): ${upsertData['p(95)'] !== undefined ? upsertData['p(95)'].toFixed(2) : 'N/A'}`,
    '----------------------------------------------',
    'Constant Load Upsert Duration (ms):',
    `  Avg: ${constantData.avg !== undefined ? constantData.avg.toFixed(2) : 'N/A'}`,
    `  p(95): ${constantData['p(95)'] !== undefined ? constantData['p(95)'].toFixed(2) : 'N/A'}`,
    '----------------------------------------------',
    'Spike Test Upsert Duration (ms):',
    `  Avg: ${spikeData.avg !== undefined ? spikeData.avg.toFixed(2) : 'N/A'}`,
    `  p(95): ${spikeData['p(95)'] !== undefined ? spikeData['p(95)'].toFixed(2) : 'N/A'}`,
    '==============================================',
  ].join('\n');
  
  return summary;
}