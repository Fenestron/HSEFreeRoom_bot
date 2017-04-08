#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


# Author: Aleksandr Kulagin a.k.a. Fenestron
# As a part of "HSE Free Room" project of "The Next Station" team


import datetime
from telebot import types
from config import *


def get_user(message):
    if isinstance(message, int):
        bduser = users.find_one({'id': message})
    else:
        bduser = users.find_one({'id': message.from_user.id})

    if bduser is None:
        # print('New user')

        user = User({
            'id': message.from_user.id,
            'username': message.from_user.username,
            'first_name': message.from_user.first_name,
            'last_name': message.from_user.last_name,
        })

        # user = User(message.__dict__, tg=1)
    else:
        user = User(bduser)

    return user


@bot.message_handler(commands=["start"])
def command_start(message: types.Message):
    user = get_user(message)
    # print(user)
    user.text = message.text
    user.save()
    # print(user)

    if user.building_name is not None:
        keyboard = types.InlineKeyboardMarkup()
        callback_button = types.InlineKeyboardButton(text="Изменить", callback_data="change building")
        keyboard.add(callback_button)
        bot.send_message(message.chat.id, 'Ваше здание: ' + user.building_name, reply_markup=keyboard)
        return

    set_building(message)


def choose_building(message: types.Message):
    user = get_user(message)

    user.text = message.text
    user.save()
    if user.text not in building_names:
        if user.text is None:
            msg = bot.reply_to(message, 'Что это?\n'
                                        'Выберите корпус из представленного списка:')
            bot.register_next_step_handler(msg, choose_building)
            return
        if user.text.startswith('/start'):
            return
        msg = bot.reply_to(message, 'Неверный корпус!\n'
                                    'Выберите корпус из представленного списка:')
        bot.register_next_step_handler(msg, choose_building)
        return

    user.building_name = message.text
    user.building_id = buildings.find_one({'name': user.building_name})['buildingOid']
    user.save()

    bot.send_message(message.chat.id, "Ваше здание: " + user.text, reply_markup=main_menu)

    '''
    keyboard = types.InlineKeyboardMarkup()
    callback_button = types.InlineKeyboardButton(text="Сегодня", callback_data="date Сегодня")
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text="Завтра", callback_data="date Завтра")
    keyboard.add(callback_button)

    msg = bot.send_message(message.chat.id, "Теперь выберите день:", reply_markup=keyboard)
    '''


def text_from_db(free_rooms):
    text = ''
    for i in range(1, 9):
        line = '*{num} пара ({begin} - {end})*. Свободные аудитории: \n'.format(
            num=i, begin=pair_list[i - 1]['begin'], end=pair_list[i - 1]['end']
        )
        rooms = free_rooms['lessons'][str(i)]

        if not rooms:
            rooms = 'Все аудитории заняты 😥'
            line += rooms
        else:
            line += ', '.join(rooms)

        line += '\n\n'
        text += line
    return text


def text_from_zrp(free_rooms):
    text = ''
    for i in range(1, 9):
        line = '*{num} пара ({begin} - {end})*. Свободные аудитории: \n'.format(
            num=i, begin=pair_list[i - 1]['begin'], end=pair_list[i - 1]['end']
        )
        rooms = ''
        for room in free_rooms:
            if i in room['lessons']:
                number = str(room['number'])
                if len(number) < 7:
                    rooms += "{number}, ".format(number=number)
        if rooms:
            rooms = rooms[:-2]
        else:
            rooms = 'Все аудитории заняты 😥'

        line += rooms + '\n\n'
        text += line

    return text


def send(message, text):
    bot.send_message(message.chat.id, text, parse_mode="Markdown")


def edit(call, text):
    bot.edit_message_text(text=text, chat_id=call.message.chat.id, message_id=call.message.message_id,
                          parse_mode="Markdown")


def result(date, message):
    call = None
    if isinstance(message, types.CallbackQuery):
        call = message
        message = call.message
    else:
        date = date.strftime(datepattern)

    # print(message)

    user = get_user(message.chat.id)
    now = datetime.datetime.now()
    reqtime = datetime.datetime.strptime(user.reqtime, "%H %M %S")
    # print(reqtime, now)
    if reqtime.hour == now.hour and reqtime.minute == now.minute and \
            (reqtime.second == now.second or reqtime.second + 1 == now.second):
        if call:
            edit(call, "FLOOD: Слишком часто!")
        else:
            send(message, "FLOOD: Слишком часто!")
        return

    if user.building_id is None:
        if call:
            edit(call, "Сначала выберите здание!")
        return

    user.date = date
    user.save()

    text = ''

    date = datetime.datetime.strptime(date, datepattern)
    if date.weekday() == 6:
        text = "А что это ты собираешься там делать в воскресенье? 😜"
    else:
        free_rooms = dbrooms.find_one({'building_id': str(user.building_id), 'date': user.date})

        # print(free_rooms)
        if free_rooms:
            text = text_from_db(free_rooms)
        else:
            free_rooms = get_free_rooms(user.date, user.building_id)
            text = text_from_zrp(free_rooms)

    if len(text) >= 3000:
        text_first = text[:text.find('*5 ')]
        if call:
            bot.edit_message_text(text=text_first, chat_id=message.chat.id, message_id=message.message_id,
                                  parse_mode="Markdown")
        else:
            bot.send_message(message.chat.id, text_first, parse_mode="Markdown")

        text_second = text[text.find('*5 '):]

        bot.send_message(message.chat.id, text_second, parse_mode="Markdown")
        return

    if call:
        edit(call, text)
    else:
        send(message, text)

        # return user


@bot.message_handler(func=lambda message: message.text == "‎ℹ Информация")
def handle_message(message: types.Message):
    user = get_user(message)
    if user.building_id is None:
        return
    text = 'Здравствуйте, {name}\n‎' \
           'Текущее здание: {building}'.format(name=message.from_user.first_name,
                                               building=user.building_name)
    keyboard = types.InlineKeyboardMarkup()
    # callback_button = types.InlineKeyboardButton(text="🆕 Изменить здание", callback_data="change building")
    # keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text="ℹ О проекте", callback_data="about")
    keyboard.add(callback_button)
    callback_button = types.InlineKeyboardButton(text="✋ Связь с админом", callback_data="admin")
    keyboard.add(callback_button)

    bot.send_message(message.chat.id, text, reply_markup=keyboard)

    # bot.send_message(message.chat.id, '🔧 Настройки')


@bot.message_handler(func=lambda message: message.text == "Сегодня")
def handle_message(message: types.Message):
    date = datetime.date.today()
    result(date, message)


@bot.message_handler(func=lambda message: message.text == "Завтра")
def handle_message(message: types.Message):
    date = datetime.date.today() + datetime.timedelta(days=1)
    result(date, message)


def get_data_keyboard(date=None):
    is_today = 0
    if (date is None) or (date == datetime.date.today().strftime(datepattern)):
        date = datetime.date.today()
        is_today = 1
    else:
        date = datetime.datetime.strptime(date, datepattern)
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for i in range(3):
        date += datetime.timedelta(days=1)

        callback_button_left = types.InlineKeyboardButton(text=week[date.weekday()] + date.strftime(' (%d.%m)'),
                                                          callback_data='date: ' + date.strftime(datepattern))
        date += datetime.timedelta(days=3)

        callback_button_right = types.InlineKeyboardButton(text=week[date.weekday()] + date.strftime(' (%d.%m)'),
                                                           callback_data='date: ' + date.strftime(datepattern))
        keyboard.add(callback_button_left, callback_button_right)

        date += datetime.timedelta(days=-3)

    if is_today:
        date += datetime.timedelta(days=3)
        keyboard.add(types.InlineKeyboardButton(text='🔜 Вперед',
                                                callback_data='dates:next:' + date.strftime(datepattern)))
    else:
        date += datetime.timedelta(days=-9)

        callback_button_left = types.InlineKeyboardButton(text='🔙 Назад',
                                                          callback_data='dates:back:' + date.strftime(datepattern))

        date += datetime.timedelta(days=12)

        callback_button_right = types.InlineKeyboardButton(text='🔜 Вперед',
                                                           callback_data='dates:next:' + date.strftime(datepattern))
        keyboard.add(callback_button_left, callback_button_right)

    return keyboard


@bot.message_handler(func=lambda message: message.text == "Выбрать день")
def handle_message(message: types.Message):
    bot.send_message(message.chat.id, 'Выберите день:', reply_markup=get_data_keyboard())


@bot.message_handler(func=lambda message: message.text == "🏩 Выбрать здание")
def handle_message(message: types.Message):
    set_building(message)


def set_building(message):
    is_new = ''

    user = get_user(message)

    if isinstance(message, types.CallbackQuery):
        # message == call
        message = message.message
        is_new = ' новый'
        text = 'Ваше предыдущие здание: ' + user.building_name
        msg = bot.edit_message_text(text=text, chat_id=message.chat.id, message_id=message.message_id)

    user.building_name = None
    user.building_id = None
    user.save()

    msg = bot.send_message(message.chat.id, "Выберите{} корпус НИУ ВШЭ:".format(is_new), reply_markup=select_building)
    # print(bot.pre_message_subscribers_next_step.get(message.chat.id))
    if bot.pre_message_subscribers_next_step.get(message.chat.id):
        return

    bot.register_next_step_handler(msg, choose_building)


def about(message: types.Message):
    text = '*HSEFreeRoom* - бот для поиска свободных аудиторий в корпусах НИУ ВШЭ.\n' \
           'Проект создан командой "The Next Station". Состав команды:\n' \
           'Александр (@Fenestron)\n' \
           'Мария (@mrnisv)\n' \
           'Сергей (@Zakhse)\n' \
           'Николай (@alagunto)\n'

    if isinstance(message, types.CallbackQuery):
        # message == call
        message = message.message
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id,
                              text=text, parse_mode="Markdown")
    else:
        bot.send_message(message.chat.id, text)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    # Если сообщение из чата с ботом
    if call.message:
        if call.data == "change building":
            # print(type(call))
            set_building(call)

        if call.data == "about":
            about(call)

        if call.data == "admin":
            text = 'С вопросами и предложениями можете писать админу — @Fenestron'
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=text)

        if call.data.startswith('date: '):
            date = call.data.split(': ')[1]
            result(date, call)

        if call.data.startswith('dates:'):
            temp, way, data = call.data.split(":")
            bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                          inline_message_id=call.inline_message_id,
                                          reply_markup=get_data_keyboard(data))


@bot.message_handler(content_types=['text'])
def handle_text_doc(message):
    pass
