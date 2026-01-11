import time

from app.storage.chromadb import ChromaDb
from app.storage.repo.memoryRepo import MemoryRepo
from app.utils.main_helper import http_request
from typing import Any, Dict, List, Union


from datetime import datetime, timedelta
def memory(user_id: str) -> dict[str, Any] | None:
    memory_repo = MemoryRepo()
    memory = memory_repo.find(user_id=user_id)
    if memory is not None:

        # اگر بیشتر از ۱۰ ساعت گذشته، مموری را نادیده بگیر
        if memory.updated_at < datetime.now() - timedelta(hours=10):
            return None

        return memory.information
    return None


def talk_process(message):
    #information = memory("1233322")
    #print('information',information)
    filter="filter"
    prompt=f'#نکات - از مکالمه کاربر و سابقه مکالمه کاربر تشخیص بده که درخواست کاربر درمورد چه چیزی است - کاربر در مکالمه قبلی خود درمورد "{filter}" درخواست داده بوده است - نوع درخواست کاربر شامل موارد زیر است  - filter : فلیتر هتلها - greeting : سلام و احوالپرسی - comparison : مقایسه یا امکانات و جزییات هتل - other : سایر #output مقدار خروجی به صورت متن و فقط یکی از موارد زیر هست - filter - comparison - greeting - other هیچگونه کاراکتری به خروجی اضافه نکن'
    params={
        "model":"qwen2.5:7b-instruct-q6_K",
        "stream":False,
        "messages":[
            {
                "role":"system",
                "content":prompt
            },
            {
                "role":"user",
                "content":message
            }
        ]
    }
    response = http_request('http://192.168.8.128:11434/api/chat',method="post", data=params)
    print(response)

    if response["status_code"] == 200:
        response = response["response"]['message']['content']

        print('response ok ',response)
        chromadb = ChromaDb()
        chromadb.save_list([
            {
                # 'id': 125,
                'document': message,
                'metadata': {'type': 'talk', 'feature': response}
            }
        ])
