from typing import Any,List

from app.exceptions import AppError
from app.utils.main_helper import http_request


class Llm:
    def __init__(self):
        pass

    def ollama_model(self, prompt: str, message: str,history:List[str]|None=None, exception: bool = False,exception_message: str = None) -> dict[str, None | dict[str, Any] | dict[str, str] | int | Any]:
        """
        :return:
        :rtype: dict[str, None | dict[str, Any] | dict[str, str] | int | Any]
        :param history:
        :param prompt:
        :param message:
        :param exception:
        :param exception_message:
        :return:
        """
        messages=[]
        if  history :
            for msg in history:
                messages.append({
                    "role": "user",
                    "content": msg
                })

        messages.append({
            "role": "user",
            "content": message
        })
        print('messagesmessagesmessagesmessages',messages)
        messages.append({
            "role": "system",
            "content": prompt
        })
        params = {
            "model": "qwen2.5:7b-instruct-q6_K",
            #"model": "qwen3:8b-q4_K_M",
            #"model": "qwen3:8b",
            #"model": "qwen3:4b-q4_K_M",
            #"model": "qwen3:30b-a3b",
            #"model": "nemotron-3-nano:30b-a3b-q4_K_M",
            #"model": "command-r-plus:104b-08-2024-q5_K_M",
            "stream": False,
            "messages": messages,
            "options": {
                "temperature": 0.8,
                "top_p": 0.9,
                "top_k": 40,
                "repeat_penalty": 1.1,
                "num_ctx": 4096,
                "num_predict": 2048
            }
        }
        # response = http_request('http://192.168.8.128:11434/api/chat',method="post", data=params)
        response = http_request('http://force.api.e24.pro/o/api/chat', method="post", data=params)

        if response["status_code"] == 200:
            response['content'] = response["response"]['message']['content']
        else:
            print(response)
            if exception:
                raise AppError(
                    status=503,
                    message=exception_message if exception_message is not None else 'خطا در ارتباط با مدل هوش مصنوعی',
                )

        return response