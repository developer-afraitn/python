from __future__ import annotations

from app.configs.state import history_info
from app.dispatch import dispatch
from app.exceptions import AppError
from app.jobs.hotel_filter_jobs import hotel_filter_process
from app.services.ai_agent.hotel.city_extractor import CityExtractor
from app.services.ai_agent.hotel.hotel_extractor import HotelExtractor
from app.services.ai_agent.hotel.memory import Memory
from app.services.ai_agent.hotel.nationality_extractor import NationalityExtractor
from app.services.ai_agent.hotel.passenger_extractor import PassengerExtractor
from app.services.ai_agent.hotel.price_extractor import PriceExtractor
from app.services.ai_agent.hotel.room_capacity_extractor import RoomCapacityExtractor
from app.services.ai_agent.hotel.star_extractor import StarExtractor
from app.storage.repo.memoryRepo import MemoryRepo
from app.logging_config import get_logger
from app.utils.datetime_helper import to_date, to_iso_date_str, today_date,gregorian_to_jalali
from app.utils.main_helper import currency_price
from app.utils.ai_response_message import success_message
from app.services.ai_agent.hotel.hotel_date_extractor import HotelDateExtractor

logger = get_logger("ai-agent")
memory_repo = MemoryRepo()

class HotelFilter:

    def __init__(self):
        self._city_cache = None
        self._city_cache_at = None
        self.date_extractor = HotelDateExtractor()


    def handle(self, user_id: str, message: str):

        """
            فیلتر نهایی به صورت زیر است
            {
                "page":1,
                "limit":3,
                "city_id":760013,
                "city_name":"کیش",
                "check_in":"2026-01-08",
                "check_out":"2026-01-11",
                "passengers":[
                    {
                        "adult":2,
                        "child":[3,4]
                    }
                ],
                "hotel":[1000355,1000360],
                "star":[1,2,3,4,5],
                "nationality":["domestic","foreign"],
                "room_capacity":[1,2,3,4],
                "min_price":10000000,
                "max_price":33000000,
                "sorting":"price,asc"
            }
        """
        memory =Memory()
        user_memory_id, information = memory.info(user_id)
        if information is None:
            information = {"city_id": None, "check_in": None, "check_out": None}

        print(information)
        processed_message,city_extract=(CityExtractor()).extract(message=message, old_selected=[{"name": information["city_name"],"id": information["city_id"]}] if information.get("city_name") else None)
        print('city_extract',city_extract,processed_message)
        
        # ✅ استفاده از کلاس جدید
        new_check_in, new_check_out, new_night = self.date_extractor.extract(
            message=processed_message,
            prev_check_in=information.get("check_in"),
            prev_check_out=information.get("check_out"),
            prev_nights=information.get("night"),
        )

        if city_extract is not None:
            found_city = city_extract[0]
            information["city_name"] = found_city['name']
            information["city_id"] = found_city['id']
        if new_check_in is not None:
            information["check_in"] = new_check_in
        if new_check_out is not None:
            information["check_out"] = new_check_out

        # BUGFIX: safe serialize (date -> str), keep str as-is
        information["check_in"] = to_iso_date_str(information.get("check_in")) or information.get("check_in")
        information["check_out"] = to_iso_date_str(information.get("check_out")) or information.get("check_out")
        information['night'] = new_night

        #detect star
        processed_message,star_extract=(StarExtractor()).extract(message=processed_message,old_selected=information.get('star'))
        if star_extract is not None:
            information["star"] = star_extract
        else:
            information.pop("star", None)

        # detect hotels
        if information.get("city_id"):
            processed_message,hotel_extract=(HotelExtractor()).extract(message=processed_message,city_id=information["city_id"],old_selected=information.get('hotel'))
            if hotel_extract is not None:
                information["hotel"] = hotel_extract
            else:
                information.pop("hotel", None)


        #detect room_capacity
        processed_message,room_capacity_extract=(RoomCapacityExtractor()).extract(message=processed_message,old_selected=information.get('room_capacity'))
        if room_capacity_extract is not None:
            information["room_capacity"] = room_capacity_extract
        else:
            information.pop("room_capacity", None)

        #detect passenger room
        (PassengerExtractor()).extract(message=processed_message)
        information['passengers'] = [{'adult': 1, 'child': []}]

        #detect nationality
        (NationalityExtractor()).extract(message=processed_message)


        #detect min , max price
        (PriceExtractor()).extract(message=processed_message)

        information['limit'] = 3
        information['page'] = 1
        information['talk_about'] = 'filter'

        # persist
        memory.update(user_memory_id,user_id,information)

        dispatch(hotel_filter_process, user_id,message,information, queue="low")
        #hotel_filter_process(user_id,message,information)
        # required fields
        required_fields = {
            "city_name" : "شهر مشخص نیست",
            "check_in" : "تاریخ ورود مشخص نیست",
            "check_out" : "تاریخ خروج مشخص نیست",
        }

        missing = [key for key in required_fields if information.get(key) in (None, "", [])]

        if missing:

            raise AppError(
                status=400,
                message=required_fields[missing[0]],
                data=None,
            )



        # date rules (assume format always valid)
        ci = to_date(information.get("check_in"))
        co = to_date(information.get("check_out"))
        t = today_date()

        if ci < t:
            raise AppError(
                status=400,
                message="تاریخ ورود باید بعد از امروز باشد.",
                data=None,
                detail={"check_in": ci.isoformat(), "today": t.isoformat()},
            )

        if co <= ci:
            raise AppError(
                status=400,
                message="تاریخ خروج باید بعد از تاریخ ورود باشد.",
                data=None,
                detail={"check_in": ci.isoformat(), "check_out": co.isoformat()},
            )
        message=self.hotel_filter_summary_text(information)
        if information.get("hotel") is not None:
            information['hotel'] = [item["id"] for item in information['hotel']]

        history_info["processed_message"] = processed_message

        return success_message(
            message=message,
            type='hotel-search',
            result={
                'filters':information
            },
            request=[])



    @staticmethod
    def hotel_filter_summary_text(detect: dict) -> str:
        # تاریخ‌های میلادی (ایزو) -> جلالی با فرمت PHP-like که خودت دادی
        city_name = detect.get("city_name")
        check_in_text = gregorian_to_jalali(detect["check_in"], "l j F")
        check_out_text = gregorian_to_jalali(detect["check_out"], "l j F Y")
        message = (
            f"فیلتر برای شهر {city_name} "
            f"با تاریخ ورود {check_in_text} "
            f"و تاریخ خروج {check_out_text} "
        )

        # Star
        star = detect.get("star")
        if star:
            star_list = sorted(map(int, star))
            if len(star_list) >= 3 and (star_list[-1] - star_list[0] + 1) == len(star_list):
                message += f" ، هتل های {star_list[0]} تا {star_list[-1]} ستاره"
            else:
                message += f" ، هتل های {' و '.join(map(str, star_list))} ستاره"

        # Room capacity
        room_capacity = detect.get("room_capacity")
        if room_capacity:
            cap_list = sorted(map(int, room_capacity))
            if len(cap_list) >= 3 and (cap_list[-1] - cap_list[0] + 1) == len(cap_list):
                message += f" ، اتاق های {cap_list[0]} تا {cap_list[-1]} تخته"
            else:
                message += f" ، اتاق های {' و '.join(map(str, cap_list))} تخته"

        # Price range
        min_price = detect.get("min_price")
        max_price = detect.get("max_price")
        if min_price or max_price:
            message += " ، بازه قیمت"
            if min_price:
                message += f" از {currency_price(min_price,show_letter= True,show_label= False)}"
            if max_price:
                message += f" تا {currency_price(max_price,show_letter= True,show_label= False)}"
            message += " تومن"
        # Hotels
        hotels = detect.get("hotel") or []
        if hotels:
            if len(hotels) == 1:
                message += f" ، هتل {hotels[0].get('name')}"
            else:
                names = [h.get("name") for h in hotels if h.get("name")]
                message += f" ، هتل های {' و '.join(names)}"

        # Passengers
        passengers = detect.get("passengers") or []
        if len(passengers) == 1:
            p = passengers[0]
            message += f" ، {p.get('adult', 0)} نفر بزرگسال"
            child = p.get("child") or []
            if child:
                message += f" و {len(child)} کودک {' و '.join(map(str, child))} ساله"

        elif len(passengers) > 1:
            for idx, p in enumerate(passengers):
                message += (
                    f" ، اتاق {(idx + 1)} شامل "
                    f"{p.get('adult', 0)} نفر بزرگسال"
                )
                child = p.get("child") or []
                if child:
                    message += (
                        f" و {len(child)} کودک "
                        f"{' و '.join(map(str, child))} ساله"
                    )

        # Sorting
        sorting_map = {
            "star,asc": "کمترین ستاره",
            "star,desc": "بیشترین ستاره",
            "user_rate,asc": "کمترین امتیاز هتل",
            "user_rate,desc": "بیشترین امتیاز هتل",
            "price,asc": "کمترین قیمت",
            "price,desc": "بیشترین قیمت",
        }

        sorting = detect.get("sorting")
        if sorting:
            message += f" ، مرتب سازی بر اساس {sorting_map.get(sorting, sorting)}"

        message += " اعمال شد"
        return message
