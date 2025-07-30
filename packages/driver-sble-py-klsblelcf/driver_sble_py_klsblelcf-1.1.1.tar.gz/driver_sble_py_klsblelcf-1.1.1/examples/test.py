import logging
import time
from lib2to3.pgen2.driver import Driver

from src.driver_sble_py_klsblelcf import KlSbleLcr

logging.basicConfig(level=logging.DEBUG)


def callback(beacon):
    logging.info(beacon)


driver = KlSbleLcr('COM18')


if driver.is_connected():
    driver.set_notification_callback(callback)

    driver.set_tx_power(31)
    driver.configure_freq(915)
    #driver.start_cw()
    driver.stop_cw()

    for idx in range(10, 32, 1):
        time.sleep(2)
        driver.get_tx_power()
        time.sleep(2)
        driver.set_tx_power(idx)


