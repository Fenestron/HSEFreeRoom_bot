#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import cherrypy
import requests
import telebot

from config import *

HSE_BOT_TOKEN = token

HSE_BOT_ADDRESS = "http://127.0.0.1:7771"

hse_bot = bot


class WebhookServer(object):

    @cherrypy.expose
    def HSEFreeRoom(self):
        if 'content-length' in cherrypy.request.headers and \
                        'content-type' in cherrypy.request.headers and \
                        cherrypy.request.headers['content-type'] == 'application/json':
            length = int(cherrypy.request.headers['content-length'])
            json_string = cherrypy.request.body.read(length).decode("utf-8")
            # Вот эта строчка и пересылает все входящие сообщения на нужного бота
            requests.post(HSE_BOT_ADDRESS, data=json_string)
            print(json_string)
            return ''
        else:
            raise cherrypy.HTTPError(403)


if __name__ == '__main__':
    print("=" * 20)
    hse_bot.remove_webhook()
    hse_bot.set_webhook(url=WEBHOOK_URL_BASE + '/HSEFreeRoom',
                        certificate=open(WEBHOOK_SSL_CERT, 'r'))

    cherrypy.config.update({
        'server.socket_host': WEBHOOK_LISTEN,
        'server.socket_port': WEBHOOK_PORT,
        'server.ssl_module': 'builtin',
        'server.ssl_certificate': WEBHOOK_SSL_CERT,
        'server.ssl_private_key': WEBHOOK_SSL_PRIV,
        'engine.autoreload.on': False
    })
    cherrypy.quickstart(WebhookServer(), '/', {'/': {}})
