from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.user_states import UserStates
from bot.services.pastvu import PastVuAPI
from bot.services.runway import RunwayAPI
from bot.keyboards.inline import get_photo_actions_keyboard
from bot.utils.progress import ProgressAnimator, PercentageProgressAnimator
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
    
    # Start video generation with animated progress
    animator = ProgressAnimator()
    init_progress_msg = await animator.send_progress_message(
        callback.message,
        "🎬 Начинаю создание видео"
    )
    
    # Create video task with animation
    task_id = await animator.animate_until_complete(
        init_progress_msg,
        RunwayAPI.create_video_from_image(photo_url),
        update_interval=0.5
    )
    
    if not task_id:
        await init_progress_msg.delete()
        await callback.message.answer("❌ Не удалось начать создание видео. Пожалуйста, попробуйте ещё раз.")
        await state.set_state(UserStates.selecting_photo)
        return
    
    # Delete initial message
    await init_progress_msg.delete()
    
    # Start animated progress with percentage
    progress_animator = PercentageProgressAnimator()
    progress_message = await progress_animator.send_progress_message_with_percentage(
        callback.message,
        "⏳ Обработка видео:",
        initial_percentage=0,
        emoji_pattern="clock"
    )
    
    # Animation task for percentage updates
    async def animate_progress():
        while True:
            success = await progress_animator.update_animation_frame_with_percentage(progress_message)
            if not success:
                break
            await asyncio.sleep(0.5)
    
    # Progress callback - just update percentage
    async def update_progress(progress):
        try:
            progress_percent = int(float(progress) * 100)
            await progress_animator.update_percentage(progress_percent)
        except:
            pass
    
    # Start animation task
    animation_task = asyncio.create_task(animate_progress())
    
    try:
        # Wait for video with progress updates
        video_url = await RunwayAPI.wait_for_video(task_id, update_progress)
    finally:
        # Stop animation
        animation_task.cancel()
        try:
            await animation_task
        except asyncio.CancelledError:
            pass
    
    if video_url:
        # Update to completion message
        try:
            await progress_message.edit_text("✅ Создание видео завершено!")
        except:
            pass
        
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
        # Update to error message
        try:
            await progress_message.edit_text("❌ Создание видео не удалось. Пожалуйста, попробуйте ещё раз.")
        except:
            pass
    
    await state.set_state(UserStates.selecting_photo)