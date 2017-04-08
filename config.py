#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import telebot
import pymongo
import datetime
from zakhse_ruz_parser import get_free_rooms

token = ''  # Токен бота

WEBHOOK_HOST = ''  # Внейшний ip-адрес сервера (Узнать: $ wget -qO- eth0.me)
WEBHOOK_PORT = 8443
WEBHOOK_LISTEN = '0.0.0.0'

WEBHOOK_SSL_CERT = './webhook_cert.pem'  # Путь к сертификату
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'  # Путь к приватному ключу

WEBHOOK_URL_BASE = "https://%s:%s" % (WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/%s/" % token

bot = telebot.TeleBot(token)

hideBoard = telebot.types.ReplyKeyboardRemove()  # if sent as reply_markup, will hide the keyboard

pair_list = [
    {'begin': '09:00', 'end': '10:20'},
    {'begin': '10:30', 'end': '11:50'},
    {'begin': '12:10', 'end': '13:30'},
    {'begin': '13:40', 'end': '15:00'},
    {'begin': '15:10', 'end': '16:30'},
    {'begin': '16:40', 'end': '18:00'},
    {'begin': '18:10', 'end': '19:30'},
    {'begin': '19:40', 'end': '21:00'},
]

# Main menu
main_menu = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=False, selective=True)
main_menu.add('Сегодня', 'Завтра')
main_menu.row('Выбрать день')
main_menu.row('‎ℹ Информация')
main_menu.row('🏩 Выбрать здание')

client = pymongo.MongoClient()
db = client.bot
users = db.users

buildings = db.buildings
building_names = [i['name'] for i in buildings.find()]
select_building = telebot.types.ReplyKeyboardMarkup(one_time_keyboard=False, selective=True)
for building in buildings.find():
    select_building.row(building['name'])

dbrooms = db.rooms

datepattern = '%Y.%m.%d'
week = ('Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс')


class User:
    def __init__(self, data):
        if not isinstance(data, dict):
            raise TypeError("Passed object is not a dictionary")

        self.id = data['id']
        self.username = data['username']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        # init => None
        self.text = data.get('text')
        self.building_name = data.get('building_name')
        self.building_id = data.get('building_id')
        self.date = data.get('date')
        self.reqtime = data.get('reqtime')  # datetime.datetime.now().strftime("%H %M %S")

    def save(self):
        self.reqtime = datetime.datetime.now().strftime("%H %M %S")
        if users.find_one({'id': self.id}):
            self.update(self.to_dict())
        else:
            users.save(self.to_dict())

    def update(self, info):
        users.update({'id': self.id}, {'$set': info})
        # for key in info.keys():
        #    self.to_dict()[key] = info[key]

    def remove(self):
        users.remove(self.to_dict())

    def __str__(self):
        return str(self.to_dict())

    def __getitem__(self, item):
        return self.to_dict()[item]

    def to_dict(self):
        return self.__dict__
