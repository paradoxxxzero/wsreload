import json
import cherrypy
from ws4py.client.threadedclient import WebSocketClient
from ws4py.server.cherrypyserver import WebSocketPlugin, WebSocketTool
from ws4py.messaging import TextMessage
from ws4py.websocket import WebSocket


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


def serve_forever(host, port):
    WebSocketPlugin(cherrypy.engine).subscribe()
    cherrypy.tools.websocket = WebSocketTool()

    cherrypy.config.update({
        'server.socket_host': host,
        'server.socket_port': port
    })

    cherrypy.quickstart(Root(), '/', config={'/': {
        'tools.websocket.on': True,
        'tools.websocket.handler_cls': BroadcastWebSocket}
    })


class ReloadClient(WebSocketClient):
    def __init__(self, host='127.0.0.1', port=50637, endpoint='wsreload',
                 protocols=None, extensions=None,
                 default_query=None, open_query=None):
        WebSocketClient.__init__(
            self, 'ws://%s:%s/%s' % (host, port, endpoint),
            protocols, extensions)
        self.default_query = default_query
        self.open_query = open_query
        self.connect()

    def reload(self, query=None):
        self.send(json.dumps(query or self.default_query))

    def opened(self):
        if self.open_query:
            self.reload(self.open_query)


def monkey_patch_http_server(query, callback=None, **kwargs):
    from BaseHTTPServer import HTTPServer
    old_serve_forever = HTTPServer.serve_forever
    rc = ReloadClient(**kwargs)

    def new_serve_forever(self):
        rc.reload(query)
        if callback:
            callback(self)
        old_serve_forever(self)

    HTTPServer.serve_forever = new_serve_forever
