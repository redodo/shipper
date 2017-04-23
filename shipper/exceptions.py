# -*- coding: utf-8 -*-


class CarrierError(Exception):
    pass


class LoadingError(CarrierError):
    pass


class UnloadingError(CarrierError):
    pass
