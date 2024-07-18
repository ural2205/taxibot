from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

class TaxiCallback(CallbackData, prefix = 'call'):
    action: str

