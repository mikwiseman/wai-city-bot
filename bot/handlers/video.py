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
        await callback.message.answer("❌ Ошибка: Фото не выбрано")
        return
    
    # Get photo URL
    photo_url = PastVuAPI.get_photo_url(current_photo.get("file"))
    
    # Start video generation
    await callback.message.answer("🎬 Начинаю создание видео...")
    
    # Create video task
    task_id = await RunwayAPI.create_video_from_image(photo_url)
    
    if not task_id:
        await callback.message.answer("❌ Не удалось начать создание видео. Пожалуйста, попробуйте ещё раз.")
        await state.set_state(UserStates.selecting_photo)
        return
    
    # Progress message
    progress_message = await callback.message.answer("⏳ Прогресс: 0%")
    
    # Progress callback
    async def update_progress(progress):
        try:
            progress_percent = int(float(progress) * 100)
            await progress_message.edit_text(f"⏳ Прогресс: {progress_percent}%")
        except:
            pass
    
    # Wait for video with progress updates
    video_url = await RunwayAPI.wait_for_video(task_id, update_progress)
    
    if video_url:
        await progress_message.edit_text("✅ Создание видео завершено!")
        
        # Send video
        await callback.message.answer_video(
            video=video_url,
            caption=(
                f"🎥 Видео создано из: {current_photo.get('title', 'Историческая фотография')}\n"
                f"📅 Год: {current_photo.get('year', 'Неизвестно')}"
            )
        )
        
        # Offer options to continue
        await callback.message.answer(
            "Что вы хотите сделать дальше?",
            reply_markup=get_photo_actions_keyboard()
        )
    else:
        await progress_message.edit_text("❌ Создание видео не удалось. Пожалуйста, попробуйте ещё раз.")
    
    await state.set_state(UserStates.selecting_photo)