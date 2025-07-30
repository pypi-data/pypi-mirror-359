import logging
import time

from src.driver_sble_py_klsblelcf import KlSbleLcr

logging.basicConfig(level=logging.DEBUG)


def callback(beacon):
    logging.info(beacon)


driver = KlSbleLcr('COM22')


if driver.is_connected():
    driver.set_notification_callback(callback)

    driver.set_tx_power(31)
    driver.configure_freq(915)
    driver.start_cw()
    input()
    driver.stop_cw()