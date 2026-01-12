import json

from app.exceptions import AppError
from app.services.ai_agent.hotel.city_extractor import CityExtractor
from app.services.ai_agent.hotel.hotel_extractor import HotelExtractor
from app.services.ai_agent.hotel.memory import Memory
from app.services.ai_agent.llm import Llm
from app.storage.chromadb import ChromaDb
from app.utils.ai_response_message import success_message
from app.utils.main_helper import http_request


class HotelComparison:


    def __init__(self):
        pass


    def handle(self, user_id: str, message: str):
        memory =Memory()
        user_memory_id, information = memory.info(user_id)
        if information is None:
            information = {"city_id": None}

        print(information)
        processed_message,city_extract=(CityExtractor()).extract(message=message, old_selected=[{"name": information["city_name"],"id": information["city_id"]}] if information.get("city_name") else None)
        print('city_extract',city_extract,processed_message)

        if city_extract is not None:
            found_city = city_extract[0]
            information["city_name"] = found_city['name']
            information["city_id"] = found_city['id']

        # detect hotels
        if information.get("city_id"):
            processed_message,hotel_extract=(HotelExtractor()).extract(message=processed_message,city_id=information["city_id"],old_selected=information.get('hotel'))
            if hotel_extract is not None:
                information["hotel"] = hotel_extract
            else:
                information.pop("hotel", None)


        # persist
        memory.update(user_memory_id,user_id,information)

        required_fields = {
            "city_name": "شهر مشخص نیست",
            "hotel": "هتلی برای مقایسه وارد نشده است",
        }

        missing = [key for key in required_fields if information.get(key) in (None, "", [])]

        if missing:
            raise AppError(
                status=400,
                message=required_fields[missing[0]],
            )
        print(information)
        hotels=[]
        chroma_db=ChromaDb()
        hotel_details=[]
        for item in information['hotel']:
            response=http_request(f"https://tourgardan.com/hotel/review/{item['id']}/obj")
            if response['status_code'] == 200:
                hotel_info=response['response']['data']
                hotel_details.append(hotel_info)
                chroma_db.save_list([
                    {
                        'id': hotel_info['id'],
                        'document': json.dumps(self.pruning_data(hotel_info), ensure_ascii=False),
                        'metadata': {'type': 'hotel_info'}
                    }
                ])
                hotels.append(response['response']['data'])

        hotel_ids=[item['id'] for item in hotels]
        result_ask_hotel=[]
        hotels=[]
        for item in hotel_ids:
            find_hotel = chroma_db.ask(message,n_results=len(hotel_ids),where={"id":item})#"type": "hotel_info",
            if len(find_hotel['ids']):
                for hotel in hotel_details:
                    if f"{hotel['id']}" == find_hotel['ids'][0][0]:
                        hotels.append(hotel)
                result_ask_hotel.append(json.loads(find_hotel['documents'][0][0]))

        prompt=f'با توجه به اطلاعات هتل به سوال کاربر پاسخ بده {result_ask_hotel}'
        response = (Llm()).ollama_model(prompt, message)
        answer='جزییات هتل را میتوانید مشاهده و مقایسه کنید'
        if response["status_code"] == 200:
            answer=response["response"]["message"]["content"]

        return success_message(
            message=answer,
            type='hotel-comparisons',
            result={
                "hotels":hotels
            },
            request=[]
        )

    def pruning_data(self,hotel):
        information = {
            'id': hotel['id'],
            'name': hotel['name_fa'],
            'short_description': hotel['short_description_fa'],
            'category': hotel['category']['name_fa'],
            'facilities': [item['name'] for item in hotel['facilities']],
            'star': hotel['star'],
            'address': hotel['address_fa'],
            'city': hotel['city']['name_fa'],
            'website': hotel['website'],
            'score_avg': hotel['score_avg'],
            'create_year': hotel['create_year'],
            'rebuilding_year': hotel['rebuilding_year'],
            'floors_count': hotel['floors_count'],
            'nearby': [item['title'] for item in hotel['nearby']],
            'user_rate': hotel['user_rate'],
            'user_rate_detail': hotel['user_rate_detail'],
        }


        return information

