# -*- coding: utf-8 -*-
import math
import wave

from bitarray import bitarray
from PIL import Image

from .exceptions import LoadingError, UnloadingError
from .pickers import LinearPicker


class BaseShipment(object):
    """The base for all types of shipments.

    :param container: the container used to store the cargo
    """

    #: The ratio of pallets to bytes
    PALLETS_PER_BYTE = None

    #: The default picker used in loading and unloading the cargo
    DEFAULT_PICKER = LinearPicker

    #: The types of containers this shipments supports
    CONTAINER_TYPES = ()

    def __init__(self, container):
        self.container = container

    def load(self, cargo, picker=None):
        if picker is None:
            picker = self.DEFAULT_PICKER()

        spots = self._get_pallet_spots()
        pallets = self._palletize_cargo(cargo)
        shipping_bill = self._create_shipping_bill(pallets)

        # for some reason we also palletize our shipping bills
        pallets = self._palletize_cargo(shipping_bill) + pallets

        if len(pallets) > len(spots):
            raise LoadingError('There are too much pallets and not enough '
                               'spots.')

        # load the pallets onto the spots
        for location, pallet in picker.iterate(spots, pallets):
            self._load_pallet(spots, location, pallet)

        # update the spots
        self._set_pallet_spots(spots)

    def unload(self, picker=None):
        if picker is None:
            picker = self.DEFAULT_PICKER()

        spots = self._get_pallet_spots()
        locations = [location for location, _ in picker.iterate(spots, spots)]

        size = self._parse_shipping_bill(spots, locations)
        if size > len(spots):
            raise UnloadingError('It appears that there is no cargo in '
                                 'this container as the supposed number '
                                 'of pallets exceed the number of '
                                 'available spots.')

        pallets = []
        while len(pallets) < size:
            location = locations.pop(0)
            pallet = self._unload_pallet(spots, location)
            pallets.append(pallet)

        cargo = self._depalletize_cargo(pallets)
        return cargo

    def ship(self, destination):
        """Ship the cargo somewhere.

        :param destination: the cargo is shipped here
        """
        raise NotImplementedError('ship function is not implemented in this '
                                  'shipment')

    def _create_shipping_bill(self, pallets):
        """Creates a bill to be sent with the shipment of the cargo.

        :param pallets: the pallets that are being shipped
        """
        size = len(pallets)
        shipping_bill = bytearray()
        for i in range(6):
            shipping_bill.insert(0, size & 0xFF)
            size >>= 8
        return bytes(shipping_bill)

    def _parse_shipping_bill(self, spots, locations):
        """Parses the size from the shipping bill in a palletized
        shipment.

        :param spots: the spots where pallets can stand
        :param locations: the locations
        """
        if self.PALLETS_PER_BYTE < 1:
            raise UnloadingError('multibyte pallets are not supported')
        elif math.log(self.PALLETS_PER_BYTE) / math.log(2) % 1:
            raise UnloadingError('PALLETS_PER_BYTE must be a power of 2')

        size = 0
        for i in range(6):
            selection = locations[:self.PALLETS_PER_BYTE]
            del locations[:self.PALLETS_PER_BYTE]

            byte = bytearray(self._depalletize_cargo([
                self._unload_pallet(spots, location) for location in selection
            ])).pop()

            size <<= 8
            size += byte

        return size

    def _get_pallet_spots(self):
        """Gets the pallet spots from the container.

        :return: this function should return a `bytearray`
        """
        raise NotImplementedError('_get_pallet_spots function is not '
                                  'implemented in this shipment')

    def _set_pallet_spots(self, spots):
        """Sets the pallet spots in the container"""
        raise NotImplementedError('_set_pallet_spots function is not '
                                  'implemented in this shipment')

    def _palletize_cargo(self, cargo):
        """Puts the cargo on pallets to make them shipment-ready.

        :param cargo: the cargo to be put on pallets
        :return: one or more pallets with the cargo
        """
        raise NotImplementedError('_palletize_cargo function is not '
                                  'implemented in this shipment')

    def _depalletize_cargo(self, palletized_cargo):
        """Gets the cargo from pallets.

        :param palletized_cargo: the palletized cargo
        :return: the cargo, depalletized
        """
        raise NotImplementedError('_depalletize_cargo function is not '
                                  'implemented in this shipment')

    def _load_pallet(self, spots, location, pallet):
        """Loads a pallet on a spot.

        :param spots: the spots where pallets can be put
        :param location: the location of the spot to put the pallet
        :param pallet: the pallet to load
        """
        raise NotImplementedError('_load_pallet function is not implemented '
                                  'in this shipment')

    def _unload_pallet(self, spots, location):
        """Unloads a pallet from a spot.

        :param spots: the spots where pallets are put
        :param location: the location of the spot to get the pallet from
        :return: a pallet
        """
        raise NotImplementedError('_unload_pallet function is not implemented '
                                  'in this shipment')


class BinaryShipment(BaseShipment):
    """Base class for binary shipments"""

    PALLETS_PER_BYTE = 8

    def _palletize_cargo(self, cargo):
        palletized_cargo = bitarray()
        palletized_cargo.frombytes(cargo)
        return palletized_cargo

    def _depalletize_cargo(self, palletized_cargo):
        cargo = bitarray(palletized_cargo)
        return cargo.tobytes()

    def _load_pallet(self, spots, location, pallet):
        spots[location] = spots[location] & 0xFFFFFE | pallet

    def _unload_pallet(self, spots, location):
        return spots[location] & 1


class LosslessImageShipment(BinaryShipment):
    """This shipment uses a lossless image as a container"""

    CONTAINER_TYPES = (
        'bmp', 'gif', 'jpe', 'jpeg', 'jpg', 'png',
    )

    def __init__(self, container):
        self.container = Image.open(container)

    def ship(self, destination):
        self.container.save(destination, 'PNG')

    def _get_pallet_spots(self):
        return bytearray(self.container.tobytes())

    def _set_pallet_spots(self, spots):
        self.container = Image.frombytes('RGB', self.container.size,
                                         bytes(spots))


class WaveShipment(BinaryShipment):
    """This shipment uses a WAVE audio file as a container"""

    CONTAINER_TYPES = (
        'wav',
    )

    def __init__(self, container):
        self.container = container
        with wave.open(container, 'rb') as f:
            self._params = f.getparams()
            self._nframes = f.getnframes()
            self._rawframes = f.readframes(self._nframes)

    def ship(self, destination):
        with wave.open(destination, 'wb') as f:
            f.setparams(self._params)
            f.writeframesraw(self._rawframes)

    def _get_pallet_spots(self):
        return bytearray(self._rawframes)

    def _set_pallet_spots(self, spots):
        self._rawframes = bytes(spots)
