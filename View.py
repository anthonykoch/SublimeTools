import sublime

from sublime import Region


def get_loc_region(view, loc):
    """
    Returns a region from a complex loc object spanning from loc start line/column
    to loc end line/column. If any of the loc info is invalid, A region with -1 for both
    points are returned.

    Line and columns start at 0

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

    Args:
        view (sublime.View): The view to get the region from
        loc (any): A complex loc object

    Returns:
        sublime.Region
    """

    start_line = get_from_loc(loc, 'start', 'line')
    start_column = get_from_loc(loc, 'start', 'column')
    end_line = get_from_loc(loc, 'end', 'line')
    end_column = get_from_loc(loc, 'end', 'column')

    # print(start_line, start_column, end_line, end_column)

    if start_line is None or start_column is None or end_line is None or end_column is None:
        return None

    start_region = Region(view.text_point(start_line, start_column))
    end_region = Region(view.text_point(end_line, end_column))

    # end = view.line(view.text_point(line - 1, column - 1) ).end()

    return Region(start_region.begin(), end_region.end())


def get_position_region(pos):
    """
    Returns a region from a position

    Args:
        view (sublime.View):
        pos (any): The value to get the position from

    Returns:
        sublime.Region as reg with the reg.begin() being the pos['start']
        and reg.end() being position['end']. If either start or end is
        invalid, the value in the region will be -1.
    """

    if not isinstance(pos, dict):
        return Region(-1, -1)

    start = pos.get('start')
    end = pos.get('end')

    if not isinstance(start, int) or start < 0:
        start = -1

    if not isinstance(end, int) or end < 0:
        end = -1

    if start > end:
        start = -1
        end = -1

    return Region(start, end)


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


def get_simple_loc_region(view, loc):
    """
    Returns a region from a simple. If either the line or column is invalid
    Region(-1, -1) will be returned

    Args:
        view (sublime.View): The buffer to get the region from
        loc (dict): A dict with at least a line key.

    Returns:
        sublime.Region
    """

    line = loc.get('line')
    column = loc.get('column')

    if not isinstance(line, int) or line <= 0:
        return None

    if not isinstance(column, int) or column <= 0:
        return None

    return sublime.Region(view.text_point(line, column))


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


