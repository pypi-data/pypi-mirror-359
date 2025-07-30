from TuXingKeJi.TuXingSDK import TuXingSDK
from TuXingKeJi.peripheral import Peripheral
from TuXingKeJi.serialHelper import find_serial_port

if __name__ == '__main__':
    port_name = find_serial_port()
    print(port_name)
    if len(port_name) > 0:
        peripheral = Peripheral(port_name[0])
        tuxing = TuXingSDK(peripheral)
        tuxing.start()
        tuxing.init_uav()
        tuxing.stop()
