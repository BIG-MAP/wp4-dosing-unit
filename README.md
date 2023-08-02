# WP4 Dosing Unit Dosimat 876 Plus

This repository contains:

- The [driver](./driver/) for the dosing unit Dosimat 876 Plus that uses the serial port for communication.
- The [HTTP server](./http/) that provides a REST API to control the dosing unit.

## Getting Started

We use the obsolete way of installing Python packages using `setup.py` to avoid issues with the missing Rust compiler for the cryptography package [[1](https://github.com/pyca/cryptography/issues/5771#issuecomment-775016788), [2](https://cryptography.io/en/latest/faq/#why-does-cryptography-require-rust)].

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the packages
python setup.py install

# Run the manual test
python tests/manual_driver_test.py
```

To start an HTTP server, run:

```bash
SERIAL_PORT_1=/dev/ttyUSB0 uvicorn dosimat_http.main:app --host "0.0.0.0" --port 8080
```

It's expected to have 6 dosing units connected together through LogiLink. Specify environment variables `SERIAL_PORT_1` to `SERIAL_PORT_6` to configure the serial ports, e.g., `SERIAL_PORT_1=/dev/ttyUSB0`.

To query the status of the dosing units, run:

```bash
curl "http://localhost:8080/dosimats/1/status"
```

To dispense 10 ml of liquid from the dosing unit 1, run:

```bash
curl -X POST "http://localhost:8080/dosimats/1/dispense?ml=10"
```
