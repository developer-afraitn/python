import re

from app.utils.main_helper import http_request, wrap_words, mask_bracketed, unmask_bracketed


def cities_list():
    response = http_request("https://tourgardan.com/api/info/city/search")
    response = response["response"]
    #print(response)

    cities = {item["text"]: item["id"] for item in response.get("data", []) if
              item.get("text") and item.get("id")}

    return cities


class CityExtractor:

    def __init__(self):
        pass

    @staticmethod
    def extract(message: str, old_selected: list | None):
        print('\n\n-----------------------------------------START CITY EXTRACTOR---------------------------------------------------\n\n')
        print('message',message)
        process_message,masked=mask_bracketed(message)

        extract = []
        cities = cities_list()
        for name, city_id in cities.items():
            if f" {name} " in f" {process_message} ":
                extract.append({
                    "name": name,
                    "id": city_id
                })

        processed_message=wrap_words(process_message, [item['name'] for item in extract], "city")

        processed_message=unmask_bracketed(processed_message,masked)

        print('extract', extract)
        print('old_selected',old_selected)
        print('processed_message',processed_message)
        print('\n\n-----------------------------------------END CITY EXTRACTOR---------------------------------------------------\n\n')
        if extract:
            return processed_message,extract

        return processed_message,old_selected
