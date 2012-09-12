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
import tornado.options
import tornado.web
import tornado.websocket
import logging
import json
import os


log = logging.getLogger('wsreload')


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render('index.html')


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    browsers = {}

    def reload(self, query=None):
        log.info('Reloading for query %s' % query)
        for browser, ua in self.browsers.items():
            log.debug('Reloading %s' % ua)
            browser.write_message(query)

    def on_message(self, message):
        log.debug('Got -> %s' % message)
        data = ''
        if '|' in message:
            pipe = message.index('|')
            message, data = message[:pipe], message[pipe + 1:]

        if message == 'subscribe':
            self.browsers[self] = data
            log.info('Added -> %r' % data)
        else if message == 'reload':
            self.reload(data)
        else if message == 'watch':
            log.info('To watch: %s' % data)
        else if message == 'unwatch':
            log.info('To unwatch: %s' % data)
        else:
            log.warn('Unknown message: %s' % message)


    def on_close(self):
        if self in self.browsers:
            ua = self.browsers.pop(self)
            log.info('Lost -> %r' % ua)
        else:
            log.info('Lost annonymous connection')


def monkey_patch_http_server(query, callback=None, **kwargs):
    from BaseHTTPServer import HTTPServer
    old_serve_forever = HTTPServer.serve_forever

    def new_serve_forever(self):
        rc.reload(query)
        if callback:
            callback(self)
        old_serve_forever(self)

    HTTPServer.serve_forever = new_serve_forever


tornado.options.define("debug", default=False, help="Debug mode")
tornado.options.define("server_host", default='127.0.0.1',
                       help="Server and websocket host")
tornado.options.define("server_port", default=50637,
                       help="Server and websocket port")
tornado.options.parse_command_line()

server = tornado.web.Application(
    [
        (r"/", IndexHandler),
        (r"/wsreload", WebSocketHandler),
    ],
    debug=tornado.options.options.debug,
    static_path=os.path.join(os.path.dirname(__file__), "static"),
    template_path=os.path.join(os.path.dirname(__file__), "templates")
)
