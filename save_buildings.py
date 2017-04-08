#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import pymongo
import zakhse_ruz_parser as zrp

client = pymongo.MongoClient()
db = client.bot
buildings = db.buildings

buildings.remove()

moscow_buildings = zrp.load_moscow_buildings()

fakes = '''Ильинка ул., д. 13 стр. 1
Кривоколенный пер., д. 3
Мытная ул., д. 46 к.5
Петровка ул., д. 12
Потаповский пер., д.16 стр.10
Профсоюзная ул, д. 33, корп. 4
Старая Басманная 21/4 корпус 4
Таллинская ул., д. 34
Вавилова ул., д. 7
Трифоновская ул., д. 57
Шаболовка ул., д. 28
Шаболовка ул., д. 31 корп. Г
Шаболовка ул., д. 31 стр. 23'''

for i in moscow_buildings:
    buildings.save(i)

for i in fakes.split('\n'):
    # print(i, buildings.find_one({'name': i}))
    buildings.remove({'name': i})

buildings.update({"name": "Кривоколенный пер., д. 3 "}, {"$set": {"name": "Кривоколенный пер., д. 3"}})
print(buildings.count())
for i in buildings.find():
    print(i['name'] + "|")
