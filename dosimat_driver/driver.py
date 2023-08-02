import logging
import time
from enum import Enum
from typing import Union

from dosimat_driver.serial_driver import SerialDriver


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
    """
    Helper class to create Dosimat serial commands using static functions.
    """

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
    def confirm_ok() -> str:
        return "$A(OK)"

    @staticmethod
    def confirm_cancel() -> str:
        return "$A(CANCEL)"

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
    """
    Dosimat device status.
    """

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
    """
    Response received after a serial command.
    """

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
        self._logger = logging.getLogger(__class__.__name__)
        self._locked = False  # Don't allow to run multiple commands at once on the device by locking it

    def close(self):
        self._serial.close()

    def is_ready(self) -> bool:
        """
        Returns True if the device is available.
        """
        status = self._get_status()
        return True if status == Status.READY else False

    def dispense(self, ml: Union[float, int]):
        """
        Dispense the given volume of liquid.
        The corresponding function must exist in the device.
        It must be named "{ml}ml-XDOS". Use dot as the decimal separator.
        """
        if self._locked:
            raise RuntimeError("Dosing unit is busy")

        try:
            self._locked = True
            self._load_method(ml=ml)
            self._dispense()
            self._wait_until_done()
        except Exception as e:
            self._logger.exception(e)
        finally:
            self._locked = False

    def stop(self):
        """
        Stop the current operation.
        """
        response = self._get_response_for_command(Command.stop())
        if response != Response.OK:
            raise RuntimeError(f"Could not stop: {response}")

    def _load_method(self, ml: Union[float, int]):
        """
        Load the method into the dosing unit.
        Method must be created in the device beforehand.
        """
        load_command = Command.load_method(name=f"{ml}ml-XDOS")
        response = self._get_response_for_command(load_command)
        self._logger.info(f"Response from {load_command}: {response}")
        if response != Response.OK:
            raise RuntimeError(f"Could not finish command {load_command}: {response}")

    def _dispense(self):
        response = self._get_response_for_command(Command.start_or_continue())
        if response != Response.OK:
            raise RuntimeError(f"Could not start dispensing: {response}")

    def _wait_until_done(self, timeout: int = 60):
        while True:
            status = self._get_status()
            self._logger.info(f"Status: {status}")
            if status == Status.READY:
                break
            time.sleep(1)
            timeout -= 1
            if timeout == 0:
                raise RuntimeError(f"Timeout of {timeout} seconds reached")

    def _get_status(self) -> Status:
        response = self._serial.send_command(Command.status())
        return Status.from_string(response)

    def _get_response_for_command(self, command: str) -> Response:
        response = self._serial.send_command(command)
        return Response.from_string(response)
