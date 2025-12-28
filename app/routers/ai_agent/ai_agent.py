from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel, Field
from app.logging_config import get_logger

from app.services.ai_agent.intent_classifier import IntentService
from app.services.ai_agent.hotel.hotel_filter import HotelFilter

router = APIRouter()
logger = get_logger("ai-agent")

# برای MVP: ساخت جدول‌ها در شروع
# (بعداً بهتره با Alembic مهاجرتی کنید)

intent_service  = IntentService()  # فعلاً rule-based

class IntentRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=4000)


class IntentResponse(BaseModel):
    intent: str  # one of: filter | comparison | greeting | other


@router.post("/ai")
def ai_agent(payload: IntentRequest):
    intent = intent_service.detect_intent(user_id=payload.user_id, message=payload.message)
    match intent:
        case 'filter':
            filter = (HotelFilter()).handle(user_id=payload.user_id, message=payload.message)
            return filter
            #return {"status":200,"message":"OK","detail":"null","data":{"type":"hotel-search","message":"فیلتر برای شهر کیش با تاریخ ورود چهارشنبه 3 دی و تاریخ خروج شنبه 6 دی 1404 ، 1 نفر بزرگسال اعمال شد","result":{"filters":{"city_name":"کیش","check_in":"2025-12-24","check_out":"2025-12-27","passengers":[{"adult":1,"child":[]}],"city_id":760013,"limit":3,"page":1,"hotel":[]}},"requests":["هتل های 4 و 5 ستاره رو برام فیلتر کن","قیمت بین 10 میلیون و 18 میلیون رو برام فیلتر کن","تاریخ ورود رو به پنج شنبه 4 دی تغییر بده","تاریخ ورود رو به جمعه 5 دی تغییر بده","دوتا اتاق میخوام.اتاق دوم سه نفر بزرگسال","شهر اصفهان رو برام فیلتر کن"]},"additional":[],"parameters":[]}
        case 'comparison':
            return {"status":200,"message":"OK","detail":"null","data":{"type":"hotel-comparison","message":"جزییات داریوش در شهر کیش را میتوانید مشاهده و مقایسه کنید","result":{"hotels":[{"id":1000336,"name_fa":"داریوش"}]},"requests":["هتل های 4 و 5 ستاره رو برام فیلتر کن","قیمت بین 10 میلیون و 18 میلیون رو برام فیلتر کن","تاریخ ورود رو به پنج شنبه 4 دی تغییر بده","تاریخ ورود رو به جمعه 5 دی تغییر بده","دوتا اتاق میخوام.اتاق دوم سه نفر بزرگسال","شهر اصفهان رو برام فیلتر کن"]},"additional":[],"parameters":[]}
        case 'greeting':
            return {"status":200,"message":"OK","detail":"null","data":{"type":"hotel-comparison","message":"سلام.من تورگردان هستم.در خدمت شما","result":{},"requests":["هتل های 4 و 5 ستاره رو برام فیلتر کن","قیمت بین 10 میلیون و 18 میلیون رو برام فیلتر کن","تاریخ ورود رو به پنج شنبه 4 دی تغییر بده","تاریخ ورود رو به جمعه 5 دی تغییر بده","دوتا اتاق میخوام.اتاق دوم سه نفر بزرگسال","شهر اصفهان رو برام فیلتر کن"]},"additional":[],"parameters":[]}
        case 'other':
            return {"other": intent}
        case _:
            return {"Unknown": 'Unknown'}