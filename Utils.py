import sublime_plugin
import sublime
import traceback
import os
import time
import string
import random

from Default.exec import AsyncProcess

from collections import defaultdict
from contextlib import contextmanager


def get_settings_node_path(settings=[]):
    """
    Returns the node_path from a settings object, or None if it doesn't
    exist.

    Args:
        settings (list): A list of settings to retrieve the node_path from
    """

    for setting in settings:
        paths = setting.get('node_path', {})

        if not isinstance(paths, dict):
            continue

        node_path = paths[sublime.platform()] if sublime.platform() in paths else None

        if node_path is not None:
            return node_path


# https://stackoverflow.com/questions/2955412/python-destructuring-bind-dictionary-contents
pluck = lambda dict, *args: (dict.get(arg) for arg in args)


def all_views():
    """ Get all views from every window """

    views = []
    for window in sublime.windows():
        for view in window.views():
            views.append(view)
    return views


def get_views_by_ids(ids):
    """
    Returns a list of views whose ids match the ids passed
    ids (list):
    """

    return [view for view in all_views() if view.id() in (ids if isinstance(ids, list) else [ids])]


def get_views_by_file_names(file_names, basename=False):
    """
    Get views by the specified filenames
    file_names (str|list):
    basename (boolean, optional): Whether or not to match the basename
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
    Returns the source scope of the page, such as source.python
    view (sublime.View)
    """

    return view.scope_name(0).split(' ')[0]


def nth(items, index):
    """
    Return an item from a list by index, or None if the index does not exist
    items (list): The list to get the nth item from
    index (int): The index of the item to get
    """

    if index < len(items):
        return items[index]


def create_hex_id(length=20):
    return ''.join([random.choice(string.hexdigits.lower()) for i in range(0, int(length))])

def create_int_id(length=20):
    return int(''.join([random.choice(string.digits) for i in range(0, int(length))]))


def incremental_id_factory():
    index = 0

    def create_incremental_id():
        nonlocal index
        index += 1
        return index

    return create_incremental_id

