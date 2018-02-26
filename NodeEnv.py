"""
Retrieves the information about system node, system npm and nvm (untested on windows)
"""

import os
import random
import string

import sublime
import sublime_plugin

from .Utils import exec_cmd


UNAVAILABLE = 'N/A{}'.format(''.join(random.choice(string.digits) for _ in range(30)))
ECHO_UNAVAILABLE = 'echo "%s"' % UNAVAILABLE
OSX_SOURCE_NVM = 'source %s' % (os.path.expanduser('~/.nvm/nvm.sh'))
WINDOWS_SOURCE_NVM = None # TODO: get nvm details from nvm-windows


node_env = None


def has_nvm():
    return os.path.isdir(os.path.expanduser('~/.nvm'))


class NodeEnv(object):
    NVM_CURRENT = 1
    NVM_DEFAULT = 2
    SYSTEM = 4

    def __init__(self, info):
        self.info = info

        # TODO: declare properties one by one, it's easier this way for now though
        for key, value in info.items():
            setattr(self, key, value)

    def get_node_path(self, dirname, on_done=None):
        # Todo set a timeout so that on_done is always async
        if not isinstance(dirname, str):
            raise Exception('dirname should be a string')
        elif not callable(on_done):
            raise Exception('on_done should be callable')

        if not os.path.isdir(dirname):
            return on_done(None)

        if not has_nvm():
            return on_done(None)

        def on_finish(data, proc):
            nvm_current = parse_cmd_result(data)[0]

            if nvm_current != UNAVAILABLE:
                on_done(nvm_current)
            else:
                return on_done(self.system_node_path)

        shell_cmd = create_shell_cmd([
            '%s && nvm which current' % (OSX_SOURCE_NVM,) if has_nvm() else ECHO_UNAVAILABLE,
        ])

        exec_cmd(shell_cmd, working_dir=dirname, shell=True, on_finish=on_finish)


def create_shell_cmd(args):
    return ';'.join(["{0}".format(arg) for arg in args]) + ';'
    # return ';'.join(["({0}) || {1}".format(arg, ECHO_UNAVAILABLE) for arg in args]) + ';'


def normalize_node_result(
        system_node_path,
        system_node_version,
        system_npm_path,
        system_npm_version,
        nvm_default_path,
    ):

    nvm_default_npm_path = None
    path = nvm_default_path

    if os.path.exists(nvm_default_path):
        nvm_default_npm_path = os.path.normpath(os.path.join(nvm_default_path, '../npm'))
    else:
        nvm_default_path = None
        path = system_node_path

    if not os.path.exists(system_node_path):
        system_node_path = None
        # NPM should never be installed apart from node, so just set it to None
        system_npm_path = None
        system_node_version = None
        path = None

    info = dict(
        system_node_path=system_node_path,
        system_node_version=system_node_version,
        system_npm_path=system_npm_path,
        system_npm_version=system_npm_version,
        nvm_default_path=nvm_default_path,
        nvm_default_npm_path=nvm_default_npm_path,
        path=path,
    )

    return info


def get_view_node_path(view):
    """
    view (sublime.View): The view to get the pathname of

    Returns the node_path from a buffer's settings, or None if it doesn't
    exist. It does not check for what nvm is currently being used in the
    directory the file lives in. For that, use get_node_path.
    """

    if view.file_name():
        path = view.settings().get('node_path')

        if isinstance(path, str):
            return path

    return None


def get_node_env(on_done=None):
    args = [
        'which node',
        'node --version',
        'which npm',
        'npm --version',
        '%s && nvm which default' % (OSX_SOURCE_NVM,) if has_nvm() else ECHO_UNAVAILABLE,
    ]

    shell_cmd = create_shell_cmd(args)

    def on_finish(data, proc):
        info = normalize_node_result(*parse_cmd_result(data))
        env = NodeEnv(info)
        on_done(env)

    exec_cmd(shell_cmd, on_finish=on_finish, shell=True)

    # print('args:', args)
    # print('shell_cmd:', shell_cmd)


def parse_cmd_result(data):
    # Might be carriage return on windows
    return [s for s in str(data, 'utf8').split('\n') if s != '']

def plugin_loaded():

    def set_node_env(env):
        global node_env

        node_env = env

    get_node_env(on_done=set_node_env)
