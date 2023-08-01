import logging
import time
from enum import Enum

import serial


class SerialDriver:
    def __init__(self, port: str):
        self.serial = serial.Serial(
            port=port,
            baudrate=19200,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            xonxoff=True,  # Software-Handshake
            rtscts=False,
            dsrdtr=False,
        )
        time.sleep(1)

    def send_command(self, command: str) -> str:
        self.serial.write((command + "\r\n").encode())
        self.serial.flush()
        response = self.serial.readline().decode().strip()
        return response

    def close(self):
        self.serial.close()


class Variable(str, Enum):
    """
    Variables for the dosing unit.
    """

    VOLUME = "Volume"  # Dosed volume
    TITER = "Titer"  # Titer of selected solution
    CONC = "Concentration"  # Concentration of selected solution
    RATE = "Rate"  # Dosing rate (XDOS only)
    TIME = "Time"  # Dosing time (XDOS only)

    def __str__(self) -> str:
        return self.name


class Command:
    @staticmethod
    def start_or_continue() -> str:
        return "$G"

    @staticmethod
    def stop() -> str:
        return "$S"

    @staticmethod
    def hold() -> str:
        return "$H"

    @staticmethod
    def status() -> str:
        return "$D"

    @staticmethod
    def load_method(name: str) -> str:
        return f"$L({name})"

    @staticmethod
    def get_variable_value(name: Variable) -> str:
        """
        Requests the value of the given variable.

        The values of the variables are only available after the end of a determination (in the status 'ready').
        """
        return f"$Q({name})"


class Status(str, Enum):
    READY = "Ready;0"
    BUSY = "Busy;0"
    HOLD = "Hold;0"

    @staticmethod
    def from_string(status: str) -> "Status":
        for item in Status:
            if item.value == status:
                return item
        raise ValueError(f"Status {status} not found")


class Response(str, Enum):
    OK = "OK"
    E1 = "Method not found"
    E2 = "Invalid variable"
    E3 = "Invalid command"

    @staticmethod
    def from_string(response: str) -> "Response":
        for item in Response:
            if item.name == response:
                return item
        raise ValueError(f"Response {response} not found")

    def __str__(self) -> str:
        return self.value


class Dosimat876:
    def __init__(self, port: str):
        self._serial = SerialDriver(port)
        self._logger = logging.getLogger(__class__)

    def dispense(self, ml: float) -> Response:
        # Create the method and load it into the dosing unit
        load_command = Command.load_method(name=f"{ml}ml-XDOS")
        response = self._serial.send_command(load_command)
        response = Response.from_string(response)
        self._logger.info(f"Response from {load_command}: {response}")

        # Dispense the amount
        self._serial.send_command(Command.start_or_continue())

        # Wait till the status is ready
        while True:
            status = self._serial.send_command(Command.status())
            status = Status.from_string(status)
            self._logger.info(f"Status: {status}")
            if status == Status.READY:
                break
            time.sleep(1)

    def close(self):
        self._serial.close()