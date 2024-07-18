from aiogram import html

def text_profile(d: tuple):
    text = f"<b>{html.underline('Информация об аккаунте')}</b>\n" \
           f"<b>Номер:</b> {d[1]} \n" \
           f"<b>Количество поездок:</b> {d[2]}"
    return text

def driver_info(driver_tuple):
    driver_info = {
        'tel': driver_tuple[1],
        'name': driver_tuple[2],
        'auto_name': driver_tuple[3],
        'auto_num': driver_tuple[4],
        'count': driver_tuple[5],
        'count_today': driver_tuple[6]
    }

    return f"<b>Телефон:</b> {driver_info['tel']}\n" \
           f"<b>Имя:</b> {driver_info['name']}\n" \
           f"<b>Марка автомобиля:</b> {driver_info['auto_name']}\n" \
           f"<b>Номер автомобиля:</b> {driver_info['auto_num']}\n" \
           f"<b>Общее количество заказов:</b> {driver_info['count']}\n" \
           f"<b>Количество заказов сегодня:</b> {driver_info['count_today']}"



def confirm(order_dict: dict):
    send_message = f"<i>Откуда:</i> <b>{order_dict['start']}</b>\n<i>Куда:</i> <b>{order_dict['finish']}</b>"
    return send_message

def driver_info_message(d):
    send_message = f"<i>Ваш заказ принят, ожидайте такси</i>\n" +\
                    "<i>Информация о водителе:</i>\n" +\
                    f"<i>Имя: </i> <b>{d[2]}</b>\n" +\
                    f"<i>Номер телефона: </i> <b>{d[1]}</b>\n" +\
                    f"<i>Марка авто :</i> <b>{d[3]}</b>\n" +\
                    f"<i>ГОСТ номер :</i> <b>{d[4]}</b>" 
    return send_message


def driver_confirm_reg(dict):
    send_message = f"Имя: {dict['name']}\n" +\
    f"Номер телефона: {dict['tel']}\n" +\
    f"Марка авто: {dict['auto_name']}\n" +\
    f"ГОСТ номер: {dict['auto_num']}\n" 

    return send_message





import re

def is_valid_phone_number(phone_number):
    # Проверка, что в строке нет букв
    if not re.match(r'^[0-9+\-() ]+$', phone_number):
        return False
    
    # Удаление всех символов, кроме цифр
    cleaned_number = re.sub(r'\D', '', phone_number)
    
    # Проверка, что номер содержит ровно 10 цифр
    if len(cleaned_number) == 10:
        return True
    
    # Проверка, что номер начинается с "+7" и содержит ровно 11 цифр
    elif cleaned_number.startswith('7') and len(cleaned_number) == 11:
        return True
    
    # Проверка, что номер начинается с "8" и содержит ровно 11 цифр
    elif cleaned_number.startswith('8') and len(cleaned_number) == 11:
        return True
    else:
        return False
    
def convert_to_digit(s):
    phone = re.sub(r'\D', '', s)
    if phone[0] == '7':
        return '+'+phone
    else:
        return '+7' + phone[1:]