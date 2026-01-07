import re

from app.utils.main_helper import http_request

def is_remove_star_filter(text: str) -> bool:
    pattern = r'(حذف\s+فیلتر\s+هتل|فیلتر\s+هتل\s+(را|رو)?\s*حذف\s+کن)'
    return bool(re.search(pattern, text))


def hotels_list(city_id:int):
    response=http_request('https://tourgardan.com/api/info/hotel/search',params={"city_id":city_id})
    response = response["response"]
    #print(response)

    hotels = {item["name_fa"]: item["id"] for item in response.get("data", []) if item.get("name_fa") and item.get("id")}

    return hotels


class HotelExtractor:

    def __init__(self):
        pass

    @staticmethod
    def extract(message: str, city_id:int, old_selected:list|None):
        print('hotel Extractor',message,city_id,old_selected)
        extract=is_remove_star_filter(message)
        if extract:
            return None

        extract = []
        hotels= hotels_list(city_id=city_id)
        for name, hotel_id in hotels.items():
            if  f" {name} " in f" {message} ":
                extract.append({
                    "name": name,
                    "id": hotel_id
                })

        print('extract_hotels',extract)
        if extract:
            return extract

        print('old_selected',old_selected)
        return old_selected
    