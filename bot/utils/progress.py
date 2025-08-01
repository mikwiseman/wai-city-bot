import asyncio
from typing import Optional
from aiogram.types import Message


class ProgressAnimator:
    """Utility class for animated progress messages"""
    
    def __init__(self):
        self.is_running = False
        self.current_task: Optional[asyncio.Task] = None
        self.current_percentage = 0
        self.progress_message: Optional[Message] = None
        self.base_text = ""
    
    async def start_animated_progress(
        self, 
        message: Message, 
        base_text: str,
        update_interval: float = 0.5
    ) -> Message:
        """Start animated progress with dots"""
        self.is_running = True
        progress_msg = await message.answer(base_text)
        
        async def animate():
            dots_states = ["", ".", "..", "..."]
            current_index = 0
            
            while self.is_running:
                try:
                    await progress_msg.edit_text(f"{base_text}{dots_states[current_index]}")
                    current_index = (current_index + 1) % len(dots_states)
                    await asyncio.sleep(update_interval)
                except Exception:
                    # Message might be deleted or invalid
                    break
        
        self.current_task = asyncio.create_task(animate())
        return progress_msg
    
    def stop(self):
        """Stop the animation"""
        self.is_running = False
        if self.current_task:
            self.current_task.cancel()
            self.current_task = None
    
    async def update_with_percentage(
        self, 
        message: Message, 
        base_text: str, 
        percentage: int
    ):
        """Update progress with percentage and animated dots"""
        dots_states = ["", ".", "..", "..."]
        dots_index = (percentage // 25) % len(dots_states)
        
        try:
            await message.edit_text(f"{base_text} {percentage}%{dots_states[dots_index]}")
        except Exception:
            pass
    
    async def start_animated_progress_with_percentage(
        self,
        message: Message,
        base_text: str,
        initial_percentage: int = 0,
        update_interval: float = 0.5
    ) -> Message:
        """Start animated progress with percentage that continuously animates dots"""
        self.is_running = True
        self.current_percentage = initial_percentage
        self.base_text = base_text
        self.progress_message = await message.answer(f"{base_text} {initial_percentage}%")
        
        async def animate():
            dots_states = ["", ".", "..", "..."]
            current_index = 0
            
            while self.is_running:
                try:
                    await self.progress_message.edit_text(
                        f"{self.base_text} {self.current_percentage}%{dots_states[current_index]}"
                    )
                    current_index = (current_index + 1) % len(dots_states)
                    await asyncio.sleep(update_interval)
                except Exception:
                    # Message might be deleted or invalid
                    break
        
        self.current_task = asyncio.create_task(animate())
        return self.progress_message
    
    async def update_percentage(self, percentage: int):
        """Update just the percentage value while animation continues"""
        self.current_percentage = percentage