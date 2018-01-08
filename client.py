import json
import sys

from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory

from box.transport import Transport


class MyClientProtocol(WebSocketClientProtocol):

    def __init__(self, _id):
        super(MyClientProtocol, self).__init__()
        self._id = _id

    def onConnect(self, response):
        print("Server connected: {0}".format(response.peer))
        self.factory.resetDelay()

    def onOpen(self):
        print("WebSocket connection open.")
        payload = Transport.to_send({'id': self._id, 'verb': 'GET'})
        self.sendMessage(payload)

    def onMessage(self, payload, isBinary):
        if not isBinary:
            print("Message received: {0}".format(payload))
            data = json.loads(payload)
            if data['status'] == 'done':
                print('DONE')
                self.sendClose(code=3200, reason=u'OK')
                self.factory.result = data

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: wasClean: {} code: {} reason: {}".format(wasClean, code, reason))


class MyClientFactory(WebSocketClientFactory, ReconnectingClientFactory):

    def __init__(self, *args, **kwargs):
        super(MyClientFactory, self).__init__(*args, **kwargs)
        self.result = None

    def buildProtocol(self, addr):
        proto = MyClientProtocol(self._id, )
        proto.factory = self
        return proto

    def clientConnectionFailed(self, connector, reason):
        print("Client connection failed {} {}".format(connector, reason))
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        if not self.result:
            print("Client connection lost {}".format(reason))
            self.retry(connector)
        else:
            print('Stop reactor')
            print (self.result)


def get_results(_id, host='127.0.0.1', port=8080):
    factory = MyClientFactory('ws://{}:{}/ws'.format(host, port))
    factory._id = _id

    reactor.connectTCP(host, port, factory)
    reactor.run()


def usage():
    print "Usage {} id port [host]".format(sys.argv[0])
    sys.exit(1)


if __name__ == "__main__":
    log.startLogging(sys.stdout)
    try:
        _id = sys.argv[1]
        port = int(sys.argv[2])
    except (ValueError, IndexError):
        usage()
    else:
        host = sys.argv[3] if len(sys.argv) > 3 else 'localhost'
        get_results(_id=_id, host=host, port=port)

