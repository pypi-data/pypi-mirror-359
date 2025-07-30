from enum import Enum

class BleReaderCommands(Enum):
    SET_868_RADIO = 0
    SET_TX_POWER = 1
    GET_TX_POWER = 2
    START_CW = 3
    STOP_CW = 4
    PING = 5
    BEACON_DATA = 6
    SET_FREQUENCY = 7
    GET_FREQUENCY = 8
    GET_CW_STATUS = 9
    RESET_CC1310 = 10
    RESET_DAC5302 = 11
    RESET_CC2340 = 12
    RESET_ALL = 13