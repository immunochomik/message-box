from __future__ import print_function
import json

from twisted.internet.task import LoopingCall


def print_waiting(waiting):
    rep = dict()
    for key, val in waiting.items():
        rep[key] = repr(val)
    print(json.dumps(rep, indent=2))


class Relay(object):
    def __init__(self):
        self.waiting = dict()
        self.done = dict()
        self._started = False

    def start(self, interval):
        if not self._started:
            looping = LoopingCall(self.check_done)
            looping.start(interval=interval)
            self._started = True

    def wait_for(self, _id, connection):
        if _id in self.done:
            return connection.found(data=self.done.pop(_id))
        if _id not in self.waiting:
            self.waiting[_id] = connection
            print_waiting(self.waiting)
        else:
            print('WARNING id {} already in waiting'.format(_id))

    def done_add(self, _id, data):
        if _id in self.waiting:
            connection = self.waiting.pop(_id)
            return connection.found(data=data)
        if _id in self.done:
            print("WARNING {} in store".format(_id))
        data[_id] = _id
        self.done[_id] = data
        print(json.dumps(self.done, indent=2))

    def check_done(self):
        print('check_done')
        if self.waiting:
            print('waiting')
            for _id in [_id for _id in self.waiting if _id in self.done]:
                connection = self.waiting.pop(_id)
                connection.found(data=self.done.pop(_id))
