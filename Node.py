"""
Retrieves the information about system node, system npm and nvm (untested on windows)
"""

import os
import random
import string

import sublime
import sublime_plugin

from .Exec import exec_cmd

OSX_SOURCE_NVM = 'source %s' % (os.path.expanduser('~/.nvm/nvm.sh'))
OSX_SOURCE_NVM_AND = OSX_SOURCE_NVM + ' && '

IS_WINDOWS = sublime.platform() == 'windows'

NVM_RUN = '{} nvm run'.format(OSX_SOURCE_NVM_AND if not IS_WINDOWS else '')

FIND_NODE = 'where node' if IS_WINDOWS else 'which node'
FIND_NODE_VERSION = 'node --version'
FIND_NPM = 'where npm' if IS_WINDOWS else 'which node'
FIND_NPM_VERSION = 'npm --version'
# On osx (and probably linux) we need to source ~/.nvm/nvm.sh. On windows, I think it's
# already on the PATH
FIND_NVM_DEFAULT = '{} nvm which default'.format(OSX_SOURCE_NVM_AND if not IS_WINDOWS else '')
FIND_NVM_CURRENT = '{} nvm which current'.format(OSX_SOURCE_NVM_AND if not IS_WINDOWS else '')


node_env = None


def has_nvm_dir():
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


def get_nvm_current_from_dir(dirname, on_done=None):
    """
    FIXME: For some reason it always go to the default alias...
    Asynchronously finds what version of nvm is being used at a directory

    Args:
        dirname (str): The dirname to find the
        on_done (callable): The callback for when it's found
    """
    # Todo set a timeout so that on_done is always async
    if not isinstance(dirname, str):
        raise Exception('dirname should be a string')
    elif not callable(on_done):
        raise Exception('on_done should be callable')

    if not os.path.isdir(dirname):
        return on_done(None)

    if not has_nvm_dir():
        return on_done(None)

    def on_finish(proc, data):
        nvm_current = parse_cmd_result(data)[0]

        if os.path.exists(nvm_current):
            on_done(nvm_current)
        else:
            on_done(None)

    shell_cmd = create_shell_cmd([
        FIND_NVM_CURRENT,
    ])

    print(shell_cmd, dirname)

    exec_cmd(shell_cmd, working_dir=dirname, shell=True, on_finish=on_finish)


def create_shell_cmd(args):
    return ';'.join(["{0}".format(arg) for arg in args]) + ';'


def parse_cmd_result(data):
    return [s for s in str(data, 'utf8').replace('\r\n', '\n').split('\n') if s != '']


def normalize_node_result(
        system_node_path,
        system_node_version,
        system_npm_path,
        system_npm_version,
        nvm_default_path,
    ):

    # The path to the version of node the user probably prefers to use
    node_path = None
    # The path to the version of npm the user probably prefers to use
    npm_path = None

    # npm should always come bundle with the node version, so it's pretty
    # straightforward to get the npm path from it
    if os.path.exists(nvm_default_path):
        nvm_default_npm_path = os.path.normpath(os.path.join(nvm_default_path, '../npm'))
    else:
        nvm_default_npm_path = None
        nvm_default_path = None

    if os.path.exists(system_node_path):
        system_npm_path = os.path.normpath(os.path.join(system_node_path, '../npm'))
    else:
        system_node_path = None
        # NPM should never be installed apart from node, so just set it to None
        system_npm_path = None
        system_node_version = None
        system_npm_version = None

    # Always try to use the nvm default alias first
    if nvm_default_path is not None:
        node_path = nvm_default_path
        npm_path = nvm_default_npm_path
    # Try to use the system installed version
    elif system_node_path is not None:
        node_path = system_node_path
        npm_path = system_npm_path
    else:
        # We couldn't find a path to node or npm (sadface)
        pass

    info = dict(
        system_node_path=system_node_path,
        system_node_version=system_node_version,
        system_npm_path=system_npm_path,
        system_npm_version=system_npm_version,
        nvm_default_path=nvm_default_path,
        nvm_default_npm_path=nvm_default_npm_path,
        node_path=node_path,
        npm_path=npm_path
    )

    return info


def get_settings_node_path(settings):
    """
    settings (sublime.Settings): The settings to retrieve the node_path from

    Returns the node_path from a settings object, or None if it doesn't
    exist. It does not check for what nvm is currently being used in the
    directory the file lives in, or if the path is actually a node binary.
    For that, use node_env.get_node_path.

    Assumes the node_path setting is defined as below:
    "node_path":
    {
      "windows": "C:/Program Files/nodejs/node.exe",
      "linux": "/usr/bin/nodejs",
      "osx": "/usr/local/bin/node"
    }
    """

    paths = settings.get('node_path', {})

    return paths[sublime.platform()] if sublime.platform() in paths else None


def get_node_env(on_done=None):
    args = [
        FIND_NODE,
        FIND_NODE_VERSION,
        FIND_NPM,
        FIND_NPM_VERSION,
        FIND_NVM_DEFAULT,
    ]

    shell_cmd = create_shell_cmd(args)

    def on_finish(proc, data):
        info = normalize_node_result(*parse_cmd_result(data))
        env = NodeEnv(info)
        on_done(env)

    exec_cmd(shell_cmd, on_finish=on_finish, shell=True)

    # print('args:', args)
    # print('shell_cmd:', shell_cmd)


def assert_node_path(settings=None):
    node_path = None

    if settings is not None:
        # If there is a global or project defined node_path, use it instead
        node_path = get_settings_node_path(settings)

    if node_path is None and node_env is not None:
        # Else use whatever node version we can find
        node_path = node_env.node_path
    else:
        return

    if node_path is None:
        message = 'Could not find any path to node via system installed or nvm'
        sublime.error_message(message)
        raise Exception(message)
    elif not os.path.exists(str(node_path)):
        message = 'The node_path setting is invalid, "{}"'.format(node_path)
        sublime.error_message(message)
        raise Exception(message)

    return node_path


def plugin_loaded():

    def set_node_env(env):
        global node_env

        node_env = env

        # For debug purposes, log the versions
        for key, value in sorted(node_env.info.items()):
            print("{:<20} {}".format(key, value))

    get_node_env(on_done=set_node_env)
