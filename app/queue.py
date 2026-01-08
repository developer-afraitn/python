import os
from redis import Redis
from rq import Queue

_queues = {}

def get_queue(name: str = "default") -> Queue:
    if name not in _queues:
        redis_url = os.getenv("REDIS_URL")
        redis_conn = Redis.from_url(redis_url)
        _queues[name] = Queue(name, connection=redis_conn)
    return _queues[name]