import time
from fastapi import HTTPException, status

REQUESTS = {}
LIMIT = 5
WINDOW = 60


def rate_limit(client_id: str):
    now = time.time()
    window_start = now - WINDOW

    history = REQUESTS.get(client_id, [])
    history = [t for t in history if t > window_start]

    if len(history) >= LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded"
        )

    history.append(now)
    REQUESTS[client_id] = history
