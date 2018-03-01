"""
Retrieves the information about system node, system npm and nvm (untested on windows)
"""

import os
import random
import string

import sublime
import sublime_plugin

from .Exec import exec_cmd
from .Settings import Settings

OSX_SOURCE_NVM = 'source %s' % (os.path.expanduser('~/.nvm/nvm.sh'))
OSX_SOURCE_NVM_AND = OSX_SOURCE_NVM + ' && '

IS_WINDOWS = sublime.platform() == 'windows'

# On osx (and probably linux) we need to source ~/.nvm/nvm.sh. On windows, I think it's
# already on the PATH
def prefix(command):
    if IS_WINDOWS:
        return command

    return OSX_SOURCE_NVM_AND + command

NVM_RUN = prefix('nvm run')

FIND_NODE = 'where node' if IS_WINDOWS else 'which node'
FIND_NODE_VERSION = 'node --version'
FIND_NPM = 'where npm' if IS_WINDOWS else 'which node'
FIND_NPM_VERSION = 'npm --version'
FIND_NVM_DEFAULT = prefix('nvm which default')
FIND_NVM_CURRENT = prefix('nvm which current')
# FIND_NVM_DEFAULT_VERSION = prefix('nvm version default')


def has_nvm_dir():
    return os.path.isdir(os.path.expanduser('~/.nvm'))


class NodeEnv(object):
    NVM_CURRENT = 1
    NVM_DEFAULT = 2
    SYSTEM = 4

    def __init__(self,
        system_node_path=None,
        system_node_version=None,
        system_npm_path=None,
        system_npm_version=None,
        nvm_default_path=None,
        nvm_default_npm_path=None,
        node_path=None,
        npm_path=None,
    ):
        self.system_node_path = system_node_path
        self.system_node_version = system_node_version
        self.system_npm_path = system_npm_path
        self.system_npm_version = system_npm_version
        self.nvm_default_path = nvm_default_path
        self.nvm_default_npm_path = nvm_default_npm_path
        self.node_path = node_path
        self.npm_path = npm_path

    def to_json(self):
        return {
            'system_node_path': self.system_node_path,
            'system_node_version': self.system_node_version,
            'system_npm_path': self.system_npm_path,
            'system_npm_version': self.system_npm_version,
            'nvm_default_path': self.nvm_default_path,
            'nvm_default_npm_path': self.nvm_default_npm_path,
            'node_path': self.node_path,
            'npm_path': self.npm_path,
        }

    def get_preferred(self, settings=[]):
        """
        Get's the user's preferred node path. First attempts to retrieve a node_path from
        and of the settings passed in the `settings` list. If a node_path is not
        found and the node_env has not yet been loaded, None is returned. If "prefer" is
        set in the SublimeTools settings, then the process is as follows:

        1. Set variable preferred to the user setting "prefer"
        2. If prefer is string "system", return node_env.system_node_path
        3. If prefer is string "nvm_default", return node_env.nvm_default_path
        4. Return None

        Args:
            default (str, optional):
            settings (list): A list of settings objects to look for a node path
        """

        node_path = get_settings_node_path(settings=settings + [user_settings])

        # If there's a path specified in the SublimeTools settings, use it first
        if isinstance(node_path, str):
            return node_path

        preferred = user_settings.get('prefer')

        if preferred == 'system':
            return self.system_node_path
        elif preferred == 'nvm_default':
            return self.nvm_default_path


# def get_nvm_current_from_dir(dirname, on_done=None):
#     """
#     FIXME: For some reason it always go to the default alias...
#     Asynchronously finds what version of nvm is being used at a directory

#     Args:
#         dirname (str): The dirname to find the
#         on_done (callable): The callback for when it's found
#     """
#     # Todo set a timeout so that on_done is always async
#     if not isinstance(dirname, str):
#         raise Exception('dirname should be a string')
#     elif not callable(on_done):
#         raise Exception('on_done should be callable')

#     if not os.path.isdir(dirname):
#         return on_done(None)

#     if not has_nvm_dir():
#         return on_done(None)

#     def on_finish(proc, data):
#         nvm_current = parse_cmd_result(data)[0]

#         if os.path.exists(nvm_current):
#             on_done(nvm_current)
#         else:
#             on_done(None)

#     shell_cmd = create_shell_cmd([
#         FIND_NVM_CURRENT,
#     ])

#     print(shell_cmd, dirname)

#     exec_cmd(shell_cmd, working_dir=dirname, shell=True, on_finish=on_finish)


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

    # Either the system path or nvm default, with preferrance to nvm
    node_path = None
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


def get_node_env(on_done=None):
    args = [
        FIND_NODE,
        FIND_NODE_VERSION,
        FIND_NPM,
        FIND_NPM_VERSION,
        FIND_NVM_DEFAULT,
        # FIND_NVM_DEFAULT_VERSION,
        # FIND_NVM_DEFAULT_NPM,
        # FIND_NVM_DEFAULT_NPM_VERSION,
    ]

    shell_cmd = create_shell_cmd(args)

    def on_finish(proc, data):
        info = normalize_node_result(*parse_cmd_result(data))
        env = NodeEnv(**info)
        on_done(env)

    exec_cmd(shell_cmd, on_finish=on_finish, shell=True)


def assert_node_path(settings=[]):
    """
    Args:
        settings (list, optional): A list of setting objects to check for a node_path key
    """

    node_path = None

    for setting in settings:
        node_path = get_settings_node_path(settings=[setting])

        if node_path:
            break

    if node_path is None and node_env is not None:
        # Use system installed or nvm default
        node_path = node_env.node_path

    if node_path is None:
        message = 'Could not find any path to node via system installed or nvm'
        sublime.error_message(message)
        raise Exception(message)
    elif not os.path.exists(str(node_path)):
        message = 'The node_path setting is invalid, "{}"'.format(node_path)
        sublime.error_message(message)
        raise Exception(message)

    return node_path


class ReloadNodeEnv(sublime_plugin.WindowCommand):

    def run(self):
        reset_node_env()


def reset_node_env():
    import datetime

    start = datetime.datetime.now()

    def set_node_env(env):
        global node_env

        delta = datetime.datetime.now() - start
        message = 'Node env loaded in {}ms'.format(int(delta.total_seconds() * 1000))

        print(message)

        node_env = env

        # For debug purposes, log the versions
        for key, value in sorted(node_env.to_json().items()):
            print("{:<20} {}".format(key, value))

    get_node_env(on_done=set_node_env)


node_env = None


def plugin_loaded():
    global user_settings

    user_settings = Settings('SublimeTools.sublime-settings')
    reset_node_env()
