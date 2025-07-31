from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.user_states import UserStates
from bot.keyboards.inline import get_location_keyboard, get_location_options_keyboard
from bot.handlers.photo import process_location
from bot.services.openai_service import OpenAIService

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.set_state(UserStates.waiting_for_location)
    await message.answer(
        "Welcome! I can help you find historical photos of places and create videos from them.\n\n"
        "You can:\n"
        "• Tap the button to open Telegram's map\n"
        "• Navigate and drop a pin anywhere on the map\n"
        "• Or type an address (e.g., 'Times Square, New York')\n\n"
        "💡 Tip: You can share location anytime during our chat!",
        reply_markup=get_location_keyboard()
    )


@router.message(F.text == "📱 How to pick any location")
async def handle_location_help(message: Message):
    """Show help for picking any location on map"""
    await message.answer(
        "📍 **How to pick ANY location on Telegram's map:**\n\n"
        "1. Tap '📍 Pick Location on Map' button\n"
        "2. The map will open with your current location\n"
        "3. **Navigate to any place** by:\n"
        "   • Pinching to zoom in/out\n"
        "   • Dragging to move around\n"
        "4. **Touch and hold** to drop a pin anywhere\n"
        "5. Tap 'Send Selected Location'\n\n"
        "💡 You're not limited to your current location - explore and pick any place in the world!",
        parse_mode="Markdown"
    )


@router.message(F.location)
async def handle_location(message: Message, state: FSMContext):
    """Handle shared location from any state"""
    lat = message.location.latitude
    lon = message.location.longitude
    
    # Send the location as a venue to show on Telegram's map
    await message.answer_venue(
        latitude=lat,
        longitude=lon,
        title="📍 Selected Location",
        address=f"Coordinates: {lat:.6f}, {lon:.6f}"
    )
    
    # Ask user what they want to do with this location
    await message.answer(
        "What would you like to do with this location?",
        reply_markup=get_location_options_keyboard(lat, lon)
    )


@router.callback_query(F.data == "new_location")
async def handle_new_location_from_photo(callback: CallbackQuery, state: FSMContext):
    """Handle when user wants to send new location from photo actions"""
    await state.set_state(UserStates.waiting_for_location)
    await callback.message.answer(
        "Please pick a new location:\n\n"
        "💡 Remember: You can navigate the map and drop a pin anywhere!",
        reply_markup=get_location_keyboard()
    )
    await callback.answer()


@router.message(UserStates.waiting_for_location, F.text)
async def handle_address_text(message: Message, state: FSMContext):
    """Handle text message as address input"""
    if message.text.startswith("/"):
        # Ignore commands when waiting for location
        return
    
    address = message.text.strip()
    await message.answer(f"🔍 Searching for location: {address}\n\nPlease wait while I find the coordinates...")
    
    # Use OpenAI to geocode the address
    coordinates = await OpenAIService.geocode_address(address)
    
    if coordinates:
        lat = coordinates["latitude"]
        lon = coordinates["longitude"]
        
        await state.update_data(latitude=lat, longitude=lon, shown_photos=[])
        await state.set_state(UserStates.selecting_photo)
        
        # Send the found location as a venue
        await message.answer_venue(
            latitude=lat,
            longitude=lon,
            title="📍 Location found",
            address=address
        )
        
        await message.answer("Searching for historical photos...")
        await process_location(message, state, lat, lon)
    else:
        await message.answer(
            "❌ Sorry, I couldn't find the coordinates for that address.\n\n"
            "Please try:\n"
            "• A more specific address\n"
            "• Including city and country\n"
            "• Or pick a location on the map:",
            reply_markup=get_location_keyboard()
        )


@router.callback_query(F.data.startswith("use_location:"))
async def handle_use_location(callback: CallbackQuery, state: FSMContext):
    """Handle when user chooses to use the shared location"""
    # Extract coordinates from callback data
    parts = callback.data.split(":")
    lat = float(parts[1])
    lon = float(parts[2])
    
    # Update state with location data
    await state.update_data(latitude=lat, longitude=lon, shown_photos=[])
    await state.set_state(UserStates.selecting_photo)
    
    # Send venue to show the location being used
    await callback.message.answer_venue(
        latitude=lat,
        longitude=lon,
        title="📍 Using this location",
        address=f"Searching for historical photos..."
    )
    
    # Delete the options message
    await callback.message.delete()
    
    # Process the location
    await process_location(callback.message, state, lat, lon)
    await callback.answer()


@router.callback_query(F.data == "request_new_location")
async def handle_request_new_location(callback: CallbackQuery, state: FSMContext):
    """Handle when user wants to change location"""
    await state.set_state(UserStates.waiting_for_location)
    await callback.message.answer(
        "Please pick a new location:\n\n"
        "💡 Remember: You can navigate the map and drop a pin anywhere!",
        reply_markup=get_location_keyboard()
    )
    await callback.answer()