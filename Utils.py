import sublime_plugin
import sublime
import string
import random


class Init(object):
    """ A class that inits itself with whatever properties are give """

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)


# https://stackoverflow.com/questions/2955412/python-destructuring-bind-dictionary-contents
pluck = lambda dict, *args: (dict.get(arg) for arg in args)

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

