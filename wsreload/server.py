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
import tornado.ioloop
import pyinotify
import logging
import json


log = logging.getLogger('wsreload')
ioloop = tornado.ioloop.IOLoop.instance()


class Watcher(pyinotify.TornadoAsyncNotifier):
    def __init__(self, files, query):
        log.debug('Watching for %s' % files)
        inotify = pyinotify.WatchManager()
        self.files = files
        self.query = query
        self.notifier = pyinotify.TornadoAsyncNotifier(
            inotify, ioloop, self.notified, pyinotify.ProcessEvent())
        inotify.add_watch(
            files, pyinotify.EventsCodes.ALL_FLAGS['IN_CLOSE_WRITE'])

    def notified(self, notifier):
        log.debug('Got notified for %s' % self.files)
        WebSocketHandler.reload(self.query)

    def close(self):
        log.debug('Closing for %s' % self.files)
        self.notifier.stop()


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    browsers = {}
    watchers = {}

    def __init__(self, *args, **kwargs):
        super(WebSocketHandler, self).__init__(*args, **kwargs)
        self.self_watches = set()

    @classmethod
    def reload(cls, query):
        log.info('Reloading for query %s' % query)
        for browser, ua in cls.browsers.items():
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

        elif message == 'reload':
            self.reload(data)

        elif message == 'watch':
            log.info('To watch: %s' % data)
            if not data in self.watchers:
                self.watchers[data] = Watcher(
                    data, '{"url": "file://%s"}' % data)
                self.self_watches.add(data)

        elif message == 'unwatch':
            log.info('To unwatch: %s' % data)
            if data in self.self_watches:
                self.self_watches.remove(data)
            if data in self.watchers:
                self.watchers.pop(data).close()

        elif message == 'watch_files':
            log.info('To watch: %s' % data)
            data = json.loads(data)
            files = data['files']
            query = data['query']
            self.watchers[str(sorted(files))] = Watcher(files, query)

        elif message == 'unwatch_files':
            log.info('To unwatch: %s' % data)
            files = str(sorted(json.loads(data)))
            if files in self.watchers:
                self.watchers.pop(files).close()
        else:
            log.warn('Unknown message: %s' % message)

    def on_close(self):
        for watch in self.self_watches:
            if watch in self.watchers:
                self.watchers.pop(watch).close()

        if self in self.browsers:
            ua = self.browsers.pop(self)
            log.info('Lost -> %r' % ua)
        else:
            log.info('Lost annonymous connection')


tornado.options.define("debug", default=False, help="Debug mode")
tornado.options.define("server_host", default='127.0.0.1',
                       help="Server and websocket host")
tornado.options.define("server_port", default=50637,
                       help="Server and websocket port")
tornado.options.parse_command_line()


server = tornado.web.Application(
    [
        (r"/wsreload", WebSocketHandler),
    ],
    debug=tornado.options.options.debug

)
