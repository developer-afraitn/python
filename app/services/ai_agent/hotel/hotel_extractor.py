from app.utils.main_helper import http_request


class HotelExtractor:
    def extract(self,message: str,city_id:int):
        result = []
        hotels=self.hotels_list(city_id=city_id)
        for name, hotel_id in hotels.items():
            if name in message:
                result.append({
                    "name": name,
                    "id": hotel_id
                })
            
        return result
    
    def hotels_list(self,city_id:int):
        response=http_request('https://tourgardan.com/api/info/hotel/search',params={"city_id":city_id})
        response = response["response"]
        #print(response)
        
        hotels = {item["name_fa"]: item["id"] for item in response.get("data", []) if item.get("name_fa") and item.get("id")}
        
        return hotels
    