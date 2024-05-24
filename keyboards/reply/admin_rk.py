from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardMarkup


main_menu = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Настройки'), KeyboardButton(text='Текущие квартиранты')]
], resize_keyboard=True)
