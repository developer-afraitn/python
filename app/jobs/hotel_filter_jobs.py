from json import JSONDecoder

from app.services.ai_agent.hotel.memory import Memory
from app.utils.main_helper import http_request

import json

def hotel_filter_process(user_id,message,detect_information):
    user_memory_id, information = (Memory()).info(user_id)
    prompt=f"- تاریخ امروز برابر است با: 1404/10/25 تو یک مدل زبانی هستی که باید فیلتر جستجوی هتل را بر اساس ورودی کاربر مدیریت کنی. فیلتر فعلی کاربر را گرفته و بر اساس ورودی کاربر بر روی فیلتر فعلی تغییرات خواسته شده را بر اساس قوانین زیر اعمال کرده و خروجی نهایی را به صورت جیسون برمیگردانی # فیلد های فیلتر کاربر - city_name :  نام فارسی شهر (رشته‌ فارسی) - check_in : تاریخ ورود به هتل به شمسی با فرمت YYYY/MM/DD - check_out : تاریخ خروج از هتل به شمسی با فرمت YYYY/MM/DD - passengers : لیستی از اتاق‌ها. هر اتاق یک شیء با \"adult\" (عدد صحیح تعداد بزرگسالان) و \"child\" (آرایه‌ای از اعداد صحیح سن کودکان، اگر هیچ کودکی نبود آرایه خالی). - hotel : لیستی از نام فارسی هتل‌های انتخابی (رشته‌ های فارسی). - star : لیستی از اعداد ستاره‌ها.عددی بین 1 تا 5. - nationality : لیستی از ملیت‌ها که فقط می‌تواند شامل \"domestic\" (برای ایرانی) یا \"foreign\" (برای خارجی) باشد. - room_capacity : لیستی از اعداد ظرفیت تخت اتاق عددی بین 1 تا 10. - min_price : حداقل قیمت عددی صحیح به ریال باشد - max_price : حداکثر قیمت عددی صحیح به ریال باشد - sorting : مرتب سازی که شامل موارد زیر است -star,asc = مرتب سازی بر اساس کمترین ستاره -star,desc = مرتب سازی بر اساس بیشترین ستاره -user_rate,asc = مرتب سازی بر اساس کمترین امتیاز هتل -user_rate,desc = مرتب سازی بر اساس بیشترین امتیاز هتل -price,asc = مرتب سازی بر اساس کمترین قیمت -price,desc = مرتب سازی بر اساس بیشترین قیمت برای حداقل یا حداکثر قیمت اگر کاربر نوع را مشخص نکرده بود نوع آن را تومان در نظر بگیر - برای تبدیل تومان به ریال عدد را در عدد 10 ضرب کن - برای تبدیل ریال به تومان عدد را بر عدد 10 تقسیم کن اگر ورودی کاربر تغییری در فیلدی ایجاد نکند، مقدار فعلی آن فیلد را نگه دار کن و آن را تغییر نده. اگر کاربر بخواهد فیلدی را حذف کند، آن فیلد را از JSON حذف کن. خروجی فقط یک JSON معتبر بدون هیچ متن اضافی، کامنت، یا کاراکتر دیگر باشد. مثلاً اگر فیلتر نهایی این باشد، دقیقاً این را خروجی بده فیلتر فعلی: {information}"
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
    #print('ddddddddddddddddddddddddddddddddddddd',prompt)
    #response = http_request('http://192.168.8.128:11434/api/chat',method="post", data=params)
    response = http_request('http://force.api.e24.pro/o/api/chat',method="post", data=params)

    if response["status_code"] == 200:
        response = response["response"]['message']['content']
        response=json.loads(response)
        for i in response:
            print(i, response.get(i),detect_information.get(i))

        print('modelllllllllll detect',response)
        print('coooooodddddeee detect',detect_information)

    else:
        print('modelllllllllllsssssssss detect',response)
