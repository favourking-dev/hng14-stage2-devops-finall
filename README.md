# hng14-stage2-devops
# HNG14 Stage 2 DevOps Project

## Overview

This project is a multi-service job processing system consisting of:

* **Frontend (Node.js)** – User interface for submitting and tracking jobs
* **API (FastAPI)** – Handles job creation and status retrieval
* **Worker (Python)** – Processes jobs from a queue
* **Redis** – Message queue shared between API and Worker

All services are containerized using Docker and orchestrated with Docker Compose.

---

##  Prerequisites

Ensure the following are installed on your machine:

* [Docker Desktop](https://www.docker.com/products/docker-desktop/) (with WSL2 enabled on Windows)
* Git
* A modern web browser (Chrome, Edge, etc.)

Verify installation:

```bash
docker --version
docker compose version
```

---

##  Clone the Repository

```bash
git clone https://github.com/favourking-dev/hng14-stage2-devops.git
cd hng14-stage2-devops
```

---

##  Start the Application

Build and start all services:

```bash
docker compose up --build
```

---

##  Access the Application

Open your browser and go to:

```text
http://localhost:3000
```

---

##  How to Use

1. Click **"Submit New Job"**
2. A job ID will be generated
3. Wait a few seconds
4. Status will update to:

```text
completed
```

---

## ✅ What a Successful Startup Looks Like

When running `docker compose up`, you should see:

* Redis:

  ```
  Ready to accept connections
  ```

* API:

  ```
  Uvicorn running on http://0.0.0.0:8000
  ```

* Worker:

  ```
  Connected to Redis
  ```

* Frontend:

  ```
  Frontend running on port 3000
  ```

---

## ⏹️ Stop the Application

Press:

```text
Ctrl + C
```

Then clean up:

```bash
docker compose down
```

---

## 🔄 Restart the Application

```bash
docker compose up
```

---

## 🐳 Services Overview

| Service  | Port | Description     |
| -------- | ---- | --------------- |
| Frontend | 3000 | User interface  |
| API      | 8000 | Backend service |
| Redis    | 6379 | Queue storage   |

---

## ⚙️ CI/CD Pipeline

This project includes a GitHub Actions pipeline with the following stages:

1. Lint
2. Test
3. Build
4. Security Scan (Trivy)
5. Integration Test
6. Deploy (mock)

The pipeline runs automatically on every push to the `main` branch.

---

## 📄 Notes

* No `.env` files are included (per project rules)
* No secrets are hardcoded
* All services communicate via Docker network

---

## 🏁 Summary

This project demonstrates:

* Containerization using Docker
* Multi-service orchestration with Docker Compose
* Asynchronous job processing with Redis
* CI/CD automation using GitHub Actions

---
