from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from bot.states.user_states import UserStates
from bot.keyboards.inline import get_location_keyboard
from bot.handlers.photo import process_location

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.set_state(UserStates.waiting_for_location)
    await message.answer(
        "Welcome! I can help you find historical photos of places and create videos from them.\n\n"
        "Please share your location or use the button below:",
        reply_markup=get_location_keyboard()
    )


@router.message(UserStates.waiting_for_location, F.location)
async def handle_location(message: Message, state: FSMContext):
    """Handle shared location"""
    lat = message.location.latitude
    lon = message.location.longitude
    
    await state.update_data(latitude=lat, longitude=lon, shown_photos=[])
    await state.set_state(UserStates.selecting_photo)
    
    await message.answer(f"📍 Location received: {lat:.6f}, {lon:.6f}\n\nSearching for historical photos...")
    await process_location(message, state, lat, lon)