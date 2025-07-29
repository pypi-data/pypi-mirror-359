import http from 'k6/http';
import { check, sleep } from 'k6';
import { Counter, Rate, Trend, Gauge } from 'k6/metrics';
import exec from 'k6/execution';
import { textSummary } from 'https://jslib.k6.io/k6-summary/0.0.1/index.js';

const BASE_URL = __ENV.BASE_URL || 'http://localhost:8000';
const API_KEY = __ENV.API_KEY || 'your-api-key';
const API_PREFIX = __ENV.API_PREFIX || '/v1';
const VU_MAX = parseInt(__ENV.VU_MAX || '10');
const DURATION = __ENV.DURATION || '10s';
const RAMP_UP = __ENV.RAMP_UP || '2s';
const RAMP_DOWN = __ENV.RAMP_DOWN || '30s';
const INDEX_NAME_PREFIX = 'k6-test-index-';
const TEST_MODE = __ENV.TEST_MODE || 'standard';
const TARGET_UPSERTS_PER_MINUTE = parseInt(__ENV.TARGET_UPSERTS_PER_MINUTE || '60');
const BATCH_SIZE = parseInt(__ENV.BATCH_SIZE || '100');

const errorRate = new Rate('error_rate');
const successRate = new Rate('success_rate');
const indexCreationDuration = new Trend('index_creation_duration');
const vectorUpsertDuration = new Trend('vector_upsert_duration');
const vectorQueryDuration = new Trend('vector_query_duration');
const trainingDuration = new Trend('training_duration');
const trainingSuccessRate = new Rate('training_success_rate');
const totalVectorsUpserted = new Counter('total_vectors_upserted');
const upsertCallCount = new Counter('upsert_calls_total');
const activeUpsertGauge = new Gauge('active_upserts');

const testScenarios = {
    standard: {
        vectorsPerIndex: 20000,
        trainingDelay: 10,
        queryCount: 2
    },
    advanced: {
        vectorsPerIndex: 30000,
        trainingDelay: 15,
        queryCount: 5
    }
};

const activeScenario = testScenarios[TEST_MODE] || testScenarios.standard;
let manualTotalVectorsUpserted = 0;

export const options = {
    scenarios: {
    
        concurrent_phase: {
            executor: 'ramping-vus',
            startTime: '5s',
            startVUs: 0,
            stages: [
                { duration: RAMP_UP, target: VU_MAX },
                { duration: DURATION, target: VU_MAX },
                { duration: RAMP_DOWN, target: 0 }
            ],
            gracefulRampDown: '5s',
            exec: 'concurrentPhase'
        }
    },
    thresholds: {
        http_req_duration: ['p(95)<10000'],
        success_rate: ['rate>0.7']
    }
};

function getHeaders() {
    return {
        'X-API-Key': API_KEY,
        'Content-Type': 'application/json'
    };
}

function generateVector(dimension) {
    const vector = [];
    for (let i = 0; i < dimension; i++) {
        vector.push((Math.random() * 2) - 1);
    }
    return vector;
}

function createIndex(indexName, indexKey) {
    const headers = getHeaders();
    const createIndexUrl = `${BASE_URL}${API_PREFIX}/indexes/create`;
    const createPayload = JSON.stringify({
        index_name: indexName,
        index_key: indexKey,
        index_config: {
            type: "ivfflat",
            n_lists: 4,
            metric: "euclidean",
            dimension: 384
        }
    });

    console.log(`[CREATE] Creating index: ${indexName}`);
    let startTime = new Date();
    let res = http.post(createIndexUrl, createPayload, { headers: headers });
    indexCreationDuration.add(new Date() - startTime);

    if (res.status === 200 || (res.status === 400 && res.body.includes("already exists"))) {
        console.log(`[CREATE] Index ${indexName} created or already exists.`);
        return true;
    } else {
        console.log(`[CREATE] Failed to create index ${indexName}: ${res.status}, ${res.body}`);
        return false;
    }
}

function upsertVectors(indexName, indexKey, batchId, batchSize) {
    const headers = getHeaders();
    const upsertUrl = `${BASE_URL}${API_PREFIX}/vectors/upsert`;

    activeUpsertGauge.add(1);

    const itemsToUpsert = [];
    for (let i = 0; i < batchSize; i++) {
        itemsToUpsert.push({
            id: `gen-${batchId}-${i}-${Date.now()}`,
            vector: generateVector(384),
            metadata: {
                timestamp: new Date().toISOString(),
                batch_id: batchId
            }
        });
    }

    const upsertPayload = JSON.stringify({
        index_name: indexName,
        index_key: indexKey,
        items: itemsToUpsert
    });

    let startTime = new Date();
    let res = http.post(upsertUrl, upsertPayload, {
        headers: headers,
        timeout: '5s'
    });
    vectorUpsertDuration.add(new Date() - startTime);

    const success = res.status === 200;

    check(res, {
        'upsert success': () => success
    });

    if (success) {
        totalVectorsUpserted.add(batchSize);
        upsertCallCount.add(1); 
        console.log(`[UPSERT] Inserted batch ${batchId} (${batchSize} vectors)`);
    } else {
        console.log(`[UPSERT] Failed batch ${batchId}: ${res.status}, ${res.body}`);
    }

    activeUpsertGauge.add(-1);
    return success ? itemsToUpsert.length : 0;
}

function trainIndex(indexName, indexKey) {
    const headers = getHeaders();
    const trainUrl = `${BASE_URL}${API_PREFIX}/indexes/train`;
    const trainPayload = JSON.stringify({
        index_name: indexName,
        index_key: indexKey,
        batch_size: 32,
        max_iters: 5,
        tolerance: 1e-3
    });

    console.log(`[TRAIN] Training index: ${indexName}`);
    let startTime = new Date();
    let res = http.post(trainUrl, trainPayload, {
        headers: headers,
        timeout: '60s'
    });
    trainingDuration.add(new Date() - startTime);

    const success = res.status === 200;
    check(res, { '[TRAIN] Training successful': () => success });

    if (success) {
        console.log(`[TRAIN] Training completed for index ${indexName}`);
    } else {
        console.log(`[TRAIN] Training failed: ${res.status}, ${res.body}`);
    }

    trainingSuccessRate.add(success);
    return success;
}

function runQuery(indexName, indexKey) {
    const headers = getHeaders();
    const queryUrl = `${BASE_URL}${API_PREFIX}/vectors/query`;

    const queryPayload = {
        index_name: indexName,
        index_key: indexKey,
        query_vectors: [generateVector(384)],
        top_k: 5,
        include: ['distances', 'metadata']
    };

    let startTime = new Date();
    
    let res = http.post(queryUrl, JSON.stringify(queryPayload), { headers: headers });
    vectorQueryDuration.add(new Date() - startTime);

    const success = res.status === 200;
    check(res, { '[QUERY] Query successful': () => success });

    if (!success) {
        console.log(`[QUERY] Failed: ${res.status}, ${res.body}`);
    }

    return success;
}

function calculateSleepTime() {
    const vus = Math.max(1, exec.instance.vusActive);
    const sleepTime = (60 / Math.max(1, TARGET_UPSERTS_PER_MINUTE)) * vus;
    return Math.max(0.1, sleepTime);
}


export function setup() {
    const INDEX_NAME = `${INDEX_NAME_PREFIX}${Date.now()}`;
    const INDEX_KEY = (() => {
        let hexKey = '';
        const hexChars = '0123456789abcdef';
        for (let i = 0; i < 64; i++) {
            hexKey += hexChars.charAt(Math.floor(Math.random() * hexChars.length));
        }
        return hexKey;
    })();
    console.log(`[SETUP] Starting setup phase: INDEX_KEY: ${INDEX_KEY} INDEX_NAME: ${INDEX_NAME}`);

    const created = createIndex(INDEX_NAME, INDEX_KEY);
    if (!created) return;

    const initialVectors = Math.max(1000, Math.ceil(activeScenario.vectorsPerIndex * 0.1));
    const batchesNeeded = Math.ceil(initialVectors / BATCH_SIZE);
    let totalInserted = 0;

    for (let i = 0; i < batchesNeeded; i++) {
        const batchId = `setup-batch-${i}`;
        const inserted = upsertVectors(INDEX_NAME, INDEX_KEY, batchId, BATCH_SIZE);
        totalInserted += inserted;
        console.log(`[SETUP] Inserted ${totalInserted}/${initialVectors}`);
        sleep(1);
    }

    sleep(activeScenario.trainingDelay);
    trainIndex(INDEX_NAME, INDEX_KEY);
    runQuery(INDEX_NAME, INDEX_KEY);

    console.log(`[SETUP] Setup complete. Index: ${INDEX_NAME}`);
    return {
        indexName: INDEX_NAME,
        indexKey: INDEX_KEY
    };
}

export function concurrentPhase(setupData) {
    const vuId = __VU;
    const INDEX_NAME = setupData.indexName;
    const INDEX_KEY = setupData.indexKey;

    console.log(`[DEBUG][VU ${vuId}] Starting concurrent phase. INDEX_KEY: ${INDEX_KEY} INDEX_NAME: ${INDEX_NAME}`);
    let batchCounter = 0;
    let localVectorsUpserted = 0;

    for (let i = 0; i < 10; i++) {
        console.log(`[DEBUG][VU ${vuId}] Iteration ${batchCounter}`);

        const batchId = `vu${vuId}-batch-${batchCounter}`;
        const inserted = upsertVectors(INDEX_NAME, INDEX_KEY, batchId, BATCH_SIZE);
        localVectorsUpserted += inserted;

        if (batchCounter % 5 === 0) {
            console.log(`[DEBUG][VU ${vuId}] Total upserts so far: ${localVectorsUpserted}`);
        }

        // if (batchCounter % 10 === 0) {
        //     runQuery(INDEX_NAME, INDEX_KEY);
        // }

        batchCounter++;
        sleep(calculateSleepTime());
    }
    sleep(6);
    return { upserts: localVectorsUpserted };
}


export function teardown(setupData) {
    const { indexName, indexKey } = setupData;
    const headers = getHeaders();

    const res = http.post(`${BASE_URL}${API_PREFIX}/vectors/num_vectors`, JSON.stringify({
        index_name: indexName,
        index_key: indexKey
    }), { headers });

    if (res.status === 200) {
        const result = JSON.parse(res.body).result;
        console.log(`[VERIFY] Vectors reported in index: ${result}`);
        return { vectors_in_index: result };
    } else {
        console.error(`[ERROR] Failed to get /num_vectors: ${res.status}, ${res.body}`);
        return { vectors_in_index: null };
    }
}



export function handleSummary(data, teardownData) {
    console.log('teardownData:', teardownData);  // debug print

    const actualUpserts = (data.metrics['total_vectors_upserted'] && data.metrics['total_vectors_upserted'].values && data.metrics['total_vectors_upserted'].values.count) || 0;
    const backendCount = teardownData && teardownData.vectors_in_index;

    let backendStatus = '';

    if (backendCount !== null && !isNaN(backendCount)) {
        const delta = Math.abs(actualUpserts - backendCount);
        const match = delta <= 100;

        backendStatus = match
            ? `✅ Backend index count matches upserts: ${backendCount} vectors (Δ=${delta})`
            : `❌ Backend mismatch: index has ${backendCount}, upserts counted ${actualUpserts} (Δ=${delta})`;
    } else {
        backendStatus = `⚠️ could not verify but expecting: ${actualUpserts}`;
    }

    console.log('\n' + '='.repeat(60));
    console.log(backendStatus);
    console.log('='.repeat(60) + '\n');

    return {
        stdout: textSummary(data, { indent: ' ', enableColors: true }),
        'summary.json': JSON.stringify(data, null, 2)
    };
}