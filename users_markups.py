from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.filters.callback_data import CallbackData
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove

class MyCallback(CallbackData, prefix = 'call'):
    action: str

class TaxiCallback(CallbackData, prefix = 'order'):
    id: int
    action: str

class DelMessageCallback(CallbackData, prefix = 'order'):
    message_id: int
    chat_id: int

start_markup = InlineKeyboardBuilder([[
    InlineKeyboardButton(text= 'Заказать такси', callback_data=MyCallback(action='makeOrder').pack()),
    InlineKeyboardButton(text= 'Мой профиль', callback_data= MyCallback(action='profile').pack())
]])
start_markup.adjust(2)

getPos_markup = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Отправить геопозицию🌍', request_location=True)]], resize_keyboard=True, one_time_keyboard = True)


confirm_markup = InlineKeyboardBuilder([[
    InlineKeyboardButton(text= 'Подтвердить',   callback_data = MyCallback(action='confirm').pack()),
    InlineKeyboardButton(text='Отменить',       callback_data = MyCallback(action='reject').pack())
]])

stop_serch_markup = InlineKeyboardBuilder([[
    InlineKeyboardButton(text= 'Отменить поиск', callback_data=MyCallback(action= 'stop_serch').pack())
]])

drivers_status_markup = InlineKeyboardBuilder([[
    InlineKeyboardButton(text= 'Начать работу', callback_data=MyCallback(action= 'Начать работу').pack()),
    InlineKeyboardButton(text= 'Завершить работу', callback_data= MyCallback(action= 'Завершить работу').pack())
]]).as_markup() 

finish_markup = InlineKeyboardBuilder([[
    InlineKeyboardButton(text = "Открыть канал", url='https://t.me/mixtaxikm'),
    InlineKeyboardButton(text = 'Оставить отзыв', url='https://t.me/+WDs74Y5MenQ4NGYy')
]]).as_markup()
