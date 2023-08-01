from dosimat_driver.driver import Dosimat876

serial_port = "/dev/ttyUSB0"

dosimat = Dosimat876(serial_port)

dosimat.dispense(1.0)
