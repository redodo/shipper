# -*- coding: utf-8 -*-


class ShipmentError(Exception):
    pass


class LoadingError(ShipmentError):
    pass


class UnloadingError(ShipmentError):
    pass
