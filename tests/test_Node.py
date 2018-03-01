import sublime
import sys

from unittest import TestCase
from unittest.mock import MagicMock

from unittesting import DeferrableTestCase

from SublimeTools.Node import NodeEnv, assert_node_path, get_settings_node_path, get_node_env
from SublimeTools.cuid import cuid
from SublimeTools import Node

settings_name = 'SublimeTools.sublime-settings'

class TestCase(DeferrableTestCase):

    def tearDown(self):
        self.write_settings({})

    def write_settings(self, obj):
        import os
        import json

        settings_file = os.path.join(sublime.packages_path(), 'user', settings_name)

        with open(settings_file, 'w') as f:
            f.write(json.dumps(obj))

    def test_get_settings_node_path(self):
        """ should get node path from a sublime settings object """

        node_path = {
            'osx': '/osx/path/to/node',
            'linux': '/linux/path/to/node',
            'windows': 'C:/path/to/node',
        }

        settings = sublime.load_settings(cuid())
        yield 200
        self.assertEqual(settings.get('node_path'), None)
        settings.set('node_path', node_path)
        self.assertEqual(get_settings_node_path(settings=[settings]), node_path[sublime.platform()])

    def test_get_node_env(self):
        """ should contain info about the node environment """

        mock = MagicMock()
        get_node_env(on_done=mock)

        yield 3000

        self.assertIsNotNone(mock.return_value)
        self.assertTrue(mock.called_once)

    def test_node_env(self):
        """ The node env is loaded """

        yield 2500
        self.assertIsNotNone(Node.node_env, msg='node env loads when sublime loads')

    def test_node_env_get_preferred(self):
        """ should return the preferred node_path """

        user_settings_node_path = cuid()
        system_node_path = cuid()
        nvm_default_path = cuid()

        env = NodeEnv(
            system_node_path=system_node_path,
            nvm_default_path=nvm_default_path,
        )

        self.write_settings({
            'node_path': {
                'osx': user_settings_node_path,
                'linux': user_settings_node_path,
                'windows': user_settings_node_path,
            }
        })
        yield 500
        self.assertEqual(env.get_preferred(), user_settings_node_path, 'prefers SublimeTools node_path setting first')

        self.write_settings({ 'prefer': 'system' })
        yield 500
        self.assertEqual(env.get_preferred(), system_node_path, msg='system gets system node path')

        self.write_settings({ 'prefer': 'nvm_default' })
        yield 500
        self.assertEqual(env.get_preferred(), nvm_default_path, msg='nvm_default gets nvm default path')

        self.write_settings({})
        yield 500
        self.assertEqual(env.get_preferred(), system_node_path, msg='Defaults to default prefer setting')
