# CyborgDB Service

![PyPI - Version](https://img.shields.io/pypi/v/cyborgdb_service)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/cyborgdb_service)

A FastAPI-based REST API wrapper for [CyborgDB](https://docs.cyborg.co), providing Confidential Vector DB capabilities over HTTP. It enables you to ingest & search vectors emeddings in a privacy-preserving manner, without revealing the contents of the vectors themselves. CyborgDB works with existing DBs (e.g., Postgres, Redis) and enables you to add, query and retrieve vector embeddings with transparent end-to-end encryption.

## Features

- **End-to-End Encryption**: Vector embeddings remain encrypted throughout their lifecycle, including at search time
- **Zero-Trust Design**: Novel architecture keeps confidential inference data secure
- **High Performance**: GPU-accelerated indexing and retrieval with CUDA support
- **Familiar API**: Easy integration with existing AI workflows
- **Multiple Backing Stores**: Works with PostgreSQL, Redis, and in-memory storage
- **Cloud Ready**: Supports AWS RDS, AWS ElastiCache, Azure Database for PostgreSQL, Azure Cache for Redis, Google Cloud SQL, and Google Cloud Memorystore

## Getting Started

### Prerequisites

- Python 3.11+
- Conda/Mamba environment manager

### Installation

1. Install `cyborgdb-service` from `pip`
   ```bash
   pip install cyborgdb-service
   ```

2. Set environment variables
   ```bash
   export CYBORGDB_API_KEY=your_api_key_here
   export CYBORGDB_DB_TYPE='redis|postgres'
   export CYBORGDB_CONNECTION_STRING=your_connection_string_here
   ```
      For connection string examples run `cyborgdb-service --help`

2. Run the server
   ```bash
   cyborgdb-service
   ```


### API Key Configuration

You need to provide your API key using **any** of these methods:

#### Method 1: Environment Variable (Easiest)
```bash
export CYBORGDB_API_KEY=your_api_key_here
docker-compose up
```

#### Method 2: .env File (Most Convenient)
Create a `.env` file in the project root:
```
CYBORGDB_API_KEY=your_api_key_here
```
Then run:
```bash
docker-compose up
```

#### Method 3: Inline with Docker Compose
```bash
CYBORGDB_API_KEY=your_api_key_here docker-compose up
```

### Build from Source

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/cyborgdb-service.git
   cd cyborgdb-service
   ```

2. Create and activate the conda environment
   ```bash
   conda env create -f environment.yml
   conda activate cyborgdb-service
   ```

3. Attach a git tag based on the version of core you want installed
   ```bash
   git tag v0.11.0-dev
   ```

4. Install `cyborgdb-service` as a local pip package
    ```bash
    pip install -e .
    ```

5. Run the server
   ```bash
   cyborgdb-service
   ```

6. Visit the API documentation at `http://localhost:8000/v1/docs`

### Running Tests

```bash
pytest --cov=cyborgdb_service
```

## Documentation

For more information on API endpoints and usage, see the [API Documentation](docs/api.md).