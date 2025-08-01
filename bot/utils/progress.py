import asyncio
import time
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
        self.start_time = 0
        self.emoji_patterns = {
            "search": ["🔍", "🔎"],
            "clock": ["⏳", "⌛"],
            "loading": ["🔄", "🔃"],
            "photo": ["📸", "📷"],
            "video": ["🎬", "🎥"]
        }
    
    async def start_animated_progress(
        self, 
        message: Message, 
        base_text: str,
        update_interval: float = 0.5,
        emoji_pattern: str = None
    ) -> Message:
        """Start animated progress with dots and optional emoji rotation"""
        self.is_running = True
        self.start_time = time.time()
        self.base_text = base_text
        
        # Extract emoji from base_text if not specified
        if emoji_pattern is None and base_text:
            if "🔍" in base_text or "🔎" in base_text:
                emoji_pattern = "search"
            elif "📸" in base_text or "📷" in base_text:
                emoji_pattern = "photo"
            elif "🎬" in base_text or "🎥" in base_text:
                emoji_pattern = "video"
            elif "⏳" in base_text or "⌛" in base_text:
                emoji_pattern = "clock"
        
        # Store the message as instance variable
        self.progress_message = await message.answer(base_text)
        
        async def animate():
            dots_states = ["", ".", "..", "..."]
            dots_index = 0
            emoji_index = 0
            emojis = self.emoji_patterns.get(emoji_pattern, []) if emoji_pattern else []
            
            # Remove emoji from base text if we're rotating it
            clean_text = base_text
            if emojis:
                for emoji in emojis:
                    clean_text = clean_text.replace(emoji, "").strip()
            
            while self.is_running:
                try:
                    # Build the animated text
                    if emojis:
                        animated_text = f"{emojis[emoji_index]} {clean_text}{dots_states[dots_index]}"
                    else:
                        animated_text = f"{base_text}{dots_states[dots_index]}"
                    
                    await self.progress_message.edit_text(animated_text)
                    
                    # Update indices
                    dots_index = (dots_index + 1) % len(dots_states)
                    if emojis:
                        emoji_index = (emoji_index + 1) % len(emojis)
                    
                    await asyncio.sleep(update_interval)
                except Exception:
                    # Message might be deleted or invalid
                    break
        
        self.current_task = asyncio.create_task(animate())
        # Ensure first frame is shown
        await asyncio.sleep(0.1)
        return self.progress_message
    
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
        update_interval: float = 0.5,
        emoji_pattern: str = "clock"
    ) -> Message:
        """Start animated progress with percentage and emoji rotation"""
        self.is_running = True
        self.start_time = time.time()
        self.current_percentage = initial_percentage
        self.base_text = base_text
        
        # Extract emoji pattern from base_text if not specified
        if emoji_pattern == "clock" and base_text:
            if "🔍" in base_text or "🔎" in base_text:
                emoji_pattern = "search"
            elif "📸" in base_text or "📷" in base_text:
                emoji_pattern = "photo"
            elif "🎬" in base_text or "🎥" in base_text:
                emoji_pattern = "video"
        
        self.progress_message = await message.answer(f"{base_text} {initial_percentage}%")
        
        async def animate():
            dots_states = ["", ".", "..", "..."]
            dots_index = 0
            emoji_index = 0
            emojis = self.emoji_patterns.get(emoji_pattern, ["⏳", "⌛"])
            
            # Remove emoji from base text if we're rotating it
            clean_text = base_text
            for emoji in emojis:
                clean_text = clean_text.replace(emoji, "").strip()
            
            while self.is_running:
                try:
                    animated_text = f"{emojis[emoji_index]} {clean_text} {self.current_percentage}%{dots_states[dots_index]}"
                    await self.progress_message.edit_text(animated_text)
                    
                    # Update indices
                    dots_index = (dots_index + 1) % len(dots_states)
                    emoji_index = (emoji_index + 1) % len(emojis)
                    
                    await asyncio.sleep(update_interval)
                except Exception:
                    # Message might be deleted or invalid
                    break
        
        self.current_task = asyncio.create_task(animate())
        # Ensure first frame is shown
        await asyncio.sleep(0.1)
        return self.progress_message
    
    async def update_percentage(self, percentage: int):
        """Update just the percentage value while animation continues"""
        self.current_percentage = percentage
    
    async def ensure_minimum_display_time(self, min_seconds: float = 2.0):
        """Ensure the progress was shown for minimum time"""
        if self.start_time > 0:
            elapsed = time.time() - self.start_time
            if elapsed < min_seconds:
                await asyncio.sleep(min_seconds - elapsed)