from fastapi import FastAPI, Request
from fastapi.responses import Response
from prometheus_client import Counter, Histogram, CONTENT_TYPE_LATEST, generate_latest
import time

app = FastAPI(title="TP4 GitOps demo")
REQUESTS = Counter("tp4_http_requests_total", "Requests served by the TP4 application", ["path", "method", "status"])
DURATION = Histogram("tp4_http_request_duration_seconds", "HTTP request duration", ["path"])

@app.middleware("http")
async def collect_metrics(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)
    started = time.monotonic()
    response = await call_next(request)
    path = request.url.path if request.url.path in ("/", "/health") else "/other"
    REQUESTS.labels(path=path, method=request.method, status=str(response.status_code)).inc()
    DURATION.labels(path=path).observe(time.monotonic() - started)
    return response

@app.get("/")
def home():
    return {"message": "TP4 GitOps / ArgoCD / Observability", "version": "v1"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/metrics")
def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
