from fastapi import FastAPI, HTTPException
import redis
import uuid
import os
import logging

app = FastAPI()

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_QUEUE = os.getenv("REDIS_QUEUE", "jobs")

# Redis connection with error handling
try:
    r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
    r.ping()
    logger.info("Connected to Redis")
except redis.RedisError as e:
    logger.error(f"Redis connection failed: {e}")
    raise

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/jobs")
def create_job():
    job_id = str(uuid.uuid4())

    try:
        r.lpush(REDIS_QUEUE, job_id)
        r.hset(f"job:{job_id}", mapping={"status": "queued"})
        logger.info(f"Job created: {job_id}")
    except redis.RedisError as e:
        logger.error(f"Failed to create job: {e}")
        raise HTTPException(status_code=500, detail="Queue error")

    return {"job_id": job_id}

@app.get("/jobs/{job_id}")
def get_job(job_id: str):
    try:
        status = r.hget(f"job:{job_id}", "status")
    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")
        raise HTTPException(status_code=500, detail="Redis error")

    if not status:
        raise HTTPException(status_code=404, detail="Job not found")

    return {"job_id": job_id, "status": status}
