from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.user_states import UserStates
from bot.services.pastvu import PastVuAPI
from bot.services.runway import RunwayAPI
from bot.keyboards.inline import get_photo_actions_keyboard
import asyncio

router = Router()


@router.callback_query(F.data == "make_video")
async def handle_make_video(callback: CallbackQuery, state: FSMContext):
    """Handle video generation request"""
    await callback.answer()
    await state.set_state(UserStates.generating_video)
    
    data = await state.get_data()
    current_photo = data.get("current_photo")
    
    if not current_photo:
        await callback.message.answer("❌ Error: No photo selected")
        return
    
    # Get photo URL
    photo_url = PastVuAPI.get_photo_url(current_photo.get("file"))
    
    # Start video generation
    await callback.message.answer("🎬 Starting video generation...")
    
    # Create video task
    task_id = await RunwayAPI.create_video_from_image(photo_url)
    
    if not task_id:
        await callback.message.answer("❌ Failed to start video generation. Please try again.")
        await state.set_state(UserStates.selecting_photo)
        return
    
    # Progress message
    progress_message = await callback.message.answer("⏳ Progress: 0%")
    
    # Progress callback
    async def update_progress(progress):
        try:
            progress_percent = int(float(progress) * 100)
            await progress_message.edit_text(f"⏳ Progress: {progress_percent}%")
        except:
            pass
    
    # Wait for video with progress updates
    video_url = await RunwayAPI.wait_for_video(task_id, update_progress)
    
    if video_url:
        await progress_message.edit_text("✅ Video generation complete!")
        
        # Send video
        await callback.message.answer_video(
            video=video_url,
            caption=(
                f"🎥 Video generated from: {current_photo.get('title', 'Historical photo')}\n"
                f"📅 Year: {current_photo.get('year', 'Unknown')}"
            )
        )
        
        # Offer options to continue
        await callback.message.answer(
            "What would you like to do next?",
            reply_markup=get_photo_actions_keyboard()
        )
    else:
        await progress_message.edit_text("❌ Video generation failed. Please try again.")
    
    await state.set_state(UserStates.selecting_photo)