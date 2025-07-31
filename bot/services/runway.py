import aiohttp
import asyncio
from typing import Optional, Dict, Any
from bot.utils.config import RUNWAY_API_KEY


class RunwayAPI:
    BASE_URL = "https://api.dev.runwayml.com/v1"
    HEADERS = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {RUNWAY_API_KEY}",
        "X-Runway-Version": "2024-11-06"
    }
    
    @staticmethod
    async def create_video_from_image(image_url: str, prompt: str = "Picture became colorful, camera moves, people walking") -> Optional[str]:
        """Create video from image using Runway gen4_turbo model"""
        payload = {
            "promptImage": image_url,
            "promptText": prompt,
            "model": "gen4_turbo",
            "ratio": "1280:720",
            "duration": 5
        }
        
        async with aiohttp.ClientSession() as session:
            # Create task
            async with session.post(
                f"{RunwayAPI.BASE_URL}/image_to_video",
                json=payload,
                headers=RunwayAPI.HEADERS
            ) as response:
                if response.status != 200:
                    print(f"Error creating video task: {await response.text()}")
                    return None
                
                data = await response.json()
                task_id = data.get("id")
                
                if not task_id:
                    return None
                
                return task_id
    
    @staticmethod
    async def get_task_status(task_id: str) -> Dict[str, Any]:
        """Get status of video generation task"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{RunwayAPI.BASE_URL}/tasks/{task_id}",
                headers=RunwayAPI.HEADERS
            ) as response:
                if response.status == 200:
                    return await response.json()
                return {"status": "ERROR", "error": await response.text()}
    
    @staticmethod
    async def wait_for_video(task_id: str, progress_callback=None) -> Optional[str]:
        """Wait for video generation to complete with progress updates"""
        max_attempts = 60  # 3 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            status_data = await RunwayAPI.get_task_status(task_id)
            status = status_data.get("status")
            
            if status == "SUCCEEDED":
                output = status_data.get("output", [])
                return output[0] if output else None
            
            elif status == "FAILED" or status == "ERROR":
                print(f"Video generation failed: {status_data}")
                return None
            
            # Call progress callback if provided
            if progress_callback and status == "RUNNING":
                progress = status_data.get("progress", "0")
                await progress_callback(progress)
            
            await asyncio.sleep(3)  # Wait 3 seconds before next check
            attempt += 1
        
        return None