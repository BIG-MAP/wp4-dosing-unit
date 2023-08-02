# WP4 Dosing Unit Dosimat 876 Plus

This repository contains:

- The [driver](./driver/) for the dosing unit Dosimat 876 Plus that uses the serial port for communication.
- The [HTTP server](./http/) that provides a REST API to control the dosing unit.

## Getting Started

We use the obsolete way of installing Python packages using `setup.py` to avoid issues with the missing Rust compiler for the cryptography package.

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# Install the packages
python setup.py install

# Run the manual test
python tests/manual_driver_test.py
```
