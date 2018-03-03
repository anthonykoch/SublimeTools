import sublime
import sys

from unittesting import DeferrableTestCase
from unittest.mock import MagicMock

from SublimeTools.View import *
from SublimeTools.cuid import cuid


version = sublime.version()

views = []


class TestExec(DeferrableTestCase):

    def setUp(self):
        pass

    def tearDown(self):
        yield 1000

        for view in views:
            window = view.window()

            if window:
                window.focus_view(view)
                window.run_command('close_file')

    def create_file(self, contents=''):
        window = self.window = sublime.active_window()
        self.view = window.new_file()
        self.view.run_command('insert', { 'characters': contents })
        self.view.set_scratch(True)
        self.view.set_read_only(True)
        views.append(self.view)

    def test_get_loc_region(self):
        """ get_loc_region gets region from loc """

        view_contents = "How could this happen to me?\nI've made my mistakes."
        self.create_file(contents=view_contents)


        region_1 = get_loc_region(self.view, {
            'start': { 'line': 0, 'column': 0 }, 'end': { 'line': 0, 'column': 0 },
        })
        self.assertIsNotNone(region_1)
        self.assertEqual(region_1.begin(), 0)
        self.assertEqual(region_1.end(), 0)


        region_2 = get_loc_region(self.view, {
            'start': { 'line': 0, 'column': 4 }, 'end': { 'line': 1, 'column': 2 },
        })
        self.assertIsNotNone(region_2)
        self.assertEqual(region_2.begin(), 4)
        self.assertEqual(region_2.end(), 31)


        invalid_locs = [
            { 'start': { 'line': -1, 'column': 0 }, 'end': { 'line': 0, 'column': 0 } },
            { 'start': { 'line': 0, 'column': -1 }, 'end': { 'line': 0, 'column': 0 } },
            { 'start': { 'line': 0, 'column': 0 }, 'end': { 'line': -1, 'column': 0 } },
            { 'start': { 'line': 0, 'column': 0 }, 'end': { 'line': 0, 'column': -1 } },
            { 'start': { 'line': '0', 'column': 0 }, 'end': { 'line': 0, 'column': 0 } },
            { 'start': { 'line': 0, 'column': '0' }, 'end': { 'line': 0, 'column': 0 } },
            { 'start': { 'line': 0, 'column': 0 }, 'end': { 'line': '0', 'column': 0 } },
            { 'start': { 'line': 0, 'column': 0 }, 'end': { 'line': 0, 'column': '0' } },
        ]

        for loc in invalid_locs:
            region = get_loc_region(self.view, loc)
            self.assertIsNone(region)

    def test_get_position_region(self):
        self.assertEqual(get_position_region({ 'start': 0, 'end': 0 }).begin(), 0)
        self.assertEqual(get_position_region({ 'start': 0, 'end': 0 }).end(), 0)

        self.assertEqual(get_position_region({ 'start': 20, 'end': 40 }).begin(), 20)
        self.assertEqual(get_position_region({ 'start': 20, 'end': 40 }).end(), 40)

        self.assertEqual(get_position_region({ 'start': 100, 'end': 0 }).begin(), -1)
        self.assertEqual(get_position_region({ 'start': 100, 'end': 0 }).end(), -1)

    def test_get_from_loc(self):
        start_column = 23
        start_line = 40
        end_column = 42
        end_line = 68
        complex_loc = {
            'start': {'column': start_column, 'line': start_line, },
            'end': {'column': end_column, 'line': end_line, },
        }

        self.assertEqual(get_from_loc(complex_loc, 'start', 'line'), start_line)
        self.assertEqual(get_from_loc(complex_loc, 'start', 'column'), start_column)
        self.assertEqual(get_from_loc(complex_loc, 'end', 'line'), end_line)
        self.assertEqual(get_from_loc(complex_loc, 'end', 'column'), end_column)

        self.assertRaises(lambda: get_from_loc(complex_loc, 'what', 'line'))
        self.assertRaises(lambda: get_from_loc(complex_loc, 'start', 'hey'))

