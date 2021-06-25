import serial
from evdev import UInput, categorize, ecodes as e, AbsInfo
from tourboxneo.constants import MAPPING, CAP


class TourBox:

    def __init__(self, dev_path='/dev/ttyACM0'):
        self.dev_path = dev_path
        self.serial = None
        self.controller = None

    def start(self):
        self.serial = serial.PosixPollSerial(self.dev_path)
        self.controller = UInput(CAP, name='TourBox', vendor=0x0483, product=0x5740)

        while self.serial.is_open:
            x = self.serial.read()
            for m in MAPPING.get(x, []):
                self.controller.write(*m)
            self.controller.syn()

def main():
    t = TourBox()
    t.start()


if __name__ == '__main__':
    main()
