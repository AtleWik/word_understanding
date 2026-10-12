import json
import time
import uuid
import functools
from pathlib import Path



#store for later
TRACE_FILE = Path("trace.jsonl")
#event from one run
RUN_ID = uuid.uuid4().hex[:8] 

def trace(category):

    def fetch_information(function):
        @functools.wraps(function)

        def wrapper(*args, **kwargs):
            start_wall =time.time()
            start = time.perf_counter()
            status = "ok"

            result = None

            try:
                result = function(*args, **kwargs)
                return result
            except Exception as e:
                status = type(e).__name__
                raise
            finally:
                result.count = len(result) if isinstance(result, (list, dict)) else None

            event = {
                "run_id": RUN_ID,
                "kind": kind,
                "name": func.__name__,
                "args": [str(a)[:50] for a in args],
                "kwargs": {k: str(v)[:50] for k, v in kwargs.items()},  # NEW
                "start": start_wall,
                "duration_ms": round((time.perf_counter() - start) * 1000, 1),
                "status": status,
                "result_count": result_count,                 
            }
            with TRACE_FILE.open("a", encoding="utf-8") as f:
                f.write(json.dumps(event, ensure_ascii=False) + "\n")
        return wrapper
    return fetch_information                