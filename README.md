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
