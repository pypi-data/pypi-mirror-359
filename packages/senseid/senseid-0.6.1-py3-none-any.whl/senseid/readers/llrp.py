import logging
import time
from enum import Enum
from typing import List, Callable

from sllurp.llrp import LLRPReaderClient, LLRPReaderConfig, LLRP_DEFAULT_PORT, LLRPReaderState

from . import SenseidReader, SenseidReaderDetails
from ..parsers import SenseidTag
from ..parsers.rain import SenseidRainTag

logger = logging.getLogger(__name__)


class LlrpReaderManufacturer(Enum):
    IMPINJ = 25882
    MOTOROLA = 161
    SIRIT = 24831


class LlrpCommunicationStandard(Enum):
    UNSPECIFIED = 0
    US_FCC_Part_15_4W = 1
    ETSI_302_208 = 2
    ETSI_300_220_500mW = 3
    Australia_LIPD_1W = 4
    Australia_LIPD_4W = 5
    Japan_ARIB_STD_T89 = 6
    Hong_Kong_OFTA_1049_2W = 7
    Taiwan_DGT_LP0002 = 8
    Korea_MIC_Article_5_2 = 9
    _902_928MHz_4_W = 10
    ETSI_302_208_Lower_Band_2W = 11
    Brazil_Lower_Band_4W = 12
    China_Lower_Band_2W = 13
    China_Higher_Band_2W = 14
    Hong_Kong_China_4W = 15
    Israel_2W = 16
    Japan_954_4W = 17
    Japan_955_20mW = 18
    _865_868MHz_500mW = 19
    Korea_4W = 20
    Korea_200mW = 21
    Malaysia_2W = 23
    New_Zealand_Lower_Band_6W = 24
    Singapore_500mW = 25
    Singapore_2W = 26
    South_Africa_4W_FHSS = 27
    South_Africa_4W = 28
    Taiwan_1W = 29
    Taiwan_500mW = 30
    Thailand_4W = 31
    Venezuela_4W = 32
    Vietnam_500mW = 33
    Vietnam_2W = 34
    Japan_4W = 35
    Japan_500mW = 36
    Brazil_Higher_Band_4W = 37
    New_Zealand_Higher_Band_6W = 38


class ImpinjReaderMode(Enum):
    MaxThroughput = 0
    Hybrid = 1
    DenseReaderM4 = 2
    DenseReaderM8 = 3
    MaxMiller = 4
    DenseReaderM4Two = 5
    AutoSetDenseReader = 1000
    AutoSetDenseReaderDeepScan = 1002
    AutoSetStaticFast = 1003
    AutoSetStaticDRM = 1004
    AutoSetCustom = 1005


class ImpinjSearchMode(Enum):
    ReaderSelected = 0
    SingleTarget = 1
    DualTarget = 2
    TagFocus = 3
    SingleTargetReset = 5
    DualTargetBtoASelect = 6


class SenseidLlrp(SenseidReader):

    def __init__(self, is_impinj: bool):
        self.driver: LLRPReaderClient | None = None
        self.notification_callback = None
        self.details = SenseidReaderDetails()
        self._tx_power: float | None = None
        self._antennas: List[bool] = [True]
        self._is_impinj: bool = is_impinj

    def connect(self, connection_string: str):
        try:
            self.connection_string = connection_string
            config = LLRPReaderConfig()
            config.start_inventory = False
            config.reset_on_connect = True
            if self._is_impinj:
                config.impinj_extended_configuration = True
            self.driver = LLRPReaderClient(self.connection_string, LLRP_DEFAULT_PORT, config)

            capabilities_received = False

            def on_get_capabilities(reader: LLRPReaderClient, state):
                nonlocal capabilities_received
                if not capabilities_received:
                    logger.debug('TODO: parse capabilities with non impinj readers')

                    if self._is_impinj:
                        self.details.model_name = self.driver.llrp.capabilities['ImpinjDetailedVersion'][
                        'ModelName'].decode('utf-8')
                        self.details.firmware_version = self.driver.llrp.capabilities['ImpinjDetailedVersion'][
                        'FirmwareVersion'].decode('utf-8')
                    else:
                        self.details.model_name = self.driver.llrp.capabilities['GeneralDeviceCapabilities'][
                        'ModelName']
                        self.details.firmware_version = self.driver.llrp.capabilities['GeneralDeviceCapabilities'][
                        'ReaderFirmwareVersion']
                    self.details.antenna_count = self.driver.llrp.capabilities['GeneralDeviceCapabilities'][
                        'MaxNumberOfAntennaSupported']
                    self.details.min_tx_power = self.driver.llrp.tx_power_table[1]
                    self.details.max_tx_power = self.driver.llrp.tx_power_table[-1]
                    self.details.region = LlrpCommunicationStandard(
                        self.driver.llrp.capabilities['RegulatoryCapabilities']['CommunicationsStandard']).name
                    logger.debug(reader.llrp.capabilities)
                    capabilities_received = True

            self.driver.add_state_callback(LLRPReaderState.STATE_SENT_GET_CONFIG, on_get_capabilities)
            self.driver.add_tag_report_callback(self._llrp_notification_callback)
            self.driver.connect()

            while not capabilities_received:
                time.sleep(0.1)
            self.driver.disconnect(None)
            self._tx_power = self.details.max_tx_power

            return True
        except Exception as e:
            logger.error(e)
            return False

    def _llrp_notification_callback(self, reader: LLRPReaderClient, tag_reports):
        logger.debug(tag_reports)
        if self.notification_callback is not None:
            for tag in tag_reports:
                #for n in range(tag['TagSeenCount']):
                self.notification_callback(SenseidRainTag(epc=tag['EPC'].decode('utf-8')))

    def disconnect(self):
        self.driver.disconnect()
        self.driver.join()

    def get_details(self) -> SenseidReaderDetails:
        return self.details

    def get_tx_power(self) -> float:
        # Only supporting same power on all antennas
        return self._tx_power

    def set_tx_power(self, dbm: float):
        # Only supporting same power on all antennas
        if self.details is None:
            self.get_details()
        if dbm > self.details.max_tx_power:
            dbm = self.details.max_tx_power
            logger.warning('Power set to max power: ' + str(dbm))
        if dbm < self.details.min_tx_power:
            dbm = self.details.min_tx_power
            logger.warning('Power set to min power: ' + str(dbm))
        self._tx_power = dbm

    def get_antenna_config(self) -> List[bool]:
        return self._antennas

    def set_antenna_config(self, antenna_config_array: List[bool]):
        if not (True in antenna_config_array):
            antenna_config_array[0] = True
            logger.warning('At least one antenna needs to be active. Enabling antenna 1.')
        self._antennas = antenna_config_array

    def start_inventory_async(self, notification_callback: Callable[[SenseidTag], None]):
        self.notification_callback = notification_callback

        config = LLRPReaderConfig()
        config.start_inventory = True
        config.reset_on_connect = True
        if self._is_impinj:
            config.impinj_extended_configuration = True
        config.duration = 0.2
        config.tag_content_selector = {
            'EnableROSpecID': False,
            'EnableSpecIndex': False,
            'EnableInventoryParameterSpecID': False,
            'EnableAntennaID': False,
            'EnableChannelIndex': False,
            'EnablePeakRSSI': False,
            'EnableFirstSeenTimestamp': False,
            'EnableLastSeenTimestamp': False,
            'EnableTagSeenCount': True,
            'EnableAccessSpecID': False,
            'C1G2EPCMemorySelector': {
                'EnableCRC': False,
                'EnablePCBits': False,
            }
        }
        if self._is_impinj:
            config.impinj_search_mode = ImpinjReaderMode.DenseReaderM4.value
        config.mode_identifier = ImpinjSearchMode.DualTarget.value
        config.antennas = []
        config.tx_power = {}
        config.tx_power_dbm = {}
        for idx, enable in enumerate(self._antennas):
            if enable:
                config.antennas.append(idx + 1)
                config.tx_power[idx + 1] = 0
                config.tx_power_dbm[idx + 1] = self._tx_power

        self.driver = LLRPReaderClient(self.connection_string, LLRP_DEFAULT_PORT, config)
        self.driver.add_tag_report_callback(self._llrp_notification_callback)
        self.driver.connect()

    def stop_inventory_async(self):
        config = LLRPReaderConfig()
        config.start_inventory = False
        config.reset_on_connect = True
        self.driver.update_config(config)
        self.driver.disconnect(None)
