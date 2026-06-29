from fastapi import FastAPI, Request, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import time
import uuid
from typing import List

app = FastAPI(
    title="Descriptive Statistics API",
    description="Computes count, sum, min, max, mean for comma-separated integers. Strict CORS and custom headers."
)

# === CONFIG ===
ALLOWED_ORIGIN = "https://dash-el2i1l.example.com"
EMAIL = "gangulysiddhartha22@gmail.com"   # ← Change ONLY if your logged-in platform email is different

# === MIDDLEWARE (ORDER IS CRITICAL) ===
# Custom middleware FIRST → wraps everything (including CORS preflights)
@app.middleware("http")
async def add_custom_headers(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.perf_counter()
    
    response = await call_next(request)
    
    process_time = time.perf_counter() - start_time
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time"] = f"{process_time:.6f}"
    
    return response

# CORS middleware SECOND (inner) — strict per-origin only
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOWED_ORIGIN],
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

# === ENDPOINT ===
@app.get("/stats")
async def get_stats(
    values: str = Query(
        ..., 
        description="Comma-separated integers (e.g. 1,2,3,4,-5)",
        example="1,2,3,4,5"
    )
):
    try:
        parts = [v.strip() for v in values.split(",") if v.strip()]
        if not parts:
            raise ValueError("No valid numbers provided")
        nums: List[int] = [int(part) for part in parts]
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid values: {e}")

    if not nums:
        raise HTTPException(status_code=400, detail="At least one integer required")

    count = len(nums)
    total = sum(nums)
    minimum = min(nums)
    maximum = max(nums)
    mean = total / count

    return {
        "email": EMAIL,
        "count": count,
        "sum": total,
        "min": minimum,
        "max": maximum,
        "mean": mean
    }

@app.get("/")
async def root():
    return {"message": "Stats service running", "endpoint": "/stats?values=1,2,3"}
