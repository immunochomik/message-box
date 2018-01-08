import json
import sys
import time
import uuid

from autobahn.twisted.resource import WebSocketResource, WSGIRootResource
from autobahn.twisted.websocket import WebSocketServerFactory, WebSocketServerProtocol
from flask import Flask, request
from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource


from box.relay import Relay
from box.transport import Transport

app = Flask(__name__)
app.secret_key = str(uuid.uuid4())

relay = Relay()


class WaitingServerProtocol(WebSocketServerProtocol):

    def onMessage(self, payload, isBinary):
        m = Transport.received(payload)
        if m.errors:
            # log error and send it back
            return self.sendClose(code=3400, reason=self.encode(m.errors))
        relay.wait_for(_id=m.id, connection=self)
        self.sendMessage(payload=self.encode('{"status":"waiting"}'))

    def found(self, data):
        self.sendMessage(self.encode(data))
        return self.sendClose(code=3200, reason=u'FOUND')

    @staticmethod
    def encode(obj):
        if isinstance(obj, bytes):
            return obj
        if isinstance(obj, str):
            return obj.encode('utf8')
        return json.dumps(obj, ensure_ascii=False).encode('utf8')


@app.route('/success', methods=['POST'])
def success():
    print(request)
    relay.done_add(request.form['_id'], {
        'status': 'done',
        'time': time.time(),
        'data': request.form['data'],
    })
    return 'OK'


@app.route('/', methods=['GET'])
def home():
    return 'This is home'


def start_server(host='127.0.0.1', port=8080):

    relay.start(1)

    log.startLogging(sys.stdout)

    # create a Twisted Web resource for our WebSocket server
    wsFactory = WebSocketServerFactory(u"ws://{}:{}".format(host, port))
    wsFactory.protocol = WaitingServerProtocol
    wsResource = WebSocketResource(wsFactory)

    # create a Twisted Web WSGI resource for our Flask server
    wsgiResource = WSGIResource(reactor, reactor.getThreadPool(), app)

    # create a root resource serving everything via WSGI/Flask, but
    # the path "/ws" served by our WebSocket stuff
    rootResource = WSGIRootResource(wsgiResource, {b'ws': wsResource})

    # create a Twisted Web Site and run everything
    site = Site(rootResource)

    reactor.listenTCP(8080, site)
    reactor.run()


def usage():
    print "Usage {} port [host]".format(sys.argv[0])
    sys.exit(1)


if __name__ == "__main__":
    try:
        port = int(sys.argv[1])
    except (ValueError, IndexError):
        usage()
    else:
        host = sys.argv[2] if len(sys.argv) > 2 else 'localhost'
        start_server(host=host, port=port)
