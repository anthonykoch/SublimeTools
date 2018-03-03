import sublime
import sys

from unittesting import DeferrableTestCase
from unittest.mock import MagicMock

from SublimeTools.Exec import exec_cmd, execjsfile, ProcessListener
from SublimeTools.cuid import cuid


version = sublime.version()


class TestExec(DeferrableTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_listener_events(self):
        """ process listener emits events """

        import os

        proc = exec_cmd('echo lmao', listener=listener)

        yield 2500

        on_data.assert_called_with(proc, bytes('lmao{0}'.format(os.linesep), 'utf8'))
        on_finish.assert_called_with(proc, bytes('lmao{0}'.format(os.linesep), 'utf8'))

        self.assertEqual(listener.data, bytes('lmao' + os.linesep, 'utf8'))

    def test_listener_events(self):
        """ process listener emits events """

        import os

        listener = ProcessListener()

        on_data = MagicMock()
        on_finish = MagicMock()

        listener.on('data', on_data)
        listener.on('finish', on_finish)

        proc = exec_cmd('echo lmao', listener=listener)

        yield 2500

        on_data.assert_called_with(proc, bytes('lmao{0}'.format(os.linesep), 'utf8'))
        on_finish.assert_called_with(proc, bytes('lmao{0}'.format(os.linesep), 'utf8'))

        self.assertEqual(listener.data, bytes('lmao' + os.linesep, 'utf8'))

    def test_exec_cmd_listener(self):
        """ exec_cmd calls handle methods on listener class """

        import os

        listener = ProcessListener()

        listener.handle_data = MagicMock()
        listener.handle_finish = MagicMock()

        proc = exec_cmd('echo lmao', listener=listener)

        yield 2500

        listener.handle_data.assert_called_with(proc, bytes('lmao{0}'.format(os.linesep), 'utf8'))
        listener.handle_finish.assert_called_with(proc)

        self.assertEqual(listener.data, bytes('lmao' + os.linesep, 'utf8'))

    def test_exec_cmd_callbacks(self):
        """ exec_cmd calls callbacks """

        import os

        on_data = MagicMock()
        on_finish = MagicMock()

        proc = exec_cmd('echo lmao;', on_finish=on_finish, on_data=on_data)

        yield 2500

        on_data.assert_called_with(proc, bytes('lmao{0}'.format(os.linesep), 'utf8'))
        on_finish.assert_called_with(proc, bytes('lmao{0}'.format(os.linesep), 'utf8'))

    def test_exec_cmd_raises(self):
        """ exec_cmd raises ex when on_finish, on_done, and listener is not passed """

        self.assertRaises(lambda: exec_cmd('echo "lol"'), msg='wtf')
