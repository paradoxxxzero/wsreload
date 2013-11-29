# -*- coding: utf-8 -*-

#     wsreload - Reload your tabs !
#     Copyright (C) 2012 Florian Mounier <paradoxxx.zero@gmail.com>
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.
#
#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.


from tornado.ioloop import IOLoop
import tornado.websocket
import json


def sporadic_websocket_send(host, port, endpoint, message):
    """Send message to server through the websocket"""
    ioloop = IOLoop.instance()

    def websocket_ready(connection):
        ws = connection.result()
        ws.write_message(message)
        ioloop.stop()

    tornado.websocket.websocket_connect(
        'ws://%s:%d/%s' % (host, port, endpoint),
        ioloop, websocket_ready)

    ioloop.start()


def sporadic_reload(query, host="127.0.0.1", port=50637, endpoint='endpoint'):
    """Send reload `query` to all connected browsers"""
    sporadic_websocket_send(
        host, port, endpoint, 'reload|' + json.dumps(query))


def watch(query, files, host="127.0.0.1", port=50637, endpoint='endpoint'):
    """Tell the server to watch files and reload tabs whenever a file change"""
    sporadic_websocket_send(
        host, port, endpoint,
        'watch_files|' + json.dumps({
            'query': json.dumps(query),
            'files': files}))


def unwatch(files, host="127.0.0.1", port=50637, endpoint='endpoint'):
    """Tell the server to stop watching files"""
    sporadic_websocket_send(
        host, port, endpoint,
        'unwatch_files|' + json.dumps(files))
