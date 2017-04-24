# -*- coding: utf-8 -*-
import random

from .helpers import RandomSeed


class BasePicker(object):
    def iterate(self, spots, pallets):
        raise NotImplementedError('iterate function is not implemented by '
                                  'this picker')


class LinearPicker(BasePicker):
    def iterate(self, spots, pallets):
        return enumerate(pallets)


class RandomPicker(BasePicker):
    def __init__(self, seed):
        self.__seed = seed

    def iterate(self, spots, pallets):
        with RandomSeed(self.__seed):
            return zip(
                random.sample(range(len(spots)), len(spots)),
                pallets,
            )
