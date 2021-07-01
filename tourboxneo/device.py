import sys

import serial
from time import sleep
from evdev import UInput, categorize, ecodes as e, AbsInfo
from serial import SerialException
import logging
from tourboxneo.constants import MAPPING, CAP

logger = logging.getLogger(__name__)


class TourBox:

    def __init__(self, dev_path='/dev/ttyACM0'):
        self.dev_path = dev_path
        self.serial = None
        self.controller = None

    def start(self):
        self.serial = serial.Serial(self.dev_path)
        self.controller = UInput(CAP, name='TourBox', vendor=0x0483, product=0x5740)

        reconnects = 0
        while self.serial.is_open:
            try:
                x = self.serial.read()
            except SerialException:
                logging.warning(f"Can't read: {self.dev_path}, maybe unplugged or no permission?")
                if reconnects < 5:
                    sleep(1)
                    reconnects += 1
                    continue
                return 1

            reconnects = 0
            for m in MAPPING.get(x, []):
                self.controller.write(*m)
            self.controller.syn()


def main():
    try:
        t = TourBox(dev_path=sys.argv[1])
        t.start()
    except KeyboardInterrupt:
        return


if __name__ == '__main__':
    main()
