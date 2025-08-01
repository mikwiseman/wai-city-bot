from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
import json
from bot.states.user_states import UserStates
from bot.keyboards.inline import get_location_keyboard, get_location_options_keyboard, get_simple_location_keyboard
from bot.handlers.photo import process_location
from bot.services.openai_service import OpenAIService
from bot.utils.progress import ProgressAnimator
import random

router = Router()


@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    """Handle /start command"""
    await state.set_state(UserStates.waiting_for_location)
    await message.answer(
        "🏛️ Добро пожаловать! Я помогу вам найти исторические фотографии любых мест и создать из них видео.\n\n"
        "🗺️ Выберите место на интерактивной карте или введите адрес - и я найду старинные фотографии этого места!",
        reply_markup=get_location_keyboard()
    )


@router.message(F.text == "📝 Ввести адрес")
async def handle_address_input(message: Message, state: FSMContext):
    """Handle address input request"""
    await state.set_state(UserStates.waiting_for_location)
    await message.answer(
        "📝 Введите адрес места, которое вы хотите найти:\n\n"
        "Например:\n"
        "• Красная площадь, Москва\n"
        "• Times Square, New York\n"
        "• Эйфелева башня, Париж"
    )


@router.message(F.text == "🎲 Случайная локация")
async def handle_random_location(message: Message, state: FSMContext):
    """Generate random location coordinates"""
    # Генерируем случайные координаты
    # Широта от -90 до 90
    lat = random.uniform(-90, 90)
    # Долгота от -180 до 180
    lon = random.uniform(-180, 180)
    
    # Отправляем локацию как venue
    await message.answer_venue(
        latitude=lat,
        longitude=lon,
        title="🎲 Случайная локация",
        address=f"Координаты: {lat:.6f}, {lon:.6f}"
    )
    
    # Спрашиваем, что делать с этой локацией
    await message.answer(
        "Сгенерирована случайная локация! Что вы хотите с ней сделать?",
        reply_markup=get_location_options_keyboard(lat, lon)
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
        title="📍 Выбранное место",
        address=f"Координаты: {lat:.6f}, {lon:.6f}"
    )
    
    # Ask user what they want to do with this location
    await message.answer(
        "Что вы хотите сделать с этим местом?",
        reply_markup=get_location_options_keyboard(lat, lon)
    )


@router.message(F.web_app_data)
async def handle_web_app_data(message: Message, state: FSMContext):
    """Handle data from Web App (map location picker)"""
    try:
        # Parse the JSON data from Web App
        data = json.loads(message.web_app_data.data)
        lat = data["latitude"]
        lon = data["longitude"]
        
        # Update state with location data
        await state.update_data(latitude=lat, longitude=lon, shown_photos=[])
        await state.set_state(UserStates.selecting_photo)
        
        # Send the location as a venue to show on Telegram's map
        await message.answer_venue(
            latitude=lat,
            longitude=lon,
            title="🗺️ Выбранное на карте место",
            address=f"Координаты: {lat:.6f}, {lon:.6f}"
        )
        
        # Start searching for photos with animated progress
        animator = ProgressAnimator()
        progress_msg = await animator.start_animated_progress(
            message, 
            "🔍 Ищу исторические фотографии"
        )
        
        await process_location(message, state, lat, lon)
        
        animator.stop()
        await progress_msg.delete()
        
    except (json.JSONDecodeError, KeyError):
        await message.answer(
            "❌ Ошибка при обработке данных карты. Попробуйте выбрать место заново.",
            reply_markup=get_simple_location_keyboard()
        )


@router.callback_query(F.data == "new_location")
async def handle_new_location_from_photo(callback: CallbackQuery, state: FSMContext):
    """Handle when user wants to send new location from photo actions"""
    await state.set_state(UserStates.waiting_for_location)
    await callback.message.answer(
        "📍 Пожалуйста, выберите новое место:",
        reply_markup=get_simple_location_keyboard()
    )
    await callback.answer()


@router.message(UserStates.waiting_for_location, F.text)
async def handle_address_text(message: Message, state: FSMContext):
    """Handle text message as address input"""
    if message.text.startswith("/"):
        # Ignore commands when waiting for location
        return
    
    address = message.text.strip()
    
    # Start animated progress
    animator = ProgressAnimator()
    progress_msg = await animator.start_animated_progress(
        message,
        f"🔍 Ищу место: {address}\n\nОпределяю координаты"
    )
    
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
            title="📍 Место найдено",
            address=address
        )
        
        # Continue with photo search animation
        animator.stop()
        await progress_msg.delete()
        
        # Start new animation for photo search
        photo_animator = ProgressAnimator()
        photo_progress_msg = await photo_animator.start_animated_progress(
            message,
            "📸 Ищу исторические фотографии"
        )
        
        await process_location(message, state, lat, lon)
        
        photo_animator.stop()
        await photo_progress_msg.delete()
    else:
        animator.stop()
        await progress_msg.delete()
        
        await message.answer(
            "❌ К сожалению, я не смог найти координаты этого адреса.\n\n"
            "Попробуйте:\n"
            "• Более точный адрес\n"
            "• Указать город и страну\n"
            "• Или используйте интерактивную карту:",
            reply_markup=get_simple_location_keyboard()
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
        title="📍 Использую это место",
        address=f"Координаты: {lat:.6f}, {lon:.6f}"
    )
    
    # Start animated progress for photo search
    animator = ProgressAnimator()
    progress_msg = await animator.start_animated_progress(
        callback.message,
        "🔍 Ищу исторические фотографии"
    )
    
    # Delete the options message
    await callback.message.delete()
    
    # Process the location
    await process_location(callback.message, state, lat, lon)
    
    # Stop animation
    animator.stop()
    await progress_msg.delete()
    
    await callback.answer()


@router.callback_query(F.data == "request_new_location")
async def handle_request_new_location(callback: CallbackQuery, state: FSMContext):
    """Handle when user wants to change location"""
    await state.set_state(UserStates.waiting_for_location)
    await callback.message.answer(
        "📍 Пожалуйста, выберите новое место:",
        reply_markup=get_simple_location_keyboard()
    )
    await callback.answer()