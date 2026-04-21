import redis
import time
import os
import signal
import logging
import sys

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Environment variables
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_QUEUE = os.getenv("REDIS_QUEUE", "jobs")

# Graceful shutdown flag
running = True

def shutdown_handler(signum, frame):
    global running
    logger.info("Shutdown signal received. Stopping worker...")
    running = False

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

# Redis connection with retry
def connect_redis():
    while True:
        try:
            client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                decode_responses=True
            )
            client.ping()
            logger.info("Connected to Redis")
            return client
        except redis.RedisError as e:
            logger.error(f"Redis connection failed: {e}. Retrying in 5s...")
            time.sleep(5)

r = connect_redis()

def process_job(job_id):
    try:
        logger.info(f"Processing job {job_id}")
        time.sleep(2)  # simulate work

        r.hset(f"job:{job_id}", mapping={"status": "completed"})
        logger.info(f"Completed job {job_id}")

    except Exception as e:
        logger.error(f"Failed job {job_id}: {e}")
        r.hset(f"job:{job_id}", mapping={"status": "failed"})

# Main loop
while running:
    try:
        job = r.brpop(REDIS_QUEUE, timeout=5)

        if job:
            _, job_id = job
            process_job(job_id)

    except redis.RedisError as e:
        logger.error(f"Redis error: {e}")
        time.sleep(5)

logger.info("Worker stopped cleanly")
sys.exit(0)