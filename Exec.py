import sublime
import os

from Default.exec import AsyncProcess

from .EventEmitter import EventEmitter

class ProcessListener(EventEmitter):
#     """
#     A listener for AsyncProcess, to be used in tangent with exec_cmd(), execjs(), and execjsfile().
#     The handlers for on

#     Example:
#         listener = ProcessListener()

#         @listener.on('data')
#         def on_data(proc, data):
#             print(data)

#         @listener.on('finish')
#         def on_finish(proc):
#             print()

#         # or listen to the events as so
#         listener.on('data', on_data)
#         listener.on('finish', on_finish)

#         exec_cmd('which node', listener=listener)

#         # or like this, but do notice that the methods are handle_data and handle_finish,
#         # not on_data or on_finish

#         clas AsyncListener(ProcessListener):
#             def handle_data(proc, data):
#                 print(data)

#             def handle_finish(proc):
#                 print(self.data)

#         listener = AsyncListener()

#         exec_cmd('which node', listener=listener)
#     """

    def __init__(self):
        EventEmitter.__init__(self)
        # super().__init__(self)
        self.data = b''
        self.finished = False

    def on_data(self, proc, data):
        self.emit('data', proc, data)
        self.data += data

        fn = getattr(self, 'handle_data', None)

        if fn is not None and callable(fn):
            fn(proc, data)

    def on_finished(self, proc):
        self.emit('finish', proc, self.data)
        self.finished = True

        fn = getattr(self, 'handle_finish', None)

        if fn is not None and callable(fn):
            fn(proc)


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
    """
    Executes a command asynchronously using sublime's own AsyncProcess class. Either
    a process listener must be passed, or one of the two on_data or on_finish callbacks.
    Failing to provide one of the above will raise an Exception.

    Args:
        command (str|list): A shell command (str) or non shell command (list)
        listener (ProcessListener, optional): A class implementing on_finish and on_data methods.
        on_finish (callable, optional): called when the process exits
        on_data (callable, optional): called when the process is emitting data
        env (dict):
        path (str):
        shell (bool): Whether or not to execute as a shell command

    Examples:
        def on_finish(data, proc):
            print(data)

            # Print the exit code for the command
            print(proc.returncode)

        exec_cmd(['node', filename], on_finish=on_finish)


        # Extending ProcessListener will remove some boiler plate code where you want to accumulate
        all of the data the listener emits.
        from SublimeTools.exec import ProcessListener

        import os

        class Listener(ProcessListener):
             def handle_data(self, proc, data):
                print(data)

            def handle_finish(self, proc):
                # Prints all the accumulated data
                print(self.data)

        # Or you can accumulate it manually

        class Listener(object):
            def __init__(self):
                self.data = b''

            def on_data(self, proc, data):
                self.data += data

            def on_finished(self, proc):
                print(self.data)

        dirname = os.path.dirname(filename)
        listener = Listener()

        exec_cmd(['node', filename], listener=listener, working_dir=dirname)
    """

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


def execjs(content, node_path=None, **kwargs):
    """
    Executes javascript with node. Node must be installed system wide or else node_path should
    be passed. The working_dir passed will be used as the base from where `require` will resolve
    modules.

    Refer to exec_cmd for more options.

    Args:
        content (str): The content to execute
        node_path (str, optional): The path to node to use, else the system installed path is used.

    Example:
        content = "require('events'); console.log('events');"
        execjs()
    """

    cmd = ['node' if node_path == None else node_path, '-e', content]

    if not isinstance(kwargs.get('working_dir')):
        raise Exception('working_dir is required')

    return exec_cmd(cmd, **kwargs)


def execjsfile(absfilename, args=[], node_path=None, **kwargs):
    """
    Executes a js file.

    Refer to exec_cmd for more options.

    Args:
        absfilename (str): An absolute path to the file you want executed.
        args (list, optional): A list of paramters that are passed to the file
        node_path (str, optional): The path to node to use, else the system installed path is used.

    Example:
        execjsfile('/users/you/memes.js', args=['--prefer-doge', 'true'])
    """

    cmd = ['node' if node_path is None else node_path, absfilename] + args

    return exec_cmd(cmd, **kwargs)
