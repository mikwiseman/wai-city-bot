from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_location_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard with location request button"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Выбрать место на карте", request_location=True)],
            [KeyboardButton(text="🎲 Случайная локация")],
            [KeyboardButton(text="📎 Использовать меню вложений")],
            [KeyboardButton(text="📱 Как выбрать любое место")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return keyboard


def get_attachment_guide_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard for attachment menu guidance"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Покажи как использовать меню вложений")],
            [KeyboardButton(text="🔙 Вернуться к кнопке локации")]
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
            text="✅ Использовать текущую локацию", 
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