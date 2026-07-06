from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
from collections import deque
import time
import uuid

app = FastAPI()

EMAIL = "23f1003060@ds.study.iitm.ac.in"

startup_time = time.time()

http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP Requests"
)

logs = deque(maxlen=1000)


@app.middleware("http")
async def log_requests(request: Request, call_next):

    http_requests_total.inc()

    request_id = str(uuid.uuid4())

    log = {
        "level": "INFO",
        "ts": time.time(),
        "path": request.url.path,
        "request_id": request_id
    }

    logs.append(log)

    response = await call_next(request)

    return response


@app.get("/work")
def work(n: int):

    for _ in range(n):
        pass

    return {
        "email": EMAIL,
        "done": n
    }


@app.get("/metrics")
def metrics():

    return PlainTextResponse(
        generate_latest().decode(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/healthz")
def health():

    return {
        "status": "ok",
        "uptime_s": time.time() - startup_time
    }


@app.get("/logs/tail")
def tail(limit: int = 10):

    return list(logs)[-limit:]