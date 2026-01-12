from __future__ import annotations
from fastapi import APIRouter
from pydantic import BaseModel, Field, field_validator
from app.logging_config import get_logger
from app.services.ai_agent.hotel.memory import Memory

from app.services.ai_agent.intent_classifier import IntentService
from app.services.ai_agent.hotel.hotel_filter import HotelFilter
from app.services.ai_agent.hotel.hotel_comparison import HotelComparison
from app.utils.ai_response_message import success_message

router = APIRouter()
logger = get_logger("ai-agent")

# برای MVP: ساخت جدول‌ها در شروع
# (بعداً بهتره با Alembic مهاجرتی کنید)

intent_service  = IntentService()  # فعلاً rule-based

class IntentRequest(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=128)
    message: str = Field(..., min_length=1, max_length=4000)
    @field_validator("user_id", mode="before")
    @classmethod
    def coerce_user_id_to_str(cls, v):
        if v is None:
            raise ValueError("user_id is required")
        return str(v)


class IntentResponse(BaseModel):
    intent: str  # one of: filter | comparison | greeting | other




#from app.jobs.test_jobs import do_something
#from app.dispatch import dispatch
@router.post("/ai")
def ai_agent(payload: IntentRequest):
    #dispatch(do_something, 1234333356,'aliiiii', queue="low") use queue
    #dispatch(do_something, user_id=1234333356,name='aliiiiieeeee', queue="low")
    print('-----------------------------------------START---------------------------------------------------')
    user_memory_id,information=(Memory()).info(payload.user_id)
    print('start')
    print('payload',payload)
    print('user_memory_id',user_memory_id)
    print('information',information)

    intent = intent_service.detect_intent(user_id=payload.user_id, message=payload.message)
    #return 'ok'
    print('intent',intent)
    match intent:
        case 'filter':
            filter = (HotelFilter()).handle(user_id=payload.user_id, message=payload.message)
            return filter
            #return {"status":200,"message":"OK","detail":"null","data":{"type":"hotel-search","message":"فیلتر برای شهر کیش با تاریخ ورود چهارشنبه 3 دی و تاریخ خروج شنبه 6 دی 1404 ، 1 نفر بزرگسال اعمال شد","result":{"filters":{"city_name":"کیش","check_in":"2025-12-24","check_out":"2025-12-27","passengers":[{"adult":1,"child":[]}],"city_id":760013,"limit":3,"page":1,"hotel":[]}},"requests":["هتل های 4 و 5 ستاره رو برام فیلتر کن","قیمت بین 10 میلیون و 18 میلیون رو برام فیلتر کن","تاریخ ورود رو به پنج شنبه 4 دی تغییر بده","تاریخ ورود رو به جمعه 5 دی تغییر بده","دوتا اتاق میخوام.اتاق دوم سه نفر بزرگسال","شهر اصفهان رو برام فیلتر کن"]},"additional":[],"parameters":[]}
        case 'comparison':
            comparison = (HotelComparison()).ask(payload.user_id, payload.message)["answer"]
            #rag.index_many(["1018483","1018392","1002353","1001612","1001477","1000336","1000354","1001104"])
            return success_message(
                message=comparison,
                type='hotel-comparisons',
                result={
                    #"hotels":[{"id":1000336,"name_fa":"داریوش"}]
                },
                request=[]
            )
        case 'greeting':
            
            return success_message(
                message="سلام.من تورگردان هستم.در خدمت شما",
                type='greeting',
                result={},
                request=[]
            )
        case 'other':
            return {"other": intent}
        case _:
            return {"Unknown": 'Unknown'}
        


@router.get("/vector")
def vector():
    comparison = (HotelComparison()).index_many(["1018483","1018392","1002353","1001612","1001477","1000336","1000354","1001104"])
    return comparison

