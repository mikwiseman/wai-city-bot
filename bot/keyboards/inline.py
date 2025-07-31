from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_location_keyboard() -> ReplyKeyboardMarkup:
    """Get keyboard with location request button"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📍 Share Location", request_location=True)]
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
            text="✅ Use this location", 
            callback_data=f"use_location:{lat}:{lon}"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="📍 Open in Google Maps", 
            url=f"https://www.google.com/maps?q={lat},{lon}&z=16"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🗺 Change location (send new one)", 
            callback_data="request_new_location"
        )
    )
    return builder.as_markup()


def get_photo_actions_keyboard() -> InlineKeyboardMarkup:
    """Get inline keyboard for photo actions"""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📍 Send new location", callback_data="new_location")
    )
    builder.row(
        InlineKeyboardButton(text="🖼 Another photo", callback_data="another_photo")
    )
    builder.row(
        InlineKeyboardButton(text="🎬 Make video", callback_data="make_video")
    )
    return builder.as_markup()