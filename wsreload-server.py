#!/usr/bin/env python2.7
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

import argparse
import cherrypy

from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.messaging import TextMessage
from ws4py.websocket import WebSocket

parser = argparse.ArgumentParser(
    description='wsreload server',
    prog='wsreload-server',
    version='1.0')

parser.add_argument('-H', '--host', dest='host', type=str, default='127.0.0.1')
parser.add_argument('-P', '--port', dest='port', type=int, default=50637)

args = parser.parse_args()

WebSocketPlugin(cherrypy.engine).subscribe()
cherrypy.tools.websocket = WebSocketTool()


class BroadcastWebSocket(WebSocket):
    def received_message(self, m):
        cherrypy.log('Transmitting %s' % m)
        cherrypy.engine.publish(
            'websocket-broadcast',
            TextMessage('%s' % m))


class Root(object):

    @cherrypy.expose
    def default(self):
        return ''

    def __getattr__(self, name):
        if name.startswith('_') or name == 'exposed':
            return object.__getattr__(name)
        else:
            return self.default

cherrypy.config.update({
    'server.socket_host': args.host,
    'server.socket_port': args.port
})

cherrypy.quickstart(Root(), '/', config={'/': {
    'tools.websocket.on': True,
    'tools.websocket.handler_cls': BroadcastWebSocket}})
