import sublime

class Settings(object):
    """
    A wrapper for a sublime.Settings object. This class will automatically reload
    the underlying settings object, creating a sort of live binding to what is
    actually defined in the settings in that moment in time.

    Example:
    user_settings = Settings('PackageName.sublime-settings')
    user.settings.get('node_path')
    """

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
        self.loaded_settings.set(key, value)

    def get(self, key, default=None):
        """ Get a value by key from the settings. Loads from default settings if key doesn't the exist. """
        return self.loaded_settings.get(key, default)

    # def get_path(self, path, default=None):
    #     """
    #     Returns the object at the neste property
    #     TODO:
    #     """
    #     pass

    def has(self, key):
        return self.loaded_settings.has(key)


def get_platform_setting(key, settings=[]):
    """
    Returns the node_path from a settings object, or None if it doesn't
    exist.

    Args:
        settings (list): A list of settings to retrieve the node_path from
    """

    for setting in settings:
        paths = setting.get(key)

        if not isinstance(paths, dict):
            continue

        node_path = paths[sublime.platform()] if sublime.platform() in paths else None

        if node_path is not None:
            return node_path
