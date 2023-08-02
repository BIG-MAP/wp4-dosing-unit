from serial.tools import list_ports

for device in list_ports():
    print(f"name={device.name}, description={device.description}, hwid={device.hwid}")
