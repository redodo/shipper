# -*- coding: utf-8 -*-
import getpass
import hashlib
import sys

import click
import simplecrypt

from .exceptions import ShipmentError
from .helpers import prompt_password
from .pickers import RandomPicker
from .shipments import LosslessImageShipment, WaveShipment


#: The default seed used for the RandomPicker
DEFAULT_SEED = 7


CARGO_TYPES = {
    'jpg': LosslessImageShipment,
    'bmp': LosslessImageShipment,
    'png': LosslessImageShipment,
    'wav': WaveShipment,
}


def get_shipment_method(container):
    for cargo_type, shipment in CARGO_TYPES.items():
        if container.lower().endswith('.{}'.format(cargo_type)):
            return shipment


@click.group()
def cli():
    """Ship cargo in different types of containers.

    All image types are supported as a container input.  The output,
    however, will always be PNG when an image is used as input.

    WAVE audio files can also be used as a container.
    """


@cli.command()
@click.argument('container', type=click.Path(exists=True))
@click.option('--cargo', '-c', type=click.File('rb'), default=sys.stdin.buffer,
              help='the cargo to load into the container (stdin by default)')
@click.option('--destination', '-d', type=click.File(),
              default=sys.stdout.buffer,
              help='ship the container somewhere (stdout by default)')
@click.option('--lock', '-l', is_flag=True, default=False,
              help='put a lock on the cargo to secure it')
def load(container, cargo, destination, lock):
    """Load a container with cargo."""
    shipment_method = get_shipment_method(container)
    seed = DEFAULT_SEED
    cargo = cargo.read()

    if lock:
        password = prompt_password(confirm=True)
        seed = hashlib.sha512(password.encode('utf-8')).hexdigest()
        cargo = simplecrypt.encrypt(password, cargo)
        del password

    shipment = shipment_method(container)
    try:
        shipment.load(cargo, picker=RandomPicker(seed))
    except ShipmentError as e:
        raise click.ClickException(e)

    shipment.ship(destination)


@cli.command()
@click.argument('container', type=click.Path(exists=True))
@click.option('--destination', '-d', type=click.File(),
              default=sys.stdout.buffer,
              help='where to put the cargo (stdout by default)')
@click.option('--unlock', '-l', is_flag=True, default=False,
              help='unlock secured cargo')
def unload(container, destination, unlock):
    """Unload cargo from a container."""
    shipment_method = get_shipment_method(container)
    seed = DEFAULT_SEED

    if unlock:
        password = prompt_password()
        seed = hashlib.sha512(password.encode('utf-8')).hexdigest()

    shipment = shipment_method(container)
    try:
        cargo = shipment.unload(picker=RandomPicker(seed))
    except ShipmentError as e:
        raise click.ClickException(e)

    if unlock:
        cargo = simplecrypt.decrypt(password, cargo)
        del password

    destination.write(cargo)
