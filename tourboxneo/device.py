import sys
import os

import serial
from time import sleep
from evdev import UInput, categorize, ecodes as e, AbsInfo
from serial import SerialException
import logging
import signal
import pathlib
from tourboxneo.constants import MAPPING, CAP

logger = logging.getLogger(__name__)

pid = str(os.getpid())
pidfile = os.getenv('pidfile') or "/run/tourbox.pid"
p = pathlib.Path(pidfile)


class GracefulKiller:
  kill_now = False
  def __init__(self):
    signal.signal(signal.SIGINT, self.exit_gracefully)
    signal.signal(signal.SIGTERM, self.exit_gracefully)

  def exit_gracefully(self, *args):
    self.kill_now = True


class TourBox:

    exit = False

    def __init__(self, dev_path='/dev/ttyACM0'):
        self.dev_path = dev_path
        self.serial = None
        self.controller = None
        self.killer = GracefulKiller()

    def start(self):
        p.write_text(pid)
        self.serial = serial.Serial(self.dev_path, timeout=2)
        self.controller = UInput(CAP, name='TourBox', vendor=0x0483, product=0x5740)
        reconnects = 0
        while not self.killer.kill_now:
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
        logger.debug('Exiting Tourbox Daemon')

def main():
    t = TourBox(dev_path=sys.argv[1])
    t.start()


if __name__ == '__main__':
    main()
