from openai import AsyncOpenAI
import json
from typing import List, Dict, Any, Optional
from bot.utils.config import OPENAI_API_KEY

client = AsyncOpenAI(api_key=OPENAI_API_KEY)


class OpenAIService:
    @staticmethod
    async def select_best_photo(photos: List[Dict[str, Any]], excluded_ids: List[int] = None) -> Optional[Dict[str, Any]]:
        """Use OpenAI o3 model to select the best historical building/street photo"""
        if excluded_ids is None:
            excluded_ids = []
        
        # Filter out already shown photos
        available_photos = [p for p in photos if p.get("cid") not in excluded_ids]
        
        if not available_photos:
            return None
        
        # Prepare photo descriptions for the model
        photo_descriptions = []
        for i, photo in enumerate(available_photos):
            desc = f"Photo {i}: Title: {photo.get('title', 'N/A')}, Year: {photo.get('year', 'N/A')}, ID: {photo.get('cid')}"
            photo_descriptions.append(desc)
        
        prompt = f"""Select the oldest building or street photo that would be suitable for video generation.
Photos:
{chr(10).join(photo_descriptions)}

Return only the photo index number (0-based) of the best choice."""
        
        try:
            # Using the new o3 model with Responses API
            response = await client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # Parse the response
            content = response.choices[0].message.content.strip()
            index = int(content)
            
            if 0 <= index < len(available_photos):
                return available_photos[index]
            
        except Exception as e:
            print(f"OpenAI API error: {e}")
            # Fallback: return the oldest available photo
            if available_photos:
                return min(available_photos, key=lambda x: x.get("year", 9999))
        
        return None
    
    @staticmethod
    async def geocode_address(address: str) -> Optional[Dict[str, float]]:
        """Use OpenAI o3 model to convert address to coordinates"""
        prompt = f"""Convert the following address to geographic coordinates (latitude and longitude).
Address: {address}

Return ONLY a JSON object with the coordinates in this exact format:
{{"latitude": <number>, "longitude": <number>}}

If the address is ambiguous or cannot be geocoded, return:
{{"error": "Cannot geocode address"}}"""
        
        try:
            response = await client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.choices[0].message.content.strip()
            result = json.loads(content)
            
            if "error" in result:
                return None
                
            if "latitude" in result and "longitude" in result:
                return {
                    "latitude": float(result["latitude"]),
                    "longitude": float(result["longitude"])
                }
            
        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"Error parsing geocoding response: {e}")
        except Exception as e:
            print(f"OpenAI API error during geocoding: {e}")
        
        return None