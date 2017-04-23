# -*- coding: utf-8 -*-
import click
import getpass
import hashlib
import simplecrypt
import sys
from .helpers import prompt_password
from .pickers import RandomPicker
from .shipments import LosslessImageShipment, WaveShipment


#: The default seed used for the RandomPicker
DEFAULT_SEED = 7


CARGO_TYPES = {
    'png': LosslessImageShipment,
    'wav': WaveShipment,
}


def get_shipment_method(container):
    for cargo_type, shipment in CARGO_TYPES.items():
        if container.lower().endswith('.{}'.format(cargo_type)):
            return shipment


@click.group()
def cli():
    pass


@cli.command()
@click.argument('container', type=click.Path(exists=True))
@click.argument('destination', type=click.Path())
@click.option('--cargo', '-c', type=click.File('rb'), default=sys.stdin.buffer)
@click.option('--lock', '-l', is_flag=True, default=False)
def load(container, destination, cargo, lock):
    shipment_method = get_shipment_method(container)
    seed = DEFAULT_SEED
    cargo = cargo.read()

    if lock:
        password = prompt_password(confirm=True)
        seed = hashlib.sha512(password.encode('utf-8')).hexdigest()
        cargo = simplecrypt.encrypt(password, cargo)
        del password

    shipment = shipment_method(container)
    shipment.load(cargo, picker=RandomPicker(seed))
    shipment.ship(destination)


@cli.command()
@click.argument('container', type=click.Path(exists=True))
@click.option('--destination', '-d', type=click.File(),
              default=sys.stdout.buffer)
@click.option('--unlock', '-l', is_flag=True, default=False)
def unload(container, destination, unlock):
    shipment_method = get_shipment_method(container)
    seed = DEFAULT_SEED

    if unlock:
        password = prompt_password()
        seed = hashlib.sha512(password.encode('utf-8')).hexdigest()

    shipment = shipment_method(container)
    cargo = shipment.unload(picker=RandomPicker(seed))

    if unlock:
        cargo = simplecrypt.decrypt(password, cargo)
        del password

    destination.write(cargo)


if __name__ == '__main__':
    cli()
