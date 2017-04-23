# -*- coding: utf-8 -*-
import click
import sys
from .pickers import RandomPicker
from .shipments import LosslessImageShipment


@click.group()
def cli():
    pass


@cli.command()
@click.argument('container', type=click.Path(exists=True))
@click.option('--cargo', '-c', type=click.File('rb'))
@click.argument('destination', type=click.Path())
def load(container, cargo, destination):
    if cargo is not None:
        contents = cargo.read()
    else:
        contents = sys.stdin.buffer.read()
    shipment = LosslessImageShipment(container)
    shipment.load(contents, picker=RandomPicker(7))
    shipment.ship(destination)


@cli.command()
@click.argument('container', type=click.Path(exists=True))
@click.option('--destination', '-d', type=click.Path())
def unload(container, destination):
    shipment = LosslessImageShipment(container)
    cargo = shipment.unload(picker=RandomPicker(7))
    if destination is not None:
        with open(destination, 'wb') as f:
            f.write(cargo)
    else:
        sys.stdout.buffer.write(cargo)


if __name__ == '__main__':
    cli()
