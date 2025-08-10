from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.utils.config import WEBAPP_URL


def get_location_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard with location request button"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="🗺️ Выбрать место на карте", 
                web_app=WebAppInfo(url=f"{WEBAPP_URL}/map_location_picker.html")
            )],
            [KeyboardButton(text="🎲 Случайная локация")],
            [KeyboardButton(text="📝 Ввести адрес")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_simple_location_keyboard() -> ReplyKeyboardMarkup:
    """Get simplified location keyboard"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(
                text="🗺️ Выбрать место на карте", 
                web_app=WebAppInfo(url=f"{WEBAPP_URL}/map_location_picker.html")
            )],
            [KeyboardButton(text="🎲 Случайная локация")],
            [KeyboardButton(text="📝 Ввести адрес")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_location_options_keyboard(lat: float, lon: float) -> InlineKeyboardMarkup:
    """Get inline keyboard for location options when user shares location"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Использовать эту локацию", 
            callback_data=f"use_location:{lat}:{lon}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🗺 Изменить место (отправить новое)", 
            callback_data="request_new_location"
        )
    )
    return builder.as_markup()


def get_photo_actions_keyboard() -> InlineKeyboardMarkup:
    """Get inline keyboard for photo actions"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📍 Отправить новое место", callback_data="new_location")
    )
    builder.row(
        InlineKeyboardButton(text="🖼 Другое фото", callback_data="another_photo")
    )
    builder.row(
        InlineKeyboardButton(text="🎬 Создать видео", callback_data="make_video")
    )
    return builder.as_markup()