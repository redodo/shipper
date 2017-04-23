# -*- coding: utf-8 -*-
import click
import getpass
import hashlib
import simplecrypt
import sys
from .pickers import RandomPicker
from .shipments import LosslessImageShipment


#: The default seed used for the RandomPicker
DEFAULT_SEED = 7


@click.group()
def cli():
    pass


def validate_pass(ctx, param, value):
    print(ctx, param, value)
    return value


@cli.command()
@click.argument('container', type=click.Path(exists=True))
@click.argument('destination', type=click.Path())
@click.option('--cargo', '-c', type=click.File('rb'), default=sys.stdin.buffer)
@click.option('--lock', '-l', is_flag=True, default=False)
def load(container, destination, cargo, lock):
    seed = DEFAULT_SEED
    cargo = cargo.read()

    if lock:
        while True:
            password = getpass.getpass('Password: ')
            if getpass.getpass('Repeat for confirmation: ') == password:
                break
            print('Confirmation did not match the password')
        seed = hashlib.sha512(password.encode('utf-8')).hexdigest()
        cargo = simplecrypt.encrypt(password, cargo)
        del password

    shipment = LosslessImageShipment(container)
    shipment.load(cargo, picker=RandomPicker(seed))
    shipment.ship(destination)


@cli.command()
@click.argument('container', type=click.Path(exists=True))
@click.option('--destination', '-d', type=click.File(),
              default=sys.stdout.buffer)
@click.option('--unlock', '-l', is_flag=True, default=False)
def unload(container, destination, unlock):
    seed = DEFAULT_SEED

    if unlock:
        password = getpass.getpass('Password: ')
        seed = hashlib.sha512(password.encode('utf-8')).hexdigest()

    shipment = LosslessImageShipment(container)
    cargo = shipment.unload(picker=RandomPicker(seed))

    if unlock:
        cargo = simplecrypt.decrypt(password, cargo)
        del password

    destination.write(cargo)


@cli.command()
@click.option('--test', default=False, type=str)
def test(test):
    print(test)


if __name__ == '__main__':
    cli()
