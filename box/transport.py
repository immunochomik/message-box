import json


class Message(object):
    __slots__ = ['id', 'verb', 'params', 'errors']

    def __init__(self):
        self.errors = []


class Transport(object):
    expected = [
        'id',
        'verb',
        'params?'
    ]

    @classmethod
    def received(cls, payload):
        message = Message()

        try:
            data = json.loads(payload.decode('utf8'))
        except Exception as exc:
            message.errors.append(exc)
        else:
            for key in cls.expected:
                required, key = cls._required(key)
                if key in data:
                    setattr(message, key, data[key])
                elif required:
                    message.errors.append('Missing required key {}'.format(key))
        return message

    @classmethod
    def _required(cls, key):
        required = True
        if key[-1] == '?':
            required, key = False, key[:-1]
        return required, key

    @classmethod
    def to_send(cls, data):
        verified = dict()
        for key in cls.expected:
            required, key = cls._required(key)
            if key in data:
                verified[key] = data[key]
            elif required:
                raise ValueError('Missing required key {}'.format(key))
        return json.dumps(verified)

