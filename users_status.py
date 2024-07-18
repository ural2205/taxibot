
from aiogram.fsm.state import State, StatesGroup



class UserRegState(StatesGroup):
    getTel = State()

class OrderState(StatesGroup):
    start = State()
    location = State()
    finish = State()

class DriverRegState(StatesGroup):
    tel = State()
    name = State()
    auto_name = State()
    auto_num = State()
    confirm = State()
