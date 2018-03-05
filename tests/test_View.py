import sublime
import sys

from sublime import Region

from unittesting import DeferrableTestCase
from unittest.mock import MagicMock

from SublimeTools.View import *
from SublimeTools.cuid import cuid


version = sublime.version()

views = []
invalid_points = [None, '', -1, float('nan'), {}, []]


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

    def test_Position(self):
        for invalid in invalid_points:
            self.assertFalse(Position(invalid).has_begin())
            self.assertFalse(Position(invalid).has_end())
            self.assertFalse(Position(invalid, 1).has_begin())

        self.assertTrue(Position(1).has_begin())
        self.assertTrue(Position(1).has_end())
        self.assertTrue(Position(1, 0).has_end())

        self.assertFalse(Position().has_begin())
        self.assertFalse(Position().has_end())
        self.assertIsNone(Position().begin())
        self.assertIsNone(Position().end())
        self.assertEqual(Position(0, 2).to_region(), Region(0, 2))
        self.assertEqual(Position(0, 2), Region(0, 2))
        self.assertEqual(Position(0, 2), (0, 2))
        self.assertEqual(Position(0, 2), [0, 2])
        self.assertEqual(list(Position(0, 2)), [0, 2])

        begin, end = Position(0, 2)
        self.assertEqual(begin, 0, msg='position is iterable')
        self.assertEqual(end, 2)

    def test_SimpleLocation(self):
        contents = 'roflsandlawls\nsaxandviolins'

        self.create_file(contents=contents)
        self.assertTrue(SimpleLocation(1, 0).has_line())
        self.assertTrue(SimpleLocation(0, 0).has_line())

        self.assertTrue(SimpleLocation(0, 0).has_column())
        self.assertTrue(SimpleLocation(0, 1).has_column())

        for invalid in invalid_points:
            self.assertFalse(SimpleLocation(invalid, 0).has_line())
            self.assertFalse(SimpleLocation(0, invalid).has_column())
            self.assertFalse(SimpleLocation(invalid, 0).is_valid())
            self.assertFalse(SimpleLocation(0, invalid).is_valid())
            self.assertFalse(SimpleLocation(invalid, invalid).is_valid())

            self.assertIsNone(SimpleLocation(invalid, 0).to_point(self.view))
            self.assertIsNone(SimpleLocation(0, invalid).to_point(self.view))
            self.assertIsNone(SimpleLocation(invalid, invalid).to_point(self.view))

            self.assertIsNone(SimpleLocation(invalid, 3).to_region(self.view))
            self.assertIsNone(SimpleLocation(1, invalid).to_region(self.view))
            self.assertIsNone(SimpleLocation(invalid, invalid).to_region(self.view))

        self.assertEqual(SimpleLocation(0, 0).to_point(self.view), 0)
        self.assertEqual(SimpleLocation(0, len(contents) + 1).to_point(self.view), len(contents))
        self.assertEqual(SimpleLocation(1, 0).to_point(self.view), 14)
        self.assertEqual(SimpleLocation(1, 2).to_point(self.view), 16)

        self.assertEqual(SimpleLocation(12, 34).to_json(), { 'line': 12, 'column': 34, })
        self.assertEqual(SimpleLocation(0, 3).to_region(self.view), Region(3))

        self.assertEqual(SimpleLocation(2, 5)['line'], 2)
        self.assertEqual(SimpleLocation(2, 5)['column'], 5)
        self.assertIsNone(SimpleLocation(2, 5)['lol'])

        line, column = SimpleLocation(30, 50)

        self.assertEqual(line, 30)
        self.assertEqual(column, 50)

    def test_ComplexLocation(self):
        contents = 'whereareand\nandwhoarewe'

        self.create_file(contents=contents)

        self.assertEqual(
                ComplexLocation(start={ 'line': 0, 'column': 0 }, end={ 'line': 0, 'column': 4 }).to_region(self.view),
                Region(0, 4)
            )

        self.assertEqual(
                ComplexLocation(start={ 'line': 0, 'column': 0 }, end={ 'line': 1, 'column': 4 }).to_region(self.view),
                Region(0, 16),
                msg='spanning multiple lines'
            )

        self.assertEqual(
                ComplexLocation(start={ 'line': 1, 'column': 0 }, end={ 'line': 1, 'column': 6 }).to_region(self.view),
                Region(12, 18)
            )

        self.assertIsNone(ComplexLocation().to_region(self.view))
        self.assertIsNone(ComplexLocation(start={}, end={}).to_region(self.view))

        for invalid in invalid_points:
            self.assertIsNone(ComplexLocation(
                start={ 'line': invalid, 'column': 1 },
                end={ 'line': 1, 'column': 1 }
            ).to_region(self.view))

            self.assertIsNone(ComplexLocation(
                start={ 'line': 1, 'column': invalid },
                end={ 'line': 1, 'column': 1 }
            ).to_region(self.view))

            self.assertIsNone(ComplexLocation(
                start={ 'line': 1, 'column': 1 },
                end={ 'line': invalid, 'column': 1 }
            ).to_region(self.view))

            self.assertIsNone(ComplexLocation(
                start={ 'line': 1, 'column': 1 },
                end={ 'line': 1, 'column': invalid }
            ).to_region(self.view))


    def test_RenderLocation(self):
        contents = 'why oh why\noh whyyyyyyyyy'

        self.create_file(contents=contents)

        for invalid in invalid_points:
            self.assertEqual(RenderLocation(position={'start': 4, 'end': 2 }).start_point(self.view), 4)
            self.assertEqual(RenderLocation(position={'start': 4, 'end': invalid }).start_point(self.view), 4)
            self.assertIsNone(RenderLocation(position={'start': invalid, 'end': 12 }).start_point(self.view), 12)

            self.assertEqual(RenderLocation(position={'start': 2, 'end': 3 }).end_point(self.view), 3)
            self.assertEqual(RenderLocation(position={'start': 2, 'end': 3 }).end_point(self.view), 3)
            self.assertEqual(RenderLocation(position={'start': invalid, 'end': 3 }).end_point(self.view), 3)

            self.assertEqual(RenderLocation(start={'line': 1, 'column': 0}).start_point(self.view), 11)
            self.assertIsNone(RenderLocation(start={'line': invalid, 'column': 0}).start_point(self.view))
            self.assertIsNone(RenderLocation(start={'line': 0, 'column': invalid}).start_point(self.view))

            self.assertEqual(RenderLocation(end={'line': 1, 'column': 0}).end_point(self.view), 11)
            self.assertIsNone(RenderLocation(end={'line': invalid, 'column': 0}).end_point(self.view))
            self.assertIsNone(RenderLocation(end={'line': 0, 'column': invalid}).end_point(self.view))

        self.assertIsNone(RenderLocation().start_point(self.view))
        self.assertIsNone(RenderLocation().end_point(self.view))
