# Latency Inference Engine

This project implements a high-performance machine learning inference engine designed to demonstrate and validate the throughput differences between **Real-Time (Online)** and **Batch (Offline)** processing strategies.

Built with **FastAPI** and **Scikit-Learn**, the system serves a Fake News Detection model under high-concurrency conditions. It addresses the scalability challenges inherent in serving ML models by implementing vectorization techniques to minimize CPU overhead and network latency.

## System Architecture

The system exposes two distinct inference strategies. The following flowchart illustrates the data flow for both endpoints:

```mermaid
graph TD
    A["Client / Load Balancer"]
    
    subgraph "Inference Server (FastAPI)"
        B{Endpoint Selection}
        A --> B
        
        %% Real-Time Path
        B -- "POST /predict (Single Item)" --> C["Real-Time Handler"]
        C --> D["Vectorize Single Text"]
        D --> E["Model Prediction"]
        E --> F["Return JSON"]
        
        %% Batch Path
        B -- "POST /predict_batch (List of Items)" --> G["Batch Handler"]
        G --> H["Vectorize List (SIMD/Parallel)"]
        H --> I["Model Prediction (Batch)"]
        I --> J["Return JSON Array"]
    end

```

## Key Features

* **Global Model State**: Implements a "Load Once" pattern where the ML model and vectorizer are loaded into memory on application startup, eliminating disk I/O latency during request processing.
* **Vectorized Batch Processing**: The batch endpoint utilizes Scikit-Learn's internal vectorization optimization to transform multiple text inputs simultaneously, leveraging CPU SIMD instructions rather than iterative looping.
* **Asynchronous Concurrency**: Built on Uvicorn (ASGI) to handle non-blocking concurrent requests efficiently.

## Performance Benchmarks

A load test was conducted using **Locust** with **100 concurrent users** to simulate high-traffic conditions. The results compare the throughput of standard single-item inference versus batch inference.

| Metric | Real-Time Endpoint (`/predict`) | Batch Endpoint (`/predict_batch`) | Performance Delta |
| --- | --- | --- | --- |
| **Concurrency** | 100 Users | 100 Users | - |
| **Requests Per Second** | 5.1 RPS | 5.6 RPS | +9.8% |
| **Items Processed/Sec** | **5.1 items/s** | **28.0 items/s** | **~5.5x Throughput Increase** |
| **Avg. Latency** | ~2035 ms | ~2038 ms | Negligible impact |

**Analysis**: While the request rate (RPS) remained similar due to network bottlenecks, the **effective throughput** (items classified per second) increased by roughly 550% when using the batch strategy. This validates that batching significantly reduces the per-item computational overhead.

## Technical Stack

* **Framework**: FastAPI
* **Server**: Uvicorn
* **ML Libraries**: Scikit-Learn, Joblib, Pandas
* **Testing**: Locust (Load Testing)

## Installation and Usage

### 1. Prerequisites

Ensure Python 3.8+ is installed.

```bash
pip install fastapi uvicorn scikit-learn joblib locust

```

### 2. Running the Server

Start the inference engine locally:

```bash
uvicorn main:app --reload

```

The API will be available at `http://127.0.0.1:8000`.

### 3. Running Stress Tests

To replicate the benchmark results, start the Locust swarm:

```bash
locust -f locustfile.py

```

Access the Locust dashboard at `http://localhost:8089` and configure the test for 100 users.

## Project Structure

* `main.py`: The application entry point containing API definitions and model loading logic.
* `locustfile.py`: Load testing script defining user behaviors for single and batch requests.
* `best_fake_news_model.pkl`: Serialized Machine Learning model.
* `tfidf_vectorizer_best.pkl`: Serialized TF-IDF vectorizer.

