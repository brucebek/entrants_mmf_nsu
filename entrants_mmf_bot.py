from config import TOKEN
from commands import *

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

import os

bot = TeleBot(TOKEN)


def get_commands():
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    markup.add(InlineKeyboardButton('Участвующие в конкурсе на ПМИ', callback_data='amcs'),
               InlineKeyboardButton('Подавшие согласие на ПМИ', callback_data='amcs_consents'),
               InlineKeyboardButton('Участвующие в конкурсе на МКН', callback_data='mcs'),
               InlineKeyboardButton('Подавшие согласие на МКН', callback_data='mcs_consents'),
               InlineKeyboardButton('Участвующие в конкурсе на М', callback_data='math'),
               InlineKeyboardButton('Подавшие согласие на М', callback_data='math_consents'),
               InlineKeyboardButton('Участвующие в конкурсе на ИВТ', callback_data='fit'),
               InlineKeyboardButton('Подавшие согласие на ИВТ', callback_data='fit_consents'))
    return markup


@bot.message_handler(commands=['lists', 'start'])
def start(message):
    commands = get_commands()
    id_user = str(message.from_user.id)
    user = get_user(id_user)
    if not user:
        bot.reply_to(message, 'У вас нет доступа к боту')
        return

    msg = f'{message.from_user.first_name}, какой список вы хотите получить?'
    if user['is_admin']:
        commands.add(
            InlineKeyboardButton(
                'Добавить пользователя', callback_data='admin_add'), InlineKeyboardButton(
                'Получить пользователя', callback_data='admin_get'), InlineKeyboardButton(
                'Удалить пользователя', callback_data='admin_del'), InlineKeyboardButton(
                'Получить историю действий пользователя', callback_data='admin_act'))
        msg += '\nВы являетесь администратором, вам доступны дополнительные команды'

    bot.send_message(message.chat.id, msg, reply_markup=commands)


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    id_user = str(call.from_user.id)
    filters = {
        'amcs': {'direction': 'ПМИ', 'type_list': 'Конкурс', 'name': 'Участвующие в конкурсе на ПМИ'},
        'amcs_consents': {'direction': 'ПМИ', 'type_list': 'Зачисление', 'name': 'Подавшие согласие на ПМИ'},
        'mcs': {'direction': 'МКН', 'type_list': 'Конкурс', 'name': 'Участвующие в конкурсе на МКН'},
        'mcs_consents': {'direction': 'МКН', 'type_list': 'Зачисление', 'name': 'Подавшие согласие на МКН'},
        'math': {'direction': 'М', 'type_list': 'Конкурс', 'name': 'Участвующие в конкурсе на М'},
        'math_consents': {'direction': 'М', 'type_list': 'Зачисление', 'name': 'Подавшие согласие на М'},
        'fit': {'direction': 'ИВТ', 'type_list': 'Конкурс', 'name': 'Участвующие в конкурсе на ИВТ'},
        'fit_consents': {'direction': 'ИВТ', 'type_list': 'Зачисление', 'name': 'Подавшие согласие на ИВТ'}}

    command = call.data.split('_')
    if command[0] != 'admin':
        add_activity(id_user, filters[call.data]['name'])
        pth = get_path_list(id_user,
                            filters[call.data]['direction'],
                            filters[call.data]['name'],
                            filters[call.data]['type_list'])
        with open(pth, 'rb') as res:
            bot.send_document(call.message.chat.id, res)
        os.remove(pth)
        return
    command = command[1]
    if command == 'add':
        msg = bot.send_message(
            call.message.chat.id,
            'Введите id и username через пробел')
        bot.register_next_step_handler(msg, add)
    else:
        msg = bot.send_message(call.message.chat.id, 'Введите id')
        if command == 'get':
            bot.register_next_step_handler(msg, get)
        elif command == 'act':
            bot.register_next_step_handler(msg, act)
        else:
            bot.register_next_step_handler(msg, delete)


def add(message):
    dt = message.text.split()
    id, username = dt[0], dt[1]
    user = add_user(id, username)
    if user:
        res = f'Пользователь {user["username"]} добавлен'
        add_activity(str(message.from_user.id), f'Добавление пользователя {user["username"]}')
    else:
        res = 'Пользователь существует'

    bot.reply_to(message, res)


def act(message):
    id = str(message.text)
    activity = get_activity(id)
    if activity:
        res = ''
        for a in activity:
            res += f'{a["time"]} - {a["action"]}\n'
        add_activity(str(message.from_user.id), f'Получение истории действий пользователя {get_user(id)["username"]}')
    else:
        res = 'Пользователь не найден'
    bot.reply_to(message, res)


def get(message):
    id = message.text
    user = get_user(id)
    if user:
        res = f'{user["username"]}'
        add_activity(str(message.from_user.id), f'Получение пользователя {user["username"]}')
    else:
        res = 'Пользователь не найден'

    bot.reply_to(message, res)


def delete(message):
    id = message.text
    user = del_user(id)
    if user:
        res = f'{user["username"]}'
        add_activity(str(message.from_user.id), f'Удаление пользователя {user["username"]}')
    else:
        res = 'Пользователь не найден'
    bot.reply_to(message, res)


bot.polling()
