import logging

from dosimat_driver.driver import Dosimat876

logging.basicConfig(level=logging.INFO)

serial_port = "/dev/ttyUSB0"

dosimat = Dosimat876(serial_port)

dosimat.dispense(10)
