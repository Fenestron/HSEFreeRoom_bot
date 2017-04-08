#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import pymongo
import datetime
from time import sleep
import zakhse_ruz_parser as zrp

client = pymongo.MongoClient()
db = client.bot
buildings = db.buildings
dbrooms = db.rooms

datepattern = '%Y.%m.%d'
mdate = datetime.datetime.today() - datetime.timedelta(days=1)

for q in range(8):
    mdate += datetime.timedelta(days=1)

    for building in buildings.find():  # {'name': "Б. Ордынка ул., д. 47/7, стр.1"}
        name = building['name']
        bid = str(building['buildingOid'])
        date = mdate.strftime(datepattern)
        print(date, name, bid)

        # if dbrooms.find_one({'building_id': bid, 'date': date}):
        #    continue

        if dbrooms.find_one({'building_id': bid, 'date': date}) is None:
            print("KEK")
            dbrooms.save({
                "building_id": bid,
                'name': name,
                "date": date,
                'lessons': {}
            }, check_keys=False)

        isRes = False
        while not isRes:
            try:
                free_rooms = zrp.get_free_rooms(date, bid)
                isRes = True
            except:
                print("*" * 10)
                sleep(45)
                pass

        for i in range(1, 9):
            rooms = []
            for room in free_rooms:
                if i in room['lessons']:
                    number = room['number']
                    if len(str(number)) < 6:
                        rooms.append(number)

            d = {
                "building_id": bid,
                'name': name,
                "date": date,
                'lessons': {str(i): rooms}
            }
            print(d)

            dbrooms.update({"building_id": bid, "date": date}, {"$set": {"lessons." + str(i): rooms}})


def print_():
    for i in dbrooms.find():
        print(i)
