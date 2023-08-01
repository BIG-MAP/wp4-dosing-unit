import serial


import time


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