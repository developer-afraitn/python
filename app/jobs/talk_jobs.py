from app.services.ai_agent.hotel.memory import Memory
from app.services.ai_agent.llm import Llm
from app.storage.chromadb import ChromaDb
from app.utils.main_helper import http_request


def talk_process(user_id,message):
    user_memory_id, information = (Memory()).info(user_id)
    if information is not None:
        talk_about=information.get("talk_about")
    else:
        talk_about=""
    prompt=f'#نکات - از مکالمه کاربر و سابقه مکالمه کاربر تشخیص بده که درخواست کاربر درمورد چه چیزی است - کاربر در مکالمه قبلی خود درمورد "{talk_about}" درخواست داده بوده است - نوع درخواست کاربر شامل موارد زیر است  - filter : فلیتر هتلها - greeting : سلام و احوالپرسی - comparison : مقایسه یا امکانات و جزییات هتل - other : سایر #output مقدار خروجی به صورت متن و فقط یکی از موارد زیر هست - filter - comparison - greeting - other هیچگونه کاراکتری به خروجی اضافه نکن'

    response = (Llm()).ollama_model(prompt,message)


    if response["status_code"] == 200:
        response = response['content']

        (ChromaDb()).save_list([
            {
                # 'id': 125,
                'document': message,
                'metadata': {'type': 'talk', 'feature': response}
            }
        ])
