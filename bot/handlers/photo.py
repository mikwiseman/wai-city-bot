from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.user_states import UserStates
from bot.services.pastvu import PastVuAPI
from bot.services.openai_service import OpenAIService
from bot.keyboards.inline import get_photo_actions_keyboard, get_location_keyboard

router = Router()


async def process_location(message: Message, state: FSMContext, lat: float, lon: float):
    """Process location and find photos"""
    # Get photos from PastVu
    photos = await PastVuAPI.get_nearest_photos(lat, lon)
    
    if not photos:
        await message.answer(
            "❌ No historical photos found for this location.\n"
            "Please try another location.",
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
            "❌ No more photos available for this location.\n"
            "Please try another location.",
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
        f"📷 {selected_photo.get('title', 'Historical photo')}\n"
        f"📅 Year: {selected_photo.get('year', 'Unknown')}\n"
        f"📍 Location: {selected_photo.get('geo', [lat, lon])}"
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
        "Please share your new location:",
        reply_markup=get_location_keyboard()
    )


@router.callback_query(F.data == "another_photo")
async def handle_another_photo(callback: CallbackQuery, state: FSMContext):
    """Handle request for another photo"""
    await callback.answer()
    
    data = await state.get_data()
    lat = data.get("latitude")
    lon = data.get("longitude")
    
    await callback.message.answer("🔍 Searching for another photo...")
    await process_location(callback.message, state, lat, lon)