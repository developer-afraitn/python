
from typing import Any
from datetime import datetime, timedelta

from app.storage.repo.memoryRepo import MemoryRepo

memory_repo = MemoryRepo()

class Memory:
    def __init__(self):
        print('ini')

    def info(self,user_id: str):
        memory = memory_repo.find(user_id=user_id)
        if memory is not None:
            user_memory_id = memory.id
            # اگر بیشتر از ۱۰ ساعت گذشته، مموری را نادیده بگیر
            if memory.updated_at < datetime.now() - timedelta(hours=10):
                return user_memory_id,None

            return user_memory_id,memory.information
        return None,None

    def update(self,user_memory_id, user_id, information):
        if user_memory_id:
            memory_repo.update(id=user_memory_id, information=information)
        else:
            memory_repo.create(user_id=user_id, information=information)