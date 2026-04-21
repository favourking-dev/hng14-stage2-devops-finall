# FIXES.md

## File: api/main.py

---

### Line 6

**Original Code:**

```python
r = redis.Redis(host="localhost", port=6379)
```

**Problem:**

* Redis connection is hardcoded to `localhost`
* Breaks in containerized environments where services communicate via service names
* Not configurable across environments (dev/staging/prod)
* Violates requirement: no hardcoded configuration

**Fix:**
Replaced with environment variables and added connection validation

**Updated Code:**

```python
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
```

---

### Line 6 (additional issue)

**Problem:**

* No connection validation (app may start even if Redis is unavailable)

**Fix:**
Added `r.ping()` with error handling

**Updated Code:**

```python
try:
    r.ping()
except redis.RedisError as e:
    raise
```

---

### Line 9–13 (`create_job` function)

**Original Code:**

```python
r.lpush("job", job_id)
r.hset(f"job:{job_id}", "status", "queued")
```

**Problems:**

* Queue name `"job"` is hardcoded and non-descriptive
* No error handling for Redis operations
* No logging for job creation
* No configurability

**Fix:**

* Introduced `REDIS_QUEUE` environment variable
* Wrapped operations in try/except
* Added logging

**Updated Code:**

```python
r.lpush(REDIS_QUEUE, job_id)
r.hset(f"job:{job_id}", mapping={"status": "queued"})
```

---

### Line 9–13 (missing observability)

**Problem:**

* No logging for job creation events

**Fix:**
Added logging:

```python
logger.info(f"Job created: {job_id}")
```

---

### Line 15–20 (`get_job` function)

**Original Code:**

```python
if not status:
    return {"error": "not found"}
```

**Problems:**

* Returns HTTP 200 for missing resource
* Not REST-compliant
* No structured error handling

**Fix:**
Replaced with FastAPI `HTTPException`

**Updated Code:**

```python
if not status:
    raise HTTPException(status_code=404, detail="Job not found")
```

---

### Line 15–20 (Redis call)

**Problem:**

* No error handling around Redis access

**Fix:**
Wrapped in try/except:

```python
try:
    status = r.hget(f"job:{job_id}", "status")
except redis.RedisError:
    raise HTTPException(status_code=500, detail="Redis error")
```

---

### Missing Feature (global)

**Problem:**

* No health check endpoint

**Why it's bad:**

* Required for Kubernetes liveness/readiness probes
* Prevents proper monitoring and orchestration

**Fix:**
Added `/health` endpoint:

```python
@app.get("/health")
def health():
    return {"status": "ok"}
```

---

### Missing Feature (global)

**Problem:**

* No logging configured

**Why it's bad:**

* No observability
* Difficult to debug production issues

**Fix:**
Added logging setup:

```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
```

---

### Improvement (Redis decoding)

**Problem:**

* Original code required `.decode()` on Redis response

**Fix:**
Enabled automatic decoding:

```python
decode_responses=True
```

**Benefit:**

* Cleaner code
* Avoids manual `.decode()` calls

## File: worker/main.py

---

### Line 5

**Original Code:**

```python
r = redis.Redis(host="localhost", port=6379)
```

**Problem:**

* Hardcoded Redis configuration
* Not suitable for containerized environments

**Fix:**
Replaced with environment variables and retry connection logic

---

### Line 11

**Original Code:**

```python
while True:
```

**Problem:**

* Infinite loop without graceful shutdown
* Cannot handle termination signals

**Fix:**
Introduced `running` flag and signal handlers (SIGINT, SIGTERM)

---

### Line 12

**Original Code:**

```python
job = r.brpop("job", timeout=5)
```

**Problem:**

* Hardcoded queue name
* No error handling

**Fix:**
Replaced with configurable `REDIS_QUEUE` and wrapped in try/except

---

### Line 7–10 (`process_job`)

**Original Code:**

```python
print(f"Processing job {job_id}")
time.sleep(2)
r.hset(f"job:{job_id}", "status", "completed")
print(f"Done: {job_id}")
```

**Problems:**

* Uses `print` instead of logging
* No error handling
* No failure state update

**Fix:**

* Replaced `print` with logging
* Added try/except
* Added failure status handling

---

### Line 10

**Problem:**

* No handling of failed jobs

**Fix:**
Added:

```python
r.hset(f"job:{job_id}", mapping={"status": "failed"})
```

---

### Line 12–15

**Problem:**

* No retry/backoff on Redis failure

**Fix:**
Wrapped loop in try/except and added sleep backoff

---

### Line 14

**Original Code:**

```python
process_job(job_id.decode())
```

**Problem:**

* Manual decoding required due to Redis config

**Fix:**
Enabled `decode_responses=True` in Redis client

---

### Missing Feature (global)

**Problem:**

* No logging system

**Fix:**
Added Python logging configuration

---

### Missing Feature (global)

**Problem:**

* No graceful shutdown support

**Fix:**
Added signal handlers and controlled loop exit

## File: frontend/app.js

---

### Line 6

**Original Code:**

```js
const API_URL = "http://localhost:8000";
```

**Problem:**

* Hardcoded API URL
* Breaks in containerized environments

**Fix:**
Replaced with environment variable:

```js
const API_URL = process.env.API_URL || "http://localhost:8000";
```

---

### Line 24

**Original Code:**

```js
app.listen(3000, () => {
```

**Problem:**

* Hardcoded port

**Fix:**
Replaced with environment variable:

```js
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
```

---

### Line 11–20

**Problem:**

* No timeout on HTTP requests

**Fix:**
Introduced axios instance with timeout:

```js
const apiClient = axios.create({
  baseURL: API_URL,
  timeout: 5000
});
```

---

### Line 13–18 (`/submit` endpoint)

**Problem:**

* Generic error handling
* No logging

**Fix:**
Added error logging and clearer response

---

### Line 20–26 (`/status` endpoint)

**Problem:**

* Generic error handling
* No logging

**Fix:**
Added logging and improved error messages

---

### Missing Feature (global)

**Problem:**

* No health check endpoint

**Fix:**
Added `/health` route

---

### Missing Feature (global)

**Problem:**

* No structured request client

**Fix:**
Introduced reusable axios instance

## Redis Configuration Fix

### File: api/main.py & worker/worker.py

### Problem:
Used "localhost" for Redis connection, which fails in Docker containers

### Fix:
Replaced with environment-based configuration:
- REDIS_HOST=redis
- Used Docker service name for networking
