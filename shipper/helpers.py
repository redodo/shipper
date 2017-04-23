# -*- coding: utf-8 -*-
import getpass
import random


class RandomSeed(object):
    """Creates a context with a temporarily used seed for the random
    library.  The state for the random functions is not modified
    outside this context.  Example usage::

        with RandomSeed('reproducible seed'):
            values = random.sample(range(1000), 10)

    It is unclear whether the state is modified outside the current
    thread as well.  Use with caution when multithreading.

    :param seed: the seed to use in the context
    """
    def __init__(self, seed):
        self.__seed = seed

    def __enter__(self):
        self.__original_state = random.getstate()
        random.seed(self.__seed)
        # don't store the seed longer than we need to
        del self.__seed

    def __exit__(self, type, value, traceback):
        random.setstate(self.__original_state)


def prompt_password(confirm=False):
    while True:
        password = getpass.getpass('Password: ')
        if not confirm or getpass.getpass('Confirmation: ') == password:
            return password
        print('Confirmation did not match the password')
