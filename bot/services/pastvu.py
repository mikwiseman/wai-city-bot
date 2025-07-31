import aiohttp
import json
from typing import List, Dict, Any


class PastVuAPI:
    BASE_URL = "https://pastvu.com/api2"
    PHOTO_BASE_URL = "https://pastvu.com/_p/a/"
    
    @staticmethod
    async def get_nearest_photos(lat: float, lon: float, year: int = 1928) -> List[Dict[str, Any]]:
        """Get nearest historical photos from PastVu API"""
        params = {
            "method": "photo.giveNearestPhotos",
            "params": json.dumps({
                "geo": [lat, lon],
                "year2": year,
                "type": "photo"
            })
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(PastVuAPI.BASE_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if "result" in data and "photos" in data["result"]:
                        return data["result"]["photos"]
                return []
    
    @staticmethod
    def get_photo_url(file_path: str) -> str:
        """Construct full photo URL from file path"""
        return f"{PastVuAPI.PHOTO_BASE_URL}{file_path}"