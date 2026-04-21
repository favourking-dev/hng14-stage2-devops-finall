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
