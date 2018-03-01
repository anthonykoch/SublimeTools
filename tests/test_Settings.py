import sublime
import sys

from unittesting import DeferrableTestCase
from unittest.mock import MagicMock

from SublimeTools.Settings import Settings
from SublimeTools.cuid import cuid


version = sublime.version()

settings_name = 'SublimeTools.sublime-settings'


class TestSettings(DeferrableTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        self.write_settings({})

    def write_settings(self, obj):
        import os
        import json

        settings_file = os.path.join(sublime.packages_path(), 'user', settings_name)

        with open(settings_file, 'w') as f:
            f.write(json.dumps(obj))

    def test_settings_update(self):
        """ The settings changes when the the settings file is written to """
        import os

        expected = 123456
        settings = Settings(settings_name)
        key = cuid()
        settings.set(key, expected)

        self.assertIsNotNone(getattr(settings, 'loaded_settings', None))
        self.assertIsInstance(settings.loaded_settings, sublime.Settings)

        self.write_settings({ key: expected })

        yield 500

        self.assertEqual(settings.get(key), expected)

    def test_settings_get(self):
        """ Get's a value by key """

        expected = 'coconut'
        key = cuid()
        self.write_settings({ key: expected })

        yield 500

        settings = Settings(settings_name)

        self.assertEqual(settings.get(key), expected)

        self.assertEqual(
            settings.get('nonexistantkey', default=123),
            123,
            msg='Returns default is settings does have the key'
        )


    def test_settings_has(self):
        """ Get's a value by key """

        expected = 'coconut'
        key = cuid()
        self.write_settings({ key: expected })

        yield 500

        settings = Settings(settings_name)

        self.assertTrue(settings.has(key))
        self.assertFalse(settings.has('lmao'))
