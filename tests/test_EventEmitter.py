import sublime
import sys

from unittest import TestCase
from unittest.mock import MagicMock

version = sublime.version()

from SublimeTools.EventEmitter import EventEmitter


class TestCase(TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_event_emitter(self):
        """ Event Emitter is all good :) """

        payload = {}
        mock = MagicMock()
        ee = EventEmitter()
        ee.on('order', mock)
        ee.emit('order', payload)

        mock.assert_called_with(payload)

        ee.off('order', mock)
        ee.emit('order', payload)

        self.assertEqual(mock.call_count, 1)

    def event_emitter_decorators(t):
        """ on can be used as a decorator """
        ee = EventEmitter()
        order = None
        expected = 123

        @ee.on('order')
        def listener():
            nonlocal order
            order = expected

        ee.emit('order')

        t.assertEqual(order, expected)

    def event_emitter_wildcards(t):
        """ on can be used as a decorator """
        ee = EventEmitter(wildcard=True, delimiter=':')

        mock = MagicMock()
        ee.on('order:*', mock)
        ee.emit('order:milk', mock)

        t.assertEqual(mock.called_once, 1)




