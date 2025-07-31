from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from bot.states.user_states import UserStates
from bot.keyboards.inline import get_location_keyboard, get_location_options_keyboard, get_attachment_guide_keyboard
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
        "• Tap location button → Choose **'Send Selected Location'**\n"
        "• Use 📎 attachment menu for more control\n"
        "• Or type an address (e.g., 'Times Square, New York')\n\n"
        "⚠️ **Important**: Choose 'Send Selected Location' to pick ANY place on the map!",
        reply_markup=get_location_keyboard(),
        parse_mode="Markdown"
    )


@router.message(F.text == "📱 How to pick any location")
async def handle_location_help(message: Message):
    """Show help for picking any location on map"""
    await message.answer(
        "📍 **How to pick ANY location (not just current):**\n\n"
        "**Option 1 - Using Location Button:**\n"
        "1. Tap '📍 Pick Location on Map' button\n"
        "2. **IMPORTANT**: Choose **'Send Selected Location'** ✅\n"
        "   (NOT 'Send My Current Location')\n"
        "3. The map opens - navigate anywhere!\n"
        "4. Tap to place pin at desired location\n"
        "5. Tap 'Send Selected Location'\n\n"
        "**Option 2 - Using Attachment Menu:**\n"
        "1. Tap 📎 (paperclip) in message field\n"
        "2. Select 'Location'\n"
        "3. Choose **'Send Selected Location'**\n"
        "4. Navigate map and pick any place\n\n"
        "⚠️ **Common mistake**: Don't use 'Send My Current Location' - that only sends GPS position!",
        parse_mode="Markdown"
    )


@router.message(F.text == "📎 Use Attachment Menu Instead")
async def handle_attachment_menu_guide(message: Message):
    """Guide user to use attachment menu"""
    await message.answer(
        "📎 **Using Attachment Menu for Better Control:**\n\n"
        "1. Look for 📎 (paperclip) next to message field\n"
        "2. Tap it and select **'Location'**\n"
        "3. You'll see 3 options:\n"
        "   • Send My Current Location (GPS only)\n"
        "   • **Send Selected Location** ← USE THIS! ✅\n"
        "   • Share Live Location\n\n"
        "4. Choose **'Send Selected Location'**\n"
        "5. Navigate the map freely\n"
        "6. Tap to drop pin anywhere\n"
        "7. Send the selected location\n\n"
        "This gives you full control over location selection! 🗺️",
        reply_markup=get_attachment_guide_keyboard(),
        parse_mode="Markdown"
    )


@router.message(F.text == "📱 Show me how to use attachment menu")
async def handle_attachment_detailed_guide(message: Message):
    """Show detailed attachment menu guide"""
    await message.answer(
        "📍 **Step-by-Step Visual Guide:**\n\n"
        "1️⃣ Find the 📎 icon at bottom of chat\n"
        "2️⃣ Tap 📎 → See menu popup\n"
        "3️⃣ Select 'Location' 📍\n"
        "4️⃣ **CRITICAL**: Select 'Send Selected Location'\n"
        "5️⃣ Map opens → Zoom out to see more\n"
        "6️⃣ Navigate to desired area\n"
        "7️⃣ Tap once to place pin 📌\n"
        "8️⃣ Tap 'Send Selected Location' button\n\n"
        "✨ **Pro tip**: Pinch to zoom, drag to move around the map!",
        parse_mode="Markdown"
    )


@router.message(F.text == "🔙 Back to location button")
async def handle_back_to_location(message: Message, state: FSMContext):
    """Go back to location button keyboard"""
    await message.answer(
        "Back to location options. Remember to choose 'Send Selected Location'!",
        reply_markup=get_location_keyboard()
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
        "💡 **Reminder**: Use 'Send Selected Location' option to pick ANY place on the map!\n"
        "Or use the attachment menu for more control.",
        reply_markup=get_location_keyboard(),
        parse_mode="Markdown"
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
            "• Or use 'Send Selected Location' from location menu:",
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
        "💡 **Reminder**: Use 'Send Selected Location' option to pick ANY place on the map!\n"
        "Or use the attachment menu for more control.",
        reply_markup=get_location_keyboard(),
        parse_mode="Markdown"
    )
    await callback.answer()