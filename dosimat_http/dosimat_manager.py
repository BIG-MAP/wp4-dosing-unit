import os
from typing import Optional, Union

from dosimat_driver.driver import Dosimat876


class DosimatManager:
    """
    Manages multiple dosing units.
    """

    def __init__(self) -> None:
        self.ports = self.get_serial_ports()
        self.dosimats = self.create_dosimat_drivers(self.ports)

    @staticmethod
    def get_serial_ports() -> list[str]:
        """
        Returns a list of serial ports to use provided by the environment variables.
        """

        serial_port_1: Optional[str] = os.environ.get("SERIAL_PORT_1", "/dev/ttyUSB0")
        serial_port_2: Optional[str] = os.environ.get("SERIAL_PORT_2", "/dev/ttyUSB1")
        serial_port_3: Optional[str] = os.environ.get("SERIAL_PORT_3", "/dev/ttyUSB2")
        serial_port_4: Optional[str] = os.environ.get("SERIAL_PORT_4", "/dev/ttyUSB3")
        serial_port_5: Optional[str] = os.environ.get("SERIAL_PORT_5", "/dev/ttyUSB4")
        serial_port_6: Optional[str] = os.environ.get("SERIAL_PORT_6", "/dev/ttyUSB5")

        serial_ports = list(
            filter(
                lambda port: port is not None,
                [
                    serial_port_1,
                    serial_port_2,
                    serial_port_3,
                    serial_port_4,
                    serial_port_5,
                    serial_port_6,
                ],
            )
        )

        return serial_ports

    @staticmethod
    def create_dosimat_drivers(serial_ports: list[str]) -> list[Dosimat876]:
        """
        Creates a list of Dosimat876 drivers.
        """
        return [Dosimat876(port) for port in serial_ports]

    def close(self):
        """
        Closes all dosing units.
        """
        for dosimat in self.dosimats:
            dosimat.close()

    def get_unit(self, id: int) -> Dosimat876:
        """
        Returns the dosing unit with the given ID.
        ID starts at 1.
        """
        return self.dosimats[id - 1]

    def dispense(self, id: int, ml: Union[float, int]):
        """
        Dispenses the given volume of liquid.
        """
        self.get_unit(id).dispense(ml)
