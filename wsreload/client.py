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
from glob import glob
import atexit
import tornado.websocket
import json
import os


def expand(files):
    return [file
            for abs_file in map(lambda x: os.path.abspath(x), files)
            for file in glob(abs_file)]


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


def sporadic_reload(query, host="127.0.0.1", port=50637, endpoint='wsreload'):
    """Send reload `query` to all connected browsers"""
    sporadic_websocket_send(
        host, port, endpoint, 'reload|' + json.dumps(query))


def watch(query, files, host="127.0.0.1", port=50637, endpoint='wsreload',
          unwatch_at_exit=False):
    """Tell the server to watch files and reload tabs whenever a file change"""
    sporadic_websocket_send(
        host, port, endpoint,
        'watch_files|' + json.dumps({
            'query': json.dumps(query),
            'files': expand(files)}))

    if unwatch_at_exit:
        import signal
        import sys

        def unwatch_atexit():
            unwatch(files)

        def on_kill(*args):
            unwatch_atexit()
            sys.exit(1)

        atexit.register(unwatch_atexit)
        signal.signal(signal.SIGTERM, on_kill)


def unwatch(files, host="127.0.0.1", port=50637, endpoint='wsreload'):
    """Tell the server to stop watching files"""
    sporadic_websocket_send(
        host, port, endpoint,
        'unwatch_files|' + json.dumps(expand(files)))


def monkey_patch_http_server(query, callback=None, **kwargs):
    try:
        from http.server import HTTPServer
    except ImportError:
        from BaseHTTPServer import HTTPServer

    old_serve_forever = HTTPServer.serve_forever

    def new_serve_forever(self):
        if callback:
            sporadic_reload(query, **kwargs)
            callback(self)
        old_serve_forever(self)

    HTTPServer.serve_forever = new_serve_forever
