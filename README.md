![Shipper](./example.png)

# Shipper

*Ship cargo in containers.*

Installation:

```bash
pip install -e git+https://github.com/redodo/shipper.git
```

Example usage:

```bash
$ echo "Hello World" | shipper load example.png shipment.png
$ shipper unload shipment.png
Hello World
```

## Securing The Cargo

The cargo that is loaded in the container can be secured using the `--lock`
parameter in the CLI. You will be prompted a password.

    shipper load --cargo data.txt example.png shipment.png --lock

Unloading secured cargo can be done by passing the `--unlock` parameter:

    shipper unload shipment.png --unlock

## The Shipment Process

The process of preparing a shipment is defined as follows:

1. The cargo is palletized to allow for easy placement in the container
2. The shipping bill is generated and also palletized (don't ask why)
3. The pallets are loaded into the available pallet spots of the container
4. The container is optionally shipped to its destination

Unloading the shipment is the reverse of that process:

1. Search for the palletized shipping bill (this is actually pretty tedious)
2. Unload the pallets from the container
3. Put the cargo back together

While the standard implementation of this package only delivers support for two
types of contains; lossless image containers and WAVE audio file containers, it
is jolly straight forward to create implementations for other types of
containers.
