# -*- coding: utf-8 -*-
from .exceptions import ShipmentError
from .shipments import LosslessImageShipment, WaveShipment


SHIPMENT_METHODS = (
    LosslessImageShipment,
    WaveShipment,
)


def shipment(container, t=None):
    """Automatically selects the correct shipment method based on the
    container type.

    :param container: the file pointer of the container
    :param t: optional overwrite of the container type
    """
    if t is None:
        try:
            if isinstance(container, str):
                filename = container
            else:
                filename = container.name
            t = filename.split('.').pop()
        except AttributeError:
            raise ShipmentError('Could not determine the container type. '
                                'Please pass the `t` parameter to this '
                                'function.')

    t = t.lower()
    for method in SHIPMENT_METHODS:
        if t in method.CONTAINER_TYPES:
            return method(container)

    raise ShipmentError('No shipment method available for '
                        'container type "{}"'.format(t))
