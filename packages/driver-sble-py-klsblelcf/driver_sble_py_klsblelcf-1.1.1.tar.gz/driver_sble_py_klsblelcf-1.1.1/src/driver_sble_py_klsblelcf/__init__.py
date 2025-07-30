import logging
import struct
from typing import Callable, List

from .power import POWER_TABLE
from .protocols.data_unit.data_unit import DataUnit
from .protocols.host import BleReaderCommands
from .protocols.host.host_handler import HostHandler
from .transports.serial import SerialTransport

logger = logging.getLogger(__name__)


class KlSbleLcr:

    def __init__(self, connection_string=None):
        self._transport: SerialTransport | None = None
        self._host_controller = HostHandler()
        self.connection_string = connection_string
        if connection_string is not None:
            self.connect(connection_string)

    def set_notification_callback(self, notification_callback: Callable[[any], None]):
         self._host_controller.set_notification_callback(notification_callback)

    def connect(self, connection_string=None) -> bool:
        if connection_string:
            self.connection_string = connection_string
        # TODO: Parse connection string to determine transport type (serial only for now)
        self._transport = SerialTransport(read_callback=self._host_controller.append_data)
        return self._transport.connect(connection_string)

    def is_connected(self) -> bool:
        if self._transport is None:
            return False
        return self._transport.is_connected()

    def disconnect(self) -> bool:
        if not self.is_connected():
            logger.info('Transport already disconnected.')
            return True
        try:
            self._transport.disconnect()
            logger.info('Transport successfully disconnected.')
            return True
        except Exception as e:
            logger.warning(e)
            return False

    def _execute_command(self, command_packet: DataUnit, has_response: bool = True):
        if not self._transport.is_connected():
            if self.connection_string is None:
                logger.info('Transport is disconnected.')
                return None
            if not self._transport.connect(self.connection_string):
                logger.info('Transport is disconnected.')
                return None

        logger.info('TX -> ' + command_packet.get_command_code().name)
        self._transport.write(command_packet.bytes())
        if has_response:
            try:
                response = self._host_controller.get_response()
                logger.info('RX <- ' + str(response))
                return response
            except TimeoutError:
                logger.warning('Timeout executing ' + command_packet.get_command_code().name)
                return None

    def configure_cw(self, enable: bool, dac0_value: int, dac1_value: int):
        logging.info('configure_cw: ' + str(enable) + ' ' + str(dac0_value) + ' ' + str(dac1_value))
        payload = bytearray(bytes([enable]) + struct.pack('>H', dac0_value) + struct.pack('>H', dac1_value))
        packet = DataUnit(command_code=BleReaderCommands.SET_868_RADIO, args=payload)
        response = self._execute_command(packet, has_response=True)
        return response

    def ping(self) -> bool:
        logging.info('PING')
        packet = DataUnit(command_code=BleReaderCommands.PING)
        response = self._execute_command(packet, has_response=True)
        return response

    # def get_reader_info(self) -> ReaderInfo:
    # TODO
    #     return info

    def get_tx_power(self) -> float:
        logging.info('Start CW')
        packet = DataUnit(command_code=BleReaderCommands.GET_TX_POWER)
        response = self._execute_command(packet, has_response=True)

        if response is not None:
            dac0_value = int.from_bytes(response[0:2], byteorder='big')
            dac1_value = int.from_bytes(response[2:4], byteorder='big')

            for power_level, power_data in POWER_TABLE.items():
                if power_data.dac0 == dac0_value and power_data.dac1 == dac1_value:
                    power_dbm = power_level/10
                    logging.info(f"Match found in POWER_TABLE: Power dBm {power_dbm}")
                    return power_dbm

        logging.warning("No match found in POWER_TABLE for the given response.")
        return None


    def set_tx_power(self, dBm: float) -> bool:
        if dBm < 10:
            dBm = 10
        if dBm > 32:
            dBm = 32
        self._power_dbm = dBm
        power_ddbm = round(self._power_dbm * 2) * 5
        logging.debug('Setting Power: ' + str(round(power_ddbm / 10, 1)) + ' dBm')

        logging.info('Configure tx power: ' + ' ' + str(POWER_TABLE[power_ddbm].dac0) + ' ' + str(POWER_TABLE[power_ddbm].dac1))
        payload = bytearray(struct.pack('>H', POWER_TABLE[power_ddbm].dac0) + struct.pack('>H', POWER_TABLE[power_ddbm].dac1))
        packet = DataUnit(command_code=BleReaderCommands.SET_TX_POWER, args=payload)
        response = self._execute_command(packet, has_response=True)
        return response

    def start_cw(self) -> bool:
        logging.info('Start CW')
        packet = DataUnit(command_code=BleReaderCommands.START_CW)
        response = self._execute_command(packet, has_response=True)
        return response

    def stop_cw(self) -> bool:
        logging.info('Stop CW')
        packet = DataUnit(command_code=BleReaderCommands.STOP_CW)
        response = self._execute_command(packet, has_response=True)
        return response

    def configure_freq(self, frequency: int):
        logging.info('Configure Frequency: ' + str(frequency))
        payload = bytearray(struct.pack('>H', frequency))
        packet = DataUnit(command_code=BleReaderCommands.SET_FREQUENCY, args=payload)
        response = self._execute_command(packet, has_response=True)
        return response

    def get_freq(self) -> int:
        logging.info('Get Frequency: ')
        packet = DataUnit(command_code=BleReaderCommands.GET_FREQUENCY)
        response = self._execute_command(packet, has_response=True)
        return response

    def get_cw_status(self) -> bool:
        logging.info('Get CW status: ')
        packet = DataUnit(command_code=BleReaderCommands.GET_CW_STATUS)
        response = self._execute_command(packet, has_response=True)
        return response

    def reset_cc1310(self) -> bool:
        logging.info('Reset CC1310')
        packet = DataUnit(command_code=BleReaderCommands.RESET_CC1310)
        response = self._execute_command(packet, has_response=True)
        return response

    def reset_dac5302(self) -> bool:
        logging.info('Reset DAC5302')
        packet = DataUnit(command_code=BleReaderCommands.RESET_DAC5302)
        response = self._execute_command(packet, has_response=True)
        return response

    def reset_cc2340(self) -> bool:
        logging.info('Reset CC2340')
        packet = DataUnit(command_code=BleReaderCommands.RESET_CC2340)
        response = self._execute_command(packet, has_response=True)
        return response

    def reset_all(self) -> bool:
        logging.info('Reset ALL')
        packet = DataUnit(command_code=BleReaderCommands.RESET_ALL)
        response = self._execute_command(packet, has_response=True)
        return response


