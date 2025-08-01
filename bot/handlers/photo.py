from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.user_states import UserStates
from bot.services.pastvu import PastVuAPI
from bot.services.openai_service import OpenAIService
from bot.keyboards.inline import get_photo_actions_keyboard, get_location_keyboard
from bot.utils.progress import ProgressAnimator

router = Router()


async def process_location(message: Message, state: FSMContext, lat: float, lon: float):
    """Process location and find photos"""
    # Get photos from PastVu
    photos = await PastVuAPI.get_nearest_photos(lat, lon)
    
    if not photos:
        await message.answer(
            "❌ Для этого места не найдено исторических фотографий.\n"
            "Пожалуйста, попробуйте другое место.",
            reply_markup=get_location_keyboard()
        )
        await state.set_state(UserStates.waiting_for_location)
        return
    
    # Get state data
    data = await state.get_data()
    shown_photos = data.get("shown_photos", [])
    
    # Select best photo using OpenAI
    selected_photo = await OpenAIService.select_best_photo(photos, shown_photos)
    
    if not selected_photo:
        await message.answer(
            "❌ Больше нет фотографий для этого места.\n"
            "Пожалуйста, попробуйте другое место.",
            reply_markup=get_location_keyboard()
        )
        await state.set_state(UserStates.waiting_for_location)
        return
    
    # Update shown photos
    shown_photos.append(selected_photo.get("cid"))
    await state.update_data(
        shown_photos=shown_photos,
        current_photo=selected_photo,
        all_photos=photos
    )
    
    # Send photo
    photo_url = PastVuAPI.get_photo_url(selected_photo.get("file"))
    caption = (
        f"📷 {selected_photo.get('title', 'Историческая фотография')}\n"
        f"📅 Год: {selected_photo.get('year', 'Неизвестно')}\n"
        f"📍 Место: {selected_photo.get('geo', [lat, lon])}"
    )
    
    await message.answer_photo(
        photo=photo_url,
        caption=caption,
        reply_markup=get_photo_actions_keyboard()
    )


@router.callback_query(F.data == "new_location")
async def handle_new_location(callback: CallbackQuery, state: FSMContext):
    """Handle new location request"""
    await callback.answer()
    await state.clear()
    await state.set_state(UserStates.waiting_for_location)
    await callback.message.answer(
        "Пожалуйста, отправьте новое место:",
        reply_markup=get_location_keyboard()
    )


@router.callback_query(F.data == "another_photo")
async def handle_another_photo(callback: CallbackQuery, state: FSMContext):
    """Handle request for another photo"""
    await callback.answer()
    
    data = await state.get_data()
    lat = data.get("latitude")
    lon = data.get("longitude")
    
    # Start animated progress
    animator = ProgressAnimator()
    progress_msg = await animator.start_animated_progress(
        callback.message,
        "🔍 Ищу другую фотографию"
    )
    
    await process_location(callback.message, state, lat, lon)
    
    # Stop animation
    animator.stop()
    await progress_msg.delete()