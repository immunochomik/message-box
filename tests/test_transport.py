import json
from unittest import TestCase

from box.transport import Transport


class MessageTestCase(TestCase):

    def test_receive_with_correct_data_check_message(self):
        data = {
            'id': 10,
            'verb': 'GET'
        }
        m = Transport.received(json.dumps(data))
        self.assertEqual(10, m.id)
        self.assertEqual('GET', m.verb)

    def test_received_missing_required_check_errors(self):
        data = {
            'verb': 'GET'
        }
        m = Transport.received(json.dumps(data))
        self.assertEqual(m.errors, ['Missing required key id'])
        self.assertEqual(m.verb, 'GET')

    def test_send_missing_required_check_rises(self):
        data = {
            'verb': 'GET'
        }
        with self.assertRaises(ValueError) as context:
            Transport.to_send(data)
        self.assertEqual(context.exception.message, 'Missing required key id')

    def test_send_all_required_check_data(self):
        data = {
            'id': 5,
            'verb': 'GET'
        }

        payload = Transport.to_send(data)
        self.assertEqual(payload, '{"verb": "GET", "id": 5}')