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


@contextmanager
def ignore(*exceptions, origin="", print_ex=True):
    try:
        yield exceptions
    except exceptions as exs:
        if print_ex:
            print('\n' + origin)
            traceback.print_exc(limit=None, file=None, chain=True)
            print()


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


def exec_cmd(
    command,
    listener=None,
    on_finish=None,
    on_data=None,
    working_dir='',
    env={},
    path='',
    shell=False
    ):
    # print('working_dir:', working_dir)

    if listener is None:
        listener = ProcessListener()

        if callable(on_finish):
            listener.on('finish', on_finish)
        elif callable(on_data):
            listener.on('data', on_data)
        else:
            raise Exception('Either a process listener or on_finish/on_data callbacks must be passed')


    if working_dir != '':
        os.chdir(working_dir)

    if shell:
        cmd = None
        shell_cmd = command;
    else:
        cmd = command
        shell_cmd = None

    child = AsyncProcess(cmd, shell_cmd, env, listener, path=path, shell=shell)
    child.pid = child.proc.pid

    return child


def execjs(content, **kwargs):
    """
    Compile a file with the plugin and execute it.
    The working_dir will be used as the base for `require`
    """

    cmd = ['node', '-e', content]

    if not isinstance(kwargs.get('working_dir')):
        raise Exception('working_dir is required')

    return exec_cmd(cmd, **kwargs)


def execjsfile(absfilename, args=[], **kwargs):
    """
    Compile a file with the plugin and execute it.
    The working_dir will be used as the base for `require`

    absfilename (str): An absolute path to the file
    working_dir (str): The working directory for the script, is used for the
                             base of requires.
    on_finished (callable): Called when the process is finished
    on_data (callable): Called when the process receives data
    """

    cmd = ['node', absfilename] + args

    return exec_cmd(cmd, **kwargs)


class EventEmitter(object):
    """ Allows subscribers to be notified of an event """

    def __init__(self):
        self.events = defaultdict(list)

    def emit(self, event_name, *args, **kwargs):
        """ Emits an event to all listeners """

        for cb in self.events[event_name]:
            cb(*args, **kwargs)

    def off(self, event_name, callback):
        """ Removes a listener from an event """

        callback_list = self.events[str(event_name)]
        self.events[event_name] = [cb for cb in callback_list if cb != callback]

    def on(self, event_name, callback):
        """ Adds a listener to an event """

        if callable(callback):
            self.events[str(event_name)].append(callback)


class Timer(object):

    def __init__(self):
        self.begin = 0
        self.end   = 0;

    def start_time(self, name=''):
        self.begin = time.perf_counter()

    def stop_time(self, name=''):
        self.end = time.perf_counter()

    def diff_time(self):
        return self.end - self.begin;

    def print_time(self, name=''):
        print(self.end - self.start_time)


class ProcessListener(EventEmitter, Timer):
    """
    A listener for AsyncProcess, to be used in tangent with exec_cmd(), execjs(), and execjsfile().
    The handlers for on

    Example:

    def handle_data(data, proc):
        pass

    def handle_finish(all_data, proc):
        pass

    listener = ProcessListener()
    listener.on('data', handle_data)
    listener.on('finish', handle_finish)
    exec_cmd('which node', listener)

    or

    clas AsyncListener(ProcessListener):
        def handle_data(data, proc):
            print(data)

        def handle_finish(proc):
            print(self.data)

    listener = ProcessListener()
    exec_cmd('which node', listener)
    """

    def __init__(self):
        super().__init__()
        self.start_time()
        self.data = b''
        self.finished = False

    def on_data(self, proc, data):
        self.emit('data', data, proc)
        self.data += data

        fn = getattr(self, 'handle_data', None)

        if fn is not None and callable(fn):
            fn(data, proc)

    def on_finished(self, proc):
        self.emit('finish', self.data, proc)
        self.stop_time()
        self.finished = True

        fn = getattr(self, 'handle_finish', None)

        if fn is not None and callable(fn):
            fn(proc)


class Settings(object):
    """ A wrapper for a sublime.Settings object """

    loaded_settings = None

    def __init__(self, path, load=True):
        self.path = path

        if load:
            self.load()

    def load(self):
        self.loaded_settings = sublime.load_settings(self.path)
        self.loaded_settings.clear_on_change(self.path)
        self.loaded_settings.add_on_change(self.path, self.load)

    def save(self):
        sublime.save_settings(self.path)

    def set(self, key, value):
        """ Set a value into the sublime.Settings object """
        self.load_setting.set(key, value)

    def get(self, key, default=None):
        """ Get a value by key from the settings. Loads from default settings if key doesn't the exist. """
        return self.loaded_settings.get(key, default)
