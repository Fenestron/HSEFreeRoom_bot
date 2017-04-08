# Author: Zakharov Sergey a.k.a. Zakhse
# As a part of "HSE Free Room" project of "The Next Station" team
# 3 december, 2016

import requests
import json


def load_buildings():
    a = requests.get("http://ruz.hse.ru/ruzservice.svc/buildings")
    buildings_list = json.loads(a.text)
    return buildings_list


def load_moscow_buildings():
    a = load_buildings()
    for i in reversed(range(len(a))):
        if (a[i]['address'] is None) or (a[i]['address'].startswith('Пермь,')) or (
                a[i]['address'].startswith('Санкт-Петербург,')) or (a[i]['address'].startswith('Нижний Новгород,')) or (
                    len(get_auditories(a[i]['buildingOid'])) < 5) or (
                a[i]['address'].startswith('г.Пермь,')):
            del a[i]
    return a


def get_auditories(building_id):
    a = requests.get("http://ruz.hse.ru/ruzservice.svc/auditoriums?buildingoid=" + str(building_id))
    auditories_list = json.loads(a.text)
    return auditories_list


# date = yyyy.mm.dd (string)
def get_lessons(date, auditory_id):
    a = requests.get(
        "http://ruz.hse.ru/ruzservice.svc/lessons?fromdate=" + date + "&todate=" + date + "&auditoriumoid=" + str(
            auditory_id))
    lessons_list = json.loads(a.text)
    return lessons_list


def building_of_auditory(auditory_id):
    a = requests.get("http://ruz.hse.ru/ruzservice.svc/auditoriums")
    list = json.loads(a.text)
    for i in range(len(list)):
        if list[i]['auditoriumOid'] == auditory_id:
            return "Building ID: " + str(list[i]['buildingOid']) + "; Name: " + list[i]['building']
    return ""


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


# date = yyyy.mm.dd (string)
# returns list of dicts - "json"
# every element of this lists has 3 fields:
# * auditoriumOid - auditory ID (int)
# * auditorium - auditory number (string)
# * lessons - list of free lessons (ints) for the auditory
def get_free_rooms(date, building_id):
    auditories_list = get_auditories(building_id)
    auditory_lessons_list = []
    for aud in auditories_list:
        lessons = get_lessons(date, str(aud['auditoriumOid']))
        temp_list = {1, 2, 3, 4, 5, 6, 7, 8}
        for les in lessons:
            temp_list_copy = temp_list.copy()
            for p in temp_list_copy:
                if pair_list[p - 1]['begin'] < les['endLesson'] and pair_list[p - 1]['end'] > les['beginLesson']:
                    temp_list.remove(p)
        if (len(temp_list)):
            auditory_lessons_list.append(
                {
                    'auditoriumOid': aud['auditoriumOid'],
                    'number': aud['number'],
                    'lessons': list(temp_list)
                })
    return auditory_lessons_list
