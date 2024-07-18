from aiogram import Bot, Dispatcher, html, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery, ReplyKeyboardRemove, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from apscheduler.schedulers.asyncio import AsyncIOScheduler
import datetime
import random

from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext

from dotenv import load_dotenv
import os

from users_markups import *
from database import DataBase
from users_status import *
from text_converter import *

load_dotenv()
TOKEN = os.getenv('TOKEN')
TAXI_CHAT = os.getenv('TAXI_CHATT')
ORDERS = os.getenv("ORDERS")
dp = Dispatcher()
dataBase = DataBase('taxi.db')
current_orders ={}
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))


async def interval_task(bot: Bot, db: DataBase):
    drivers = db.showAll('drivers')
    report = 'Отчет за сегодня:\n'
    total_orders = 0
    for driver in drivers:
        name = driver[2]
        today_orders = driver[6]
        if today_orders != 0:
            report += f"{name} - {today_orders} заказов\n"
            total_orders += today_orders
            await bot.send_message(driver[0], f"Отчет за сегодня:\n{name} - {today_orders} заказов\n")
    report += f'Итог: {total_orders}'
    db.nullColmn('drivers', 'count_today')
    await bot.send_message(TAXI_CHAT, report)


async def main() -> None:
    scheduler = AsyncIOScheduler(timezone = 'Europe/Moscow')
    scheduler.add_job(interval_task, trigger='cron', hour = 18, kwargs={'bot':bot, 'db': dataBase})
    scheduler.start()
    await dp.start_polling(bot)


@dp.message(CommandStart())
async def start_message(message: Message, state: FSMContext):

    await state.clear()
    count = dataBase.OnlineCount()
    user_name = message.from_user.first_name

    greetings = [
        f"Добрый день, <b>{user_name}</b>! 🚕 Мы рады видеть тебя снова.\nВ нашем распоряжении {count} водителей, готовых выехать к тебе в любое время.",
        f"Здравствуй, <b>{user_name}</b>! 🚕 Ты готов заказать такси?\nВ настоящее время у нас {count} водителей в сети, и мы готовы помочь тебе добраться до нужного места.",
        f"Приветствуем, <b>{user_name}</b>! 🚕 Наш такси-сервис всегда готов помочь тебе.\nВ настоящее время у нас {count} водителей в сети, и мы готовы отправиться к тебе в любое время.",
        f"Добро пожаловать, <b>{user_name}</b>! 🚕 Мы рады видеть тебя в нашем такси-сервисе.\nВ настоящее время у нас {count} водителей в сети, и мы готовы помочь тебе добраться до нужного места быстро и комфортно.",
        f"Здравствуй, <b>{user_name}</b>! 🚕 Ты готов заказать такси? Мы готовы помочь тебе в любое время.\nВ настоящее время у нас {count} водителей в сети, и мы готовы отправиться к тебе в любое время."
    ]
    send_message = random.choice(greetings)
    user_id = message.from_user.id
    
    if dataBase.isExist('users', 'id', user_id):
        await message.answer(text=send_message, reply_markup=start_markup.as_markup())
    else:
        send_message = f'К сожалению, <b>{user_name}</b>, вы еще не зарегистрированы в нашем такси-сервисе.\nЧтобы зарегистрироваться, просто введите ваш номер телефона.'
        await message.answer(text=send_message)
        await state.set_state(UserRegState.getTel)



@dp.callback_query(MyCallback.filter(F.action == 'profile'))
async def get_profile(call: CallbackQuery):
    id = call.from_user.id

    if dataBase.isExist('drivers', 'id', id):
        row = dataBase.getRow('drivers', id, 'id', '*')
        send_message = driver_info(row)
    else:
        row =dataBase.getRow('users',id, 'id', '*')
        send_message = text_profile(row) 
    
    await call.message.delete_reply_markup()
    await call.message.answer(send_message, reply_markup= start_markup.as_markup())


@dp.message(Command('driver'))
async def start_driver_register(message: Message, state: FSMContext):
    await state.update_data(driver_id=message.from_user.id)
    send_message = "Введите номер телефона 📞"
    await message.answer(text=send_message)
    await state.set_state(DriverRegState.tel)

@dp.message(Command('info'))
async def info_drivers(message: Message, state: FSMContext):
    all_drivers = dataBase.showAll('drivers')
    count = 0
    for row in all_drivers:
        print(row)
        if row[-1] == 1:
            send_message = f"{row[2]} - {row[1]}"
            count += 1
            await message.answer(text= send_message)
    await message.answer(f'Всего: {count} водителей Онлайн.')

@dp.message(Command('status'))
async def change_status(message: Message, state: FSMContext):
    
    id = message.from_user.id
    if dataBase.isExist('drivers', 'id', id):
        status = dataBase.getRow('drivers', id, 'id', 'is_online')[0]
        status = 'ОНЛАЙН' if status==1 else 'ОФЛАЙН'
        await message.answer(f"Ваш статус {status}.\nЕсли хотите изменить нажмите на кнопки ниже", reply_markup= drivers_status_markup)



@dp.message(UserRegState.getTel)
async def new_user(message: Message, state: FSMContext):
    user_id = message.from_user.id
    tel_num = message.text
    if is_valid_phone_number(tel_num):
        dataBase.addRow('users', user_id, tel_num, 0)
        await state.clear()
        send_message = 'Вы зарегистрированы! 🎉 Теперь можете заказать такси! 🚕'
        await message.answer(text=send_message, reply_markup=start_markup.as_markup())
    else:
        send_message = 'Введите корректный номер телефона. 📞'
        await message.answer(text=send_message)


@dp.callback_query(MyCallback.filter(F.action == 'makeOrder'))
async def make_order(call: CallbackQuery, state: FSMContext):

    send_message = 'Откуда вас забрать? 📍'
    await call.message.edit_text(text=send_message)
    await state.set_state(OrderState.start)


@dp.message(F.text, OrderState.start)
async def start_point(message: Message, state: FSMContext):
    await state.update_data(start=message.text)
    send_message = 'Отправьте вашу геопозицию, для этого нажмите на кнопку ниже 🗺️'
    await message.answer(text=send_message, reply_markup=getPos_markup)
    await state.set_state(OrderState.location)



@dp.message(F.location, OrderState.location)
async def start_location(message: Message, state: FSMContext):
    await state.update_data(location=message.location)
    send_message = "Куда вас отвезти? 🛤️"
    await message.answer(text=send_message, reply_markup=ReplyKeyboardRemove())
    await state.set_state(OrderState.finish)


@dp.message(OrderState.finish)
async def get_adress(message: Message, state: FSMContext):
    await state.update_data(finish = message.text)
    data = await state.get_data()
    send_message = confirm(data)
    await message.answer(send_message, reply_markup=confirm_markup.as_markup())

@dp.callback_query(MyCallback.filter(F.action == 'reject'))
async def reject_order(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Заказ отменен. Нажмите /start, чтобы начать сначала.")
    await state.clear()

@dp.callback_query(MyCallback.filter(F.action == 'confirm'))
async def confirm_order(call: CallbackQuery, state: FSMContext):
    pas_id = call.from_user.id

    chat_markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text= 'Взять заказ', callback_data=TaxiCallback(id= pas_id, action='newOrder').pack())
    ]])
    order_message = await bot.send_message(TAXI_CHAT, text=call.message.text, reply_markup= chat_markup)

    
    user_markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text= 'Отменить поиск ❌', callback_data= DelMessageCallback(message_id= order_message.message_id, chat_id=TAXI_CHAT).pack())
    ]])
    await call.message.edit_reply_markup()
    del_message = await call.message.answer('Ищем водителя...🔎', reply_markup=user_markup)
    current_orders[pas_id] = (await state.get_data(), del_message.message_id)

    await state.clear()


@dp.callback_query(TaxiCallback.filter(F.action == 'newOrder'))
async def take_order(call: CallbackQuery, state: FSMContext):
    driver_id = int(call.from_user.id)
    if dataBase.isExist('drivers', 'id', driver_id):
        await call.answer('Вы взяли заказ. 🚕 Перейдите к боту, чтобы увидеть детали заказа', show_alert=True)
        pas_id = int(call.data.split(':')[1])
        data = current_orders[pas_id][0]
        user_mes_id = current_orders[pas_id][1]

        location = data['location']
        latitude = location.latitude
        longitude = location.longitude

        await call.message.delete()     #Удалить из канала
        driver_info = dataBase.getRow('drivers', driver_id, 'id', '*')
        message_to_user = driver_info_message(driver_info)
        await bot.edit_message_text(text= message_to_user, chat_id=pas_id, message_id=user_mes_id)

        order_message = html.bold('Ваш Заказ: \n') + confirm(data) + html.italic('\nТелефон: ') + html.bold(str(dataBase.getTelNum('users', 'tel', pas_id)[0]))

        driver_markup = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton(text= 'На месте 📍', callback_data=TaxiCallback(id=pas_id, action='Подъехал').pack())
        ]])

        await bot.send_location(call.from_user.id, latitude=latitude, longitude=longitude)
        await bot.send_message(chat_id= driver_id, text = order_message, reply_markup= driver_markup)
        await bot.send_message(chat_id= ORDERS, text =  order_message +'\n'+message_to_user)

    else:
        await call.answer('Вы не водитель, обратитесь к админу. 🚔', show_alert=True)


@dp.callback_query(TaxiCallback.filter(F.action == 'Подъехал'))
async def arrived(call: CallbackQuery, state: FSMContext):
    driver_id = int(call.from_user.id)
    pas_id = int(call.data.split(':')[1])

    await bot.send_message(pas_id, 'Водитель приехал, можете выходить. 🚗 Хорошей поездки!')
    driver_markup = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text='Завершить ✅', callback_data=TaxiCallback(id = pas_id, action= 'завершить').pack())
    ]])
    await call.message.edit_reply_markup(reply_markup=driver_markup)


@dp.callback_query(TaxiCallback.filter(F.action == 'завершить'))
async def finish_trip(call: CallbackQuery, state: FSMContext):
    driver_id = int(call.from_user.id)
    pas_id = int(call.data.split(':')[1])

    dataBase.incCell('drivers', driver_id, 'count', 'count_today')
    dataBase.incCell('users', pas_id, 'count')

    drivers_count = dataBase.getRow('drivers', driver_id, 'id', 'count, count_today')

    await bot.send_message(pas_id, 'Вы приехали! Спасибо что выбрали нас! 🚕', reply_markup= finish_markup)
    await call.message.delete_reply_markup()
    await call.message.answer(f'Вы завершили поездку. ✅\nВаша статистика: \nВсего: {drivers_count[0]}\nСегодня: {drivers_count[1]}')
    await state.clear()
    current_orders.pop(pas_id)




@dp.callback_query(DelMessageCallback.filter())
async def reject_serch(call: CallbackQuery, state: FSMContext):
    pas_id = call.from_user.id
    data = call.data.split(':')
    del_mes_id = data[1]
    del_chat_id = data[2]
    await bot.delete_message(del_chat_id, del_mes_id)
    await call.message.edit_text('Поиск остановлен. ❌ Чтобы начать сначала нажмите /start')
    current_orders.pop(pas_id)
    await state.clear()








@dp.message(DriverRegState.tel)
async def driversTelNum(message:Message, state: FSMContext):
    tel_num = message.text
    if is_valid_phone_number(tel_num):
        await state.update_data(tel = tel_num)
        await state.set_state(DriverRegState.name)
        await message.answer('Введите Фамилию ИО')
    else:
        await message.answer('Введите корректный номер телефона.')

@dp.message(DriverRegState.name)
async def driversName(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name = name)
    await state.set_state(DriverRegState.auto_name)
    await message.answer('Введите марку автомобиля, можно так же указать цвет, чтобы пассажиры могли легче найти вас.')

@dp.message(DriverRegState.auto_name)
async def driversAutoName(message: Message, state: FSMContext):
    auto_name = message.text
    await state.update_data(auto_name = auto_name)
    await state.set_state(DriverRegState.auto_num)
    await message.answer("Введите ГОСТ номер машины, можно без букв.")

@dp.message(DriverRegState.auto_num)
async def driversAutoNum(message: Message, state: FSMContext):
    auto_num = message.text
    await state.update_data(auto_num = auto_num)
    await state.set_state(DriverRegState.confirm)

    send_message = driver_confirm_reg(await state.get_data())
    markups = InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text= 'Подтвердить', callback_data=MyCallback(action='confirmreg').pack()),
        InlineKeyboardButton(text= 'Отменить', callback_data=MyCallback(action='reject').pack())
    ]])

    await message.answer(text= send_message, reply_markup=markups)

@dp.callback_query(DriverRegState.confirm, MyCallback.filter(F.action == 'confirmreg'))
async def driversAddBase(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    dataBase.addRow('drivers', data['driver_id'], data['tel'], data['name'], data['auto_name'], data['auto_num'], 0, 0, 0)
    await call.message.edit_text('Вы зарегистрированы! Можете начать принимать заказы в чате. Не забывайте менять свой статус. Для этого нажмите на кнопку ниже, или наерите команду /status', reply_markup= drivers_status_markup)
    await state.clear()

@dp.callback_query(MyCallback.filter(F.action == 'Начать работу'))
async def begin_work(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Вы начали смену, теперь можете принимать заказы. Если хотите изменить свой статус нажмите /status")
    id = call.from_user.id
    dataBase.makeOnline(id)

@dp.callback_query(MyCallback.filter(F.action == 'Завершить работу'))
async def finish_work(call: CallbackQuery, state: FSMContext):
    await call.message.edit_text("Вы завершили смену. Если хотите изменить свой статус нажмите /status")
    id = call.from_user.id
    dataBase.makeOfline(id)
    







async def f(bot: Bot):
    await bot.send_message(TAXI_CHAT, 'HI')




if __name__ == "__main__":
    asyncio.run(main())
