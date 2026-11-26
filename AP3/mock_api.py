"""NorthMart mock orders API (AP2).

Run from the root of your AP2 directory:
    uvicorn mock_api:app --port 8000
Needs fastapi, uvicorn and duckdb, and the file data/source/northmart_api_feed.parquet.
"""
import random
from datetime import date as Date

import duckdb
from fastapi import FastAPI, HTTPException

FEED = "data/source/northmart_api_feed.parquet"
PAGE_SIZE = 100

app = FastAPI(title="NorthMart orders API")
con = duckdb.connect()
con.execute(f"CREATE TABLE feed AS SELECT * FROM read_parquet('{FEED}')")


@app.get("/orders")
def orders(date: str, page: int = 1):
    try:
        Date.fromisoformat(date)
    except ValueError:
        raise HTTPException(400, "date must be YYYY-MM-DD")
    if page < 1:
        raise HTTPException(400, "page starts at 1")
    if random.random() < 0.1:                      # the service is sometimes unavailable
        raise HTTPException(503, "temporarily unavailable")

    cur = con.cursor()
    cur.execute("SELECT * EXCLUDE (seq, day) FROM feed WHERE day = CAST(? AS DATE) ORDER BY seq", [date])
    cols = [d[0] for d in cur.description]
    items = [dict(zip(cols, r)) for r in cur.fetchall()]

    total_pages = max(1, -(-len(items) // PAGE_SIZE))
    start = (page - 1) * PAGE_SIZE
    return {"date": date, "page": page, "total_pages": total_pages,
            "items": items[start:start + PAGE_SIZE]}

