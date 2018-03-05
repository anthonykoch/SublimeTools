import collections

import sublime

from sublime import Region

from .Utils import pluck


def is_length(value):
    return isinstance(value, int) and value >= 0


class Position(object):
    """
    Represents an AST position object.
    Represents
    """

    def __init__(self, start=None, end=None):
        self.a = start if is_length(start) else None

        if end is None:
            self.b = start
        else:
            self.b = end if is_length(end) else None

    def __getitem__(self, key):
        """
        Allow subscripting with start/end or 0, 1
        """
        if key == 'start' or key == 0:
            return self.a
        elif key == 'end' or key == 1:
            return self.b

        return None

    def __str__(self):
        return '({}, {})'.format(self.a, self.b)

    def __eq__(self, other):
        """
        Allows comparing with regions or other iterables
        """

        if isinstance(other, Region):
            return other.begin() == self.a and other.end() == self.b

        if not isinstance(other, collections.Iterable) or len(other) < 2:
            return False

        return other[0] == self.a and other[1] == self.b

    def __iter__(self):
        yield self.a
        yield self.b

    def __len__(self):
        return 2

    def begin(self):
        """ Returns the start of the position """
        return self.a

    def end(self):
        """ Returns the end of the position """
        return self.b

    def has_begin(self):
        """ Returns true if the start is an int and more than -1 """
        return is_length(self.a)

    def has_end(self):
        """ Returns true if the end is an int and more than -1 """
        return is_length(self.b)

    def is_valid(self):
        """ Returns true if the start and end are ints and more than -1 """
        return self.has_begin() and self.has_end()

    def to_region(self):
        """ Converts the position to a region """
        return Region(self.a, self.b)

    def to_json(self):
        return {
            'start': self.a,
            'end': self.b,
        }


class SimpleLocation(object):
    """
    Creates a simple location representing a line and column.
    """

    def __init__(self, line, column, **kwargs):
        self.line = line if is_length(line) else None
        self.column = column if is_length(column) else None

    def __getitem__(self, key):
        if key == 'line':
            return self.line
        elif key == 'column':
            return self.column

        return None

    def __iter__(self):
        """ Allow destructuring """
        yield self.line
        yield self.column

    def __str__(self):
        return '({}:{})'.format(self.line, self.column)

    def has_line(self):
        """ Return true if the line is an int and more than -1 """
        return is_length(self.line)

    def has_column(self):
        """ Return true if the column is an int and more than -1 """
        return is_length(self.column)

    def is_valid(self):
        """ Return true if both the line and column are ints and more than -1 """
        return self.has_line() and self.has_column()

    def to_point(self, view):
        """ Converts the line and column to a point in a view's buffer """

        if self.is_valid():
            return view.text_point(self.line, self.column)

        return None

    def to_region(self, view):
        """
        Returns:
            None if the line or column are invalid or an empty region with
        """
        if self.is_valid():
            return Region(self.to_point(view))

        return None

    def to_json(self):
        return { 'line': self.line, 'column': self.column }


class ComplexLocation(object):
    """
    Represents a complex location that has both starting line and columns, as well
    as ending line and columns.

    Attributes:
        start (SimpleLocation): The starting location
        end (SimpleLocation): The ending location
    """

    def __init__(self, start=None, end=None, **kwargs):
        self.start = SimpleLocation(*pluck(start, 'line', 'column'))
        self.end = SimpleLocation(*pluck(end, 'line', 'column'))

    def to_region(self, view):
        """
        Returns a region spanning from the start line and column to the end line and colum, or
        None if the start or end locations have invalid line or columns.

        Args:
            view (sublime.View): The view's buffer will be used in calculating the region's points

        Returns:
            sublime.Region or None if the start or end location are invalid
        """

        if not self.start.is_valid() or not self.end.is_valid():
            return None

        start_point = self.start.to_point(view)
        end_point = self.end.to_point(view)

        return Region(start_point, end_point)


class RenderLocation(object):

    """
    A render location is either created from a position (start and end), complex
    location, or both.

    Examples:
        simple_loc = { 'line': 0, 'column': 0 }
        complex_loc = {
            'start': { 'line': 0, 'column': 0 },
            'end': { 'line': 0, 'column': 0 },
        }
        position = { 'start': 0, 'end': 0 }
    """

    BEGIN = 1 << 0
    END = 1 << 1
    START_LINE = 1 << 2
    START_COLUMN = 1 << 3
    END_LINE = 1 << 4
    END_COLUMN = 1 << 5

    def __init__(self, position=None, start=None, end=None, **kwargs):
        pos_start, pos_end = pluck(position, 'start', 'end')

        self.loc = ComplexLocation(start=start, end=end)
        self.pos = Position(start=pos_start, end=pos_end)

    def __str__(self):
        return str(self.to_json())

    def to_json(self):
        return {
            'start': self.loc.start.to_json(),
            'end': self.loc.end.to_json(),
        }

    def render_ability(self):
        """
        Returns a mask of the the locations that are available.
        """

        mask = 0
        mask |= RenderLocation.BEGIN        if self.pos.has_begin()        else 0
        mask |= RenderLocation.END          if self.pos.has_end()          else 0
        mask |= RenderLocation.START_LINE   if self.loc.start.has_line()   else 0
        mask |= RenderLocation.START_COLUMN if self.loc.start.has_column() else 0
        mask |= RenderLocation.END_LINE     if self.loc.end.has_line()     else 0
        mask |= RenderLocation.END_COLUMN   if self.loc.end.has_column()   else 0

        return mask

    def start_line(self, view):
        if self.loc.start.has_line():
            return self.loc.start.line
        elif self.pos.has_begin():
            return view.rowcol(self.pos.begin())[0]

        return None

    def end_line(self, view):
        if self.loc.end.has_line():
            return self.loc.end.line
        elif self.pos.has_end():
            return view.rowcol(self.pos.end())[0]

        return None

    def start_point(self, view):
        if self.pos.has_begin():
            return self.pos.begin()
        elif self.loc.start.is_valid():
            return self.loc.start.to_point(view)

        return None

    def end_point(self, view):
        if self.pos.has_end():
            return self.pos.end()
        elif self.loc.end.is_valid():
            return self.loc.end.to_point(view)

        return None


def get_from_loc(loc, side, attr):
    """
    Examples:
        loc = {
            'start': {
                'column': 23,
                'line': 40,
            },
            'end': {
                'column': 42,
                'line': 68,
            },
        }

        get_from_loc(loc, 'start', 'column') # 23
        get_from_loc(loc, 'end', 'line') # 68

    Args:
        loc (dict): The loc object
        side (str): Either 'start' or 'end'
        attr (str): Either 'line' or 'column'

    Raises:
        Exception is side is not "start" or "end"

    Returns:
        None if the loc or side of the loc chosen is not a dict
    """

    if side not in ['start', 'end']:
        raise Exception('side(enum:"start"|"end"), got ' + str(side))
    elif attr not in ['line', 'column']:
        raise Exception('side (enum:"line"|"column"), got ' + str(attr))

    if isinstance(loc, dict):
        if side in loc and isinstance(loc[side], dict):
            value = loc[side].get(attr)

            if isinstance(value, int) and value >= 0:
                return value

    return None


def all_views():
    """
    Gets all views in all windows

    Returns:
        list of sublime.View
    """

    views = []

    for window in sublime.windows():
        for view in window.views():
            views.append(view)

    return views


def get_views_by_ids(ids):
    """
    Returns a list of views whose ids match the ids passed.

    Args:
        ids (list of int): The ids to match against

    Returns:
        list of sublime.View
    """

    return [view for view in all_views() if view.id() in (ids if isinstance(ids, list) else [ids])]


def get_views_by_file_names(file_names, basename=False):
    """
    Get views by the specified filenames.

    Args:
        file_names (str|list): A filename or list of filenames
        basename (boolean, optional): Whether or not to match the basename

    Returns:
        list of views that match the filenames passed
    """
    if not isinstance(file_names, list):
        file_names = [file_names]

    views = []

    if basename:
        for view in all_views():
            for file_name in file_names:
                if view.file_name() and os.path.basename(view.file_name()) == os.path.basename(file_name):
                    views.append(view)
    else:
        for window in sublime.windows():
            for file_name in file_names:
                view = window.find_open_file(file_name)
                if view:
                    views.append(view)

    return views


def get_source_scope(view):
    """
    Args:
        view (sublime.View): The view to retrieve the source scope from

    Returns:
        The source scope for the view
    """

    return view.scope_name(0).split(' ')[0]


