from app.queue import get_queue

def dispatch(job, *args, queue: str = "default", **kwargs):
    return get_queue(queue).enqueue(job, *args, **kwargs)