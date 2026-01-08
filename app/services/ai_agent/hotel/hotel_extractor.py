import re

from app.utils.main_helper import http_request, mask_bracketed, wrap_words, unmask_bracketed


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
        print('\n\n-----------------------------------------START HOTEL EXTRACTOR---------------------------------------------------\n\n')
        print(message)
        process_message,masked=mask_bracketed(message)
        extract=is_remove_star_filter(process_message)
        if extract:
            processed_message=unmask_bracketed(process_message,masked)
            return processed_message,None

        extract = []
        hotels= hotels_list(city_id=city_id)
        for name, hotel_id in hotels.items():
            if  f" {name} " in f" {process_message} ":
                extract.append({
                    "name": name,
                    "id": hotel_id
                })
        processed_message=wrap_words(process_message, [item['name'] for item in extract], "hotel")

        processed_message=unmask_bracketed(processed_message,masked)

        print('extract', extract)
        print('old_selected',old_selected)
        print('processed_message',processed_message)
        print('\n\n-----------------------------------------END HOTEL EXTRACTOR---------------------------------------------------\n\n')
        if extract:
            return processed_message,extract
        return processed_message,old_selected
    