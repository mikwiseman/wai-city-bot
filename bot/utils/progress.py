import asyncio
from typing import Optional
from aiogram.types import Message


class ProgressAnimator:
    """Simple utility class for animated progress messages"""
    
    def __init__(self):
        self.dots_index = 0
        self.emoji_index = 0
        self.dots_states = ["", ".", "..", "..."]
        self.emoji_patterns = {
            "search": ["🔍", "🔎"],
            "clock": ["⏳", "⌛"],
            "loading": ["🔄", "🔃"],
            "photo": ["📸", "📷"],
            "video": ["🎬", "🎥"]
        }
    
    async def send_progress_message(
        self, 
        message: Message, 
        text: str,
        emoji_pattern: Optional[str] = None
    ) -> Message:
        """Send initial progress message"""
        # Auto-detect emoji pattern from text
        if emoji_pattern is None and text:
            if "🔍" in text or "🔎" in text:
                emoji_pattern = "search"
            elif "📸" in text or "📷" in text:
                emoji_pattern = "photo"
            elif "🎬" in text or "🎥" in text:
                emoji_pattern = "video"
            elif "⏳" in text or "⌛" in text:
                emoji_pattern = "clock"
        
        # Store pattern for updates
        self.current_emoji_pattern = emoji_pattern
        self.base_text = text
        
        # Clean text if we'll be rotating emojis
        if emoji_pattern and emoji_pattern in self.emoji_patterns:
            emojis = self.emoji_patterns[emoji_pattern]
            clean_text = text
            for emoji in emojis:
                clean_text = clean_text.replace(emoji, "").strip()
            self.clean_text = clean_text
            # Start with first emoji
            initial_text = f"{emojis[0]} {clean_text}"
        else:
            self.clean_text = text
            initial_text = text
        
        # Reset indices
        self.dots_index = 0
        self.emoji_index = 0
        
        # Send message
        return await message.answer(initial_text)
    
    async def update_animation_frame(self, progress_message: Message) -> bool:
        """Update message with next animation frame"""
        try:
            # Get current dots state
            dots = self.dots_states[self.dots_index]
            
            # Build animated text
            if self.current_emoji_pattern and self.current_emoji_pattern in self.emoji_patterns:
                emojis = self.emoji_patterns[self.current_emoji_pattern]
                emoji = emojis[self.emoji_index]
                animated_text = f"{emoji} {self.clean_text}{dots}"
            else:
                animated_text = f"{self.base_text}{dots}"
            
            # Update message
            await progress_message.edit_text(animated_text)
            
            # Update indices for next frame
            self.dots_index = (self.dots_index + 1) % len(self.dots_states)
            if self.current_emoji_pattern:
                self.emoji_index = (self.emoji_index + 1) % len(self.emoji_patterns.get(self.current_emoji_pattern, []))
            
            return True
        except Exception:
            # Message might be deleted or can't be edited
            return False
    
    async def animate_until_complete(
        self,
        progress_message: Message,
        operation,
        update_interval: float = 1.0
    ):
        """Animate progress message until operation completes"""
        # Create animation task
        async def animate():
            while True:
                success = await self.update_animation_frame(progress_message)
                if not success:
                    break
                await asyncio.sleep(update_interval)
        
        # Run operation and animation concurrently
        animation_task = asyncio.create_task(animate())
        
        try:
            # Wait for operation to complete
            result = await operation
            return result
        finally:
            # Stop animation
            animation_task.cancel()
            try:
                await animation_task
            except asyncio.CancelledError:
                pass


class PercentageProgressAnimator(ProgressAnimator):
    """Progress animator with percentage support"""
    
    def __init__(self):
        super().__init__()
        self.current_percentage = 0
    
    async def send_progress_message_with_percentage(
        self,
        message: Message,
        text: str,
        initial_percentage: int = 0,
        emoji_pattern: str = "clock"
    ) -> Message:
        """Send initial progress message with percentage"""
        self.current_percentage = initial_percentage
        self.current_emoji_pattern = emoji_pattern
        self.base_text = text
        
        # Clean text if we'll be rotating emojis
        if emoji_pattern in self.emoji_patterns:
            emojis = self.emoji_patterns[emoji_pattern]
            clean_text = text
            for emoji in emojis:
                clean_text = clean_text.replace(emoji, "").strip()
            self.clean_text = clean_text
            # Start with first emoji
            initial_text = f"{emojis[0]} {clean_text} {initial_percentage}%"
        else:
            self.clean_text = text
            initial_text = f"{text} {initial_percentage}%"
        
        # Reset indices
        self.dots_index = 0
        self.emoji_index = 0
        
        # Send message
        return await message.answer(initial_text)
    
    async def update_percentage(self, percentage: int):
        """Update the percentage value"""
        self.current_percentage = percentage
    
    async def update_animation_frame_with_percentage(self, progress_message: Message) -> bool:
        """Update message with next animation frame and current percentage"""
        try:
            # Get current dots state
            dots = self.dots_states[self.dots_index]
            
            # Build animated text
            if self.current_emoji_pattern in self.emoji_patterns:
                emojis = self.emoji_patterns[self.current_emoji_pattern]
                emoji = emojis[self.emoji_index]
                animated_text = f"{emoji} {self.clean_text} {self.current_percentage}%{dots}"
            else:
                animated_text = f"{self.base_text} {self.current_percentage}%{dots}"
            
            # Update message
            await progress_message.edit_text(animated_text)
            
            # Update indices for next frame
            self.dots_index = (self.dots_index + 1) % len(self.dots_states)
            if self.current_emoji_pattern:
                self.emoji_index = (self.emoji_index + 1) % len(self.emoji_patterns.get(self.current_emoji_pattern, []))
            
            return True
        except Exception:
            # Message might be deleted or can't be edited
            return False