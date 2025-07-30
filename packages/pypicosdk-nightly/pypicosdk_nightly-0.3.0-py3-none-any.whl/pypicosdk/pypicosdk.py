import ctypes
import os
import warnings
import platform
import time
import typing

from .error_list import ERROR_STRING
from .constants import *
from .version import VERSION

# Exceptions
class PicoSDKNotFoundException(Exception):
    pass

class PicoSDKException(Exception):
    pass

class OverrangeWarning(UserWarning):
    pass

class PowerSupplyWarning(UserWarning):
    pass


# General Functions
def _check_path(location, folders):
    for folder in folders:
        path = os.path.join(location, folder)
        if os.path.exists(path):
            return path
    raise PicoSDKException("No PicoSDK or PicoScope 7 drivers installed, get them from http://picotech.com/downloads")

def _get_lib_path() -> str:
    system = platform.system()
    if system == "Windows":
        program_files = os.environ.get("PROGRAMFILES")
        checklist = [
            'Pico Technology\\SDK\\lib', 
            'Pico Technology\\PicoScope 7 T&M Stable',
            'Pico Technology\\PicoScope 7 T&M Early Access']
        return _check_path(program_files, checklist)
    elif system == "Linux":
        return _check_path('opt', 'picoscope')
    elif system == "Darwin":
        raise PicoSDKException("macOS is not yet tested and supported")
    else:
        raise PicoSDKException("Unsupported OS")

def get_all_enumerated_units() -> tuple[int, list[str]]:
    """
    Enumerates all PicoScope units supported by this wrapper
    returns the number of units and serial of each unit

    Returns:
        tuple[int, list[str]]: int of units and list of unit serials
    """
    n_units = 0
    unit_serial = []
    for scope in [ps6000a()]:
        units = scope.get_enumerated_units()
        n_units += units[0]
        unit_serial += units[1].split(',')
    return n_units, unit_serial


# PicoScope Classes
class PicoScopeBase:
    """PicoScope base class including common SDK and python modules and functions"""
    # Class Functions
    def __init__(self, dll_name, *args, **kwargs):
        # Pytest override
        self._pytest = "pytest" in args
            
        # Setup DLL location per device
        if self._pytest:
            self.dll = None
        else:
            self.dll = ctypes.CDLL(os.path.join(_get_lib_path(), dll_name + ".dll"))
        self._unit_prefix_n = dll_name

        # Setup class variables
        self.handle = ctypes.c_short()
        self.range = {}
        self.probe_scale = {}
        self.resolution = None
        self.max_adc_value = None
        self.min_adc_value = None
        self.over_range = 0
    
    def __exit__(self):
        self.close_unit()

    def __del__(self):
        self.close_unit()

    # General Functions
    def _get_attr_function(self, function_name: str) -> ctypes.CDLL:
        """
        Returns ctypes function based on sub-class prefix name.

        For example, `_get_attr_function("OpenUnit")` will return `self.dll.ps####aOpenUnit()`.

        Args:
            function_name (str): PicoSDK function name, e.g., "OpenUnit".

        Returns:
            ctypes.CDLL: CDLL function for the specified name.
        """
        return getattr(self.dll, self._unit_prefix_n + function_name)
    
    def _error_handler(self, status: int) -> None:
        """
        Checks status code against error list; raises an exception if not 0.

        Errors such as `SUPPLY_NOT_CONNECTED` are returned as warnings.

        Args:
            status (int): Returned status value from PicoSDK.

        Raises:
            PicoSDKException: Pythonic exception based on status value.
        """
        error_code = ERROR_STRING[status]
        if status != 0:
            if status in [POWER_SOURCE.SUPPLY_NOT_CONNECTED]:
                warnings.warn('Power supply not connected.',
                              PowerSupplyWarning)
                return
            # Certain status codes indicate that the driver is busy or waiting
            # for more data rather than an actual failure. These should not
            # raise an exception as callers may poll until data is ready.
            if status == 407:  # PICO_WAITING_FOR_DATA_BUFFERS
                return
            self.close_unit()
            raise PicoSDKException(error_code)
        return
    
    def _call_attr_function(self, function_name:str, *args) -> int:
        """
        Calls a specific attribute function with the provided arguments.

        Args:
            function_name (str): PicoSDK function suffix.

        Returns:
            int: Returns status integer of PicoSDK dll.
        """
        attr_function = self._get_attr_function(function_name)
        status = attr_function(*args)
        self._error_handler(status)
        return status

    # General PicoSDK functions    
    def _open_unit(self, serial_number:int=None, resolution:RESOLUTION=0) -> None:
        """
        Opens PicoScope unit.

        Args:
            serial_number (int, optional): Serial number of specific unit, e.g., JR628/0017.
            resolution (RESOLUTION, optional): Resolution of device. 
        """

        if serial_number is not None:
            serial_number = serial_number.encode()
        self._call_attr_function(
            'OpenUnit',
            ctypes.byref(self.handle),
            serial_number, 
            resolution
        )
        self.resolution = resolution
    
    def close_unit(self) -> None:
        """
        Closes the PicoScope device and releases the hardware handle.

        This calls the PicoSDK `CloseUnit` function to properly disconnect from the device.

        Returns:
                None
        """
        if self._pytest:
            return
        else:
            self._get_attr_function('CloseUnit')(self.handle)

    def stop(self) -> None: 
        """
        This function stops the scope device from sampling data
        """
        self._call_attr_function(
            'Stop',
            self.handle
        )

    def is_ready(self) -> None:
        """
        Blocks execution until the PicoScope device is ready.

        Continuously calls the PicoSDK `IsReady` function in a loop, checking if
        the device is prepared to proceed with data acquisition.

        Returns:
                None
        """

        ready = ctypes.c_int16()
        attr_function = getattr(self.dll, self._unit_prefix_n + "IsReady")
        while True:
            status = attr_function(
                self.handle, 
                ctypes.byref(ready)
            )
            self._error_handler(status)
            if ready.value != 0:
                break
    
    # Get information from PicoScope
    def get_unit_info(self, unit_info: UNIT_INFO) -> str:
        """
        Get specified information from unit. Use UNIT_INFO.XXXX or integer.

        Args:
            unit_info (UNIT_INFO): Specify information from PicoScope unit i.e. UNIT_INFO.PICO_BATCH_AND_SERIAL.

        Returns:
            str: Returns data from device.
        """
        string = ctypes.create_string_buffer(16)
        string_length = ctypes.c_int16(32)
        required_size = ctypes.c_int16(32)
        status = self._call_attr_function(
            'GetUnitInfo',
            self.handle,
            string,
            string_length,
            ctypes.byref(required_size),
            ctypes.c_uint32(unit_info)
        )
        return string.value.decode()
    
    def get_unit_serial(self) -> str:
        """
        Get and return batch and serial of unit.

        Returns:
                str: Returns serial, e.g., "JR628/0017".
        """
        return self.get_unit_info(UNIT_INFO.PICO_BATCH_AND_SERIAL)
    
    def _get_enabled_channel_flags(self) -> int:
        """
        Returns integer of enabled channels as a binary code.
        Where channel A is LSB.
        I.e. Channel A and channel C would be '0101' -> 5

        Returns:
            int: Decimal of enabled channels
        """
        enabled_channel_byte = 0
        for channel in self.range:
            enabled_channel_byte += 2**channel
        return enabled_channel_byte
    
    def get_nearest_sampling_interval(self, interval_s:float) -> dict:
        """
        This function returns the nearest possible sample interval to the requested 
        sample interval. It does not change the configuration of the oscilloscope.

        Channels need to be setup first before calculating as more channels may 
        increase sample interval.

        Args:
            interval_s (float): Time value in seconds (s) you would like to obtain.

        Returns:
            dict: Dictionary of suggested timebase and actual sample interval in seconds (s).
        """
        timebase = ctypes.c_uint32()
        time_interval = ctypes.c_double()
        self._call_attr_function(
            'NearestSampleIntervalStateless',
            self.handle,
            self._get_enabled_channel_flags(),
            ctypes.c_double(interval_s),
            self.resolution,
            ctypes.byref(timebase),
            ctypes.byref(time_interval),
        )
        return {"timebase": timebase.value, "actual_sample_interval": time_interval.value}
    
    def get_timebase(timebase, samples):
        # Override for PicoScopeBase
        raise NotImplementedError("Method not yet available for this oscilloscope")
    
    def _get_timebase(self, timebase: int, samples: int, segment:int=0) -> dict:
        """
        This function calculates the sampling rate and maximum number of 
        samples for a given timebase under the specified conditions.

        Args:
                timebase (int): Selected timebase multiplier (refer to programmer's guide).
                samples (int): Number of samples.
                segment (int, optional): The index of the memory segment to use.

        Returns:
                dict: Returns interval (ns) and max samples as a dictionary.
        """
        time_interval_ns = ctypes.c_double()
        max_samples = ctypes.c_uint64()
        attr_function = getattr(self.dll, self._unit_prefix_n + 'GetTimebase')
        status = attr_function(
            self.handle,
            timebase,
            samples,
            ctypes.byref(time_interval_ns),
            ctypes.byref(max_samples),
            segment
        )
        self._error_handler(status)
        return {"Interval(ns)": time_interval_ns.value, 
                "Samples":          max_samples.value}
    
    def _get_timebase_2(self, timebase: int, samples: int, segment:int=0):
        """
        Calculates the sampling rate and maximum number of samples for a given
        timebase under the specified conditions.

        Args:
                timebase (int): Selected timebase multiplier (refer to programmer's guide).
                samples (int): Number of samples.
                segment (int, optional): Index of the memory segment to use.

        Returns:
                dict: Dictionary containing:
                        - 'interval' (ns): Time interval between samples.
                        - 'max_samples': Maximum number of samples.
        """
        time_interval_ns = ctypes.c_float()
        max_samples = ctypes.c_int32()
        attr_function = getattr(self.dll, self._unit_prefix_n + 'GetTimeBase2')
        status = attr_function(
            self.handle,
            timebase,
            samples,
            ctypes.byref(time_interval_ns),
            ctypes.byref(max_samples),
            segment
        )
        self._error_handler(status)
        return {"Interval(ns)": time_interval_ns.value, 
                "Samples":          max_samples.value}
    
    def sample_rate_to_timebase(self, sample_rate:float, unit=SAMPLE_RATE.MSPS):
        """
        Converts sample rate to a PicoScope timebase value based on the 
        attached PicoScope.

        This function will return the closest possible timebase.
        Use `get_nearest_sample_interval(interval_s)` to get the full timebase and 
        actual interval achieved.

        Args:
            sample_rate (int): Desired sample rate 
            unit (SAMPLE_RATE): unit of sample rate.
        """
        interval_s = 1 / (sample_rate * unit)
        
        return self.get_nearest_sampling_interval(interval_s)["timebase"]
    
    def interval_to_timebase(self, interval:float, unit=TIME_UNIT.S):
        """
        Converts a time interval (between samples) into a PicoScope timebase 
        value based on the attached PicoScope.

        This function will return the closest possible timebase.
        Use `get_nearest_sample_interval(interval_s)` to get the full timebase and 
        actual interval achieved.

        Args:
            interval (float): Desired time interval between samples
            unit (TIME_UNIT, optional): Time unit of interval.
        """
        interval_s = interval / unit
        return self.get_nearest_sampling_interval(interval_s)["timebase"]
    
    def _get_adc_limits(self) -> tuple:
        """
        Gets the ADC limits for specified devices.

        Currently tested on: 6000a.

        Returns:
                tuple: (minimum value, maximum value)

        Raises:
                PicoSDKException: If device hasn't been initialized.
        """
        if self.resolution is None:
            raise PicoSDKException("Device has not been initialized, use open_unit()")
        min_value = ctypes.c_int32()
        max_value = ctypes.c_int32()
        self._call_attr_function(
            'GetAdcLimits',
            self.handle,
            self.resolution,
            ctypes.byref(min_value),
            ctypes.byref(max_value)
        )
        return min_value.value, max_value.value
    
    def _get_maximum_adc_value(self) -> int:
        """
        Gets the ADC limits for specified devices.

        Currently tested on: 5000a.

        Returns:
                int: Maximum ADC value.
        """
        max_value = ctypes.c_int16()
        self._call_attr_function(
            'MaximumValue',
            self.handle,
            ctypes.byref(max_value)
        )
        return max_value.value
    
    def get_time_axis(self, timebase:int, samples:int) -> list:
        """
        Return an array of time values based on the timebase and number
        of samples

        Args:
            timebase (int): PicoScope timebase 
            samples (int): Number of samples captured

        Returns:
            list: List of time values in nano-seconds
        """
        interval = self.get_timebase(timebase, samples)['Interval(ns)']
        return [round(x*interval, 4) for x in range(samples)]
    
    def get_trigger_time_offset(self, time_unit: TIME_UNIT, segment_index: int = 0) -> int:
        """
        Get the trigger time offset for jitter correction in waveforms.

        The driver interpolates between adjacent samples to estimate when the
        trigger actually occurred.  This means the value returned can have a
        very fine granularity—down to femtoseconds—even though the effective
        resolution is usually limited to roughly one-tenth of the sampling
        interval in real-world use.

        Args:
            time_unit (TIME_UNIT): Desired unit for the returned offset.
            segment_index (int, optional): The memory segment to query. Default
                is 0.

        Returns:
            int: Trigger time offset converted to ``time_unit``.

        Raises:
            PicoSDKException: If the function call fails or preconditions are
                not met.
        """
        time = ctypes.c_int64()
        returned_unit = ctypes.c_int32()

        self._call_attr_function(
            'GetTriggerTimeOffset',
            self.handle,
            ctypes.byref(time),
            ctypes.byref(returned_unit),
            ctypes.c_uint64(segment_index)
        )

        # Convert the returned time to the requested ``time_unit``
        pico_unit = PICO_TIME_UNIT(returned_unit.value)
        time_s = time.value / TIME_UNIT[pico_unit.name]
        return int(time_s * TIME_UNIT[time_unit.name])


    def get_trigger_info(
        self,
        first_segment_index: int = 0,
        segment_count: int = 1,
    ) -> typing.Union[PICO_TRIGGER_INFO, list[PICO_TRIGGER_INFO]]:
        """Retrieve trigger timing information for one or more segments.

        This method wraps the ``ps6000aGetTriggerInfo`` API call and returns
        one or more :class:`~pypicosdk.constants.PICO_TRIGGER_INFO` structures.
        Each structure exposes attributes such as ``status_``, ``triggerTime_``
        and ``timeUnits_`` (refer to :mod:`pypicosdk.constants` for the full
        list of fields).  The ``status_`` field is a
        :class:`~pypicosdk.constants.PICO_STATUS` bit field that may include
        flags like ``PICO_DEVICE_TIME_STAMP_RESET`` or
        ``PICO_TRIGGER_TIME_NOT_REQUESTED``. ``timeUnits_`` values are defined
        by :class:`~pypicosdk.constants.PICO_TIME_UNIT`.

        Args:
            first_segment_index: Index of the first memory segment to query.
            segment_count: Number of consecutive segments starting at
                ``first_segment_index``.

        Returns:
            If ``segment_count`` is ``1``, a single ``PICO_TRIGGER_INFO``
            instance is returned. Otherwise a list of ``PICO_TRIGGER_INFO``
            objects is provided.

        Raises:
            PicoSDKException: If the function call fails or preconditions are
                not met.
        """

        info_array = (PICO_TRIGGER_INFO * segment_count)()

        self._call_attr_function(
            "GetTriggerInfo",
            self.handle,
            ctypes.byref(info_array[0]),
            ctypes.c_uint64(first_segment_index),
            ctypes.c_uint64(segment_count),
        )

        if segment_count == 1:
            return info_array[0]
        return list(info_array)

    def get_values_trigger_time_offset_bulk(
        self,
        from_segment_index: int,
        to_segment_index: int,
    ) -> list[tuple[int, PICO_TIME_UNIT]]:
        """Retrieve trigger time offsets for a range of segments.

        This method calls ``ps6000aGetValuesTriggerTimeOffsetBulk`` and
        returns the trigger time offset and associated time unit for each
        requested segment.

        Args:
            from_segment_index: Index of the first memory segment to query.
            to_segment_index: Index of the last memory segment. If this value
                is less than ``from_segment_index`` the driver wraps around.

        Returns:
            list[tuple[int, PICO_TIME_UNIT]]: ``[(offset, unit), ...]`` for each
            segment beginning with ``from_segment_index``.
        """

        count = to_segment_index - from_segment_index + 1
        times = (ctypes.c_int64 * count)()
        units = (ctypes.c_int32 * count)()

        self._call_attr_function(
            "GetValuesTriggerTimeOffsetBulk",
            self.handle,
            ctypes.byref(times),
            ctypes.byref(units),
            ctypes.c_uint64(from_segment_index),
            ctypes.c_uint64(to_segment_index),
        )

        results = []
        for i in range(count):
            results.append((times[i], PICO_TIME_UNIT(units[i])))
        return results

    def set_no_of_captures(self, n_captures: int) -> None:
        """Configure the number of captures for rapid block mode."""

        self._call_attr_function(
            "SetNoOfCaptures",
            self.handle,
            ctypes.c_uint64(n_captures),
        )

    def get_no_of_captures(self) -> int:
        """Return the number of captures configured for rapid block."""

        n_captures = ctypes.c_uint64()
        self._call_attr_function(
            "GetNoOfCaptures",
            self.handle,
            ctypes.byref(n_captures),
        )
        return n_captures.value

    def get_values_bulk(
        self,
        start_index: int,
        no_of_samples: int,
        from_segment_index: int,
        to_segment_index: int,
        down_sample_ratio: int,
        down_sample_ratio_mode: int,
        overflow: ctypes.c_int16,
    ) -> int:
        """Retrieve data from multiple memory segments."""

        self.is_ready()
        c_samples = ctypes.c_uint64(no_of_samples)
        self._call_attr_function(
            "GetValuesBulk",
            self.handle,
            ctypes.c_uint64(start_index),
            ctypes.byref(c_samples),
            ctypes.c_uint64(from_segment_index),
            ctypes.c_uint64(to_segment_index),
            ctypes.c_uint64(down_sample_ratio),
            down_sample_ratio_mode,
            ctypes.byref(overflow),
        )
        self.over_range = overflow.value
        self.is_over_range()
        return c_samples.value

    def get_values_bulk_async(
        self,
        start_index: int,
        no_of_samples: int,
        from_segment_index: int,
        to_segment_index: int,
        down_sample_ratio: int,
        down_sample_ratio_mode: int,
        lp_data_ready,
        p_parameter,
    ) -> None:
        """Begin asynchronous retrieval of values from multiple segments."""

        self._call_attr_function(
            "GetValuesBulkAsync",
            self.handle,
            ctypes.c_uint64(start_index),
            ctypes.c_uint64(no_of_samples),
            ctypes.c_uint64(from_segment_index),
            ctypes.c_uint64(to_segment_index),
            ctypes.c_uint64(down_sample_ratio),
            down_sample_ratio_mode,
            lp_data_ready,
            p_parameter,
        )

    def get_values_overlapped(
        self,
        start_index: int,
        no_of_samples: int,
        down_sample_ratio: int,
        down_sample_ratio_mode: int,
        from_segment_index: int,
        to_segment_index: int,
        overflow: ctypes.c_int16,
    ) -> int:
        """Retrieve overlapped data from multiple segments."""

        self.is_ready()
        c_samples = ctypes.c_uint64(no_of_samples)
        self._call_attr_function(
            "GetValuesOverlapped",
            self.handle,
            ctypes.c_uint64(start_index),
            ctypes.byref(c_samples),
            ctypes.c_uint64(down_sample_ratio),
            down_sample_ratio_mode,
            ctypes.c_uint64(from_segment_index),
            ctypes.c_uint64(to_segment_index),
            ctypes.byref(overflow),
        )
        self.over_range = overflow.value
        self.is_over_range()
        return c_samples.value

    def stop_using_get_values_overlapped(self) -> None:
        """Terminate overlapped capture mode."""

        self._call_attr_function(
            "StopUsingGetValuesOverlapped",
            self.handle,
        )


    
    # Data conversion ADC/mV & ctypes/int 
    def mv_to_adc(self, mv: float, channel_range: int, channel: typing.Optional[CHANNEL] = None) -> int:
        """
        Converts a millivolt (mV) value to an ADC value based on the device's
        maximum ADC range.

        Args:
                mv (float): Voltage in millivolts to be converted.
                channel_range (int): Range of channel in millivolts i.e. 500 mV.
                channel (CHANNEL, optional): Channel associated with ``mv``. The
                    probe scaling for the channel will be applied if provided.

        Returns:
                int: ADC value corresponding to the input millivolt value.
        """
        scale = self.probe_scale.get(channel, 1)
        channel_range_mv = RANGE_LIST[channel_range]
        return int(((mv / scale) / channel_range_mv) * self.max_adc_value)

    def adc_to_mv(self, adc: int, channel_range: int, channel: typing.Optional[CHANNEL] = None):
        """Converts ADC value to mV using the stored probe scaling."""
        scale = self.probe_scale.get(channel, 1)
        channel_range_mv = float(RANGE_LIST[channel_range])
        return ((float(adc) / float(self.max_adc_value)) * channel_range_mv) * scale
    
    def buffer_adc_to_mv(self, buffer: list, channel: str) -> list:
        """Converts an ADC buffer list to mV list"""
        return [self.adc_to_mv(sample, self.range[channel], channel) for sample in buffer]
    
    def channels_buffer_adc_to_mv(self, channels_buffer: dict) -> dict:
        "Converts dict of multiple channels adc values to millivolts (mV)"
        for channel in channels_buffer:
            channels_buffer[channel] = self.buffer_adc_to_mv(channels_buffer[channel], channel)
        return channels_buffer
    
    def buffer_ctypes_to_list(self, ctypes_list):
        "Converts a ctype dataset into a python list of samples"
        return [sample for sample in ctypes_list]
    
    def channels_buffer_ctype_to_list(self, channels_buffer):
        "Takes a ctypes channel dictionary buffer and converts into a integer array."
        for channel in channels_buffer:
            channels_buffer[channel] = self.buffer_ctypes_to_list(channels_buffer[channel])
        return channels_buffer

    # Set methods for PicoScope configuration    
    def _change_power_source(self, state: POWER_SOURCE) -> 0:
        """
        Change the power source of a device to/from USB only or DC + USB.

        Args:
                state (POWER_SOURCE): Power source variable (i.e. POWER_SOURCE.SUPPLY_NOT_CONNECTED).
        """
        self._call_attr_function(
            'ChangePowerSource',
            self.handle,
            state
        )

    def _set_channel_on(self, channel, range, coupling=COUPLING.DC, offset=0.0, bandwidth=BANDWIDTH_CH.FULL):
        """Sets a channel to ON at a specified range (6000E)"""
        self.range[channel] = range
        attr_function = getattr(self.dll, self._unit_prefix_n + 'SetChannelOn')
        status = attr_function(
            self.handle,
            channel,
            coupling,
            range,
            ctypes.c_double(offset),
            bandwidth
        )
        return self._error_handler(status)
    
    def _set_channel_off(self, channel):
        """Sets a channel to OFF (6000E)"""
        attr_function = getattr(self.dll, self._unit_prefix_n + 'SetChannelOff')
        status = attr_function(
            self.handle, 
            channel
        )
        return self._error_handler(status)
    
    def _set_channel(self, channel, range, enabled=True, coupling=COUPLING.DC, offset=0.0):
        """Set a channel ON with a specified range (5000D)"""
        self.range[channel] = range
        status = self.dll.ps5000aSetChannel(
            self.handle,
            channel,
            enabled,
            coupling,
            range,
            ctypes.c_float(offset)
        )
        return self._error_handler(status)
    
    def set_simple_trigger(self, channel, threshold_mv, enable=True, direction=TRIGGER_DIR.RISING, delay=0, auto_trigger=0):
        """Configure a simple edge trigger.

        Args:
            channel (int): The input channel to apply the trigger to.
            threshold_mv (float): Trigger threshold level in millivolts.
            enable (bool, optional): Enables or disables the trigger.
            direction (TRIGGER_DIR, optional): Trigger direction (e.g., ``TRIGGER_DIR.RISING``).
            delay (int, optional): Delay in samples after the trigger condition is met before starting capture.
            auto_trigger (int, optional): Timeout in **microseconds** after which data capture proceeds even if no
                trigger occurs.
        """
        if channel in self.range:
            threshold_adc = self.mv_to_adc(threshold_mv, self.range[channel], channel)
        else:
            threshold_adc = int(threshold_mv)
        self._call_attr_function(
            'SetSimpleTrigger',
            self.handle,
            enable,
            channel,
            threshold_adc,
            direction,
            delay,
            auto_trigger
        )

    def set_trigger_channel_conditions(
        self,
        source: int,
        state: int,
        action: int = ACTION.CLEAR_ALL | ACTION.ADD,
    ) -> None:
        """Configure a trigger condition using ``SetTriggerChannelConditions``.

        Args:
            source: Input source for the condition as a :class:`CHANNEL` value.
            state: Desired trigger state from :class:`PICO_TRIGGER_STATE`.
            action: How to apply the condition relative to any existing
                configuration. Defaults to ``ACTION.CLEAR_ALL | ACTION.ADD``.
        """

        cond = PICO_CONDITION(source, state)

        self._call_attr_function(
            "SetTriggerChannelConditions",
            self.handle,
            ctypes.byref(cond),
            ctypes.c_int16(1),
            action,
        )

    def set_trigger_channel_properties(
        self,
        threshold_upper: int,
        hysteresis_upper: int,
        threshold_lower: int,
        hysteresis_lower: int,
        channel: int,
        aux_output_enable: int = 0,
        auto_trigger_us: int = 0,
    ) -> None:
        """Configure trigger thresholds using ``SetTriggerChannelProperties``.

        Args:
            threshold_upper: ADC value for the upper trigger level.
            hysteresis_upper: Hysteresis for ``threshold_upper`` in ADC counts.
            threshold_lower: ADC value for the lower trigger level.
            hysteresis_lower: Hysteresis for ``threshold_lower`` in ADC counts.
            channel: Channel these settings apply to.
            aux_output_enable: Optional auxiliary output flag.
            auto_trigger_us: Auto-trigger timeout in microseconds. ``0`` waits
                indefinitely.
        """

        prop = PICO_TRIGGER_CHANNEL_PROPERTIES(
            threshold_upper,
            hysteresis_upper,
            threshold_lower,
            hysteresis_lower,
            channel,
        )

        self._call_attr_function(
            "SetTriggerChannelProperties",
            self.handle,
            ctypes.byref(prop),
            ctypes.c_int16(1),
            ctypes.c_int16(aux_output_enable),
            ctypes.c_uint32(auto_trigger_us),
        )

    def set_trigger_channel_directions(
        self,
        channel: int,
        direction: int,
        threshold_mode: int,
    ) -> None:
        """Configure trigger directions using ``SetTriggerChannelDirections``.

        Args:
            channel: Channel to apply the direction to.
            direction: Desired trigger direction from
                :class:`PICO_THRESHOLD_DIRECTION`.
            threshold_mode: Threshold mode from :class:`PICO_THRESHOLD_MODE`.
        """

        dir_struct = PICO_DIRECTION(channel, direction, threshold_mode)

        self._call_attr_function(
            "SetTriggerChannelDirections",
            self.handle,
            ctypes.byref(dir_struct),
            ctypes.c_int16(1),
        )
    
    def set_data_buffer_for_enabled_channels():
        raise NotImplementedError("Method not yet available for this oscilloscope")
    
    def _set_data_buffer_ps5000a(self, channel, samples, segment=0, ratio_mode=0):
        """Set data buffer (5000D)"""
        buffer = (ctypes.c_int16 * samples)
        buffer = buffer()
        self._call_attr_function(
            'SetDataBuffer',
            self.handle,
            channel,
            ctypes.byref(buffer),
            samples,
            segment,
            ratio_mode
        )
        return buffer
    
    def _set_data_buffer_ps6000a(
        self,
        channel,
        samples,
        segment=0,
        datatype=DATA_TYPE.INT16_T,
        ratio_mode=RATIO_MODE.RAW,
        action=ACTION.CLEAR_ALL | ACTION.ADD,
    ) -> ctypes.Array | None:
        """
        Allocates and assigns a data buffer for a specified channel on the 6000A series.

        Args:
            channel (int): The channel to associate the buffer with (e.g., CHANNEL.A).
            samples (int): Number of samples to allocate in the buffer.
            segment (int, optional): Memory segment to use. 
            datatype (DATA_TYPE, optional): C data type for the buffer (e.g., INT16_T). 
            ratio_mode (RATIO_MODE, optional): Downsampling mode. 
            action (ACTION, optional): Action to apply to the data buffer (e.g., CLEAR_ALL | ADD).

        Returns:
            ctypes.Array | None: The allocated buffer or ``None`` when clearing existing buffers.

        Raises:
            PicoSDKException: If an unsupported data type is provided.
        """
        if samples == 0:
            buffer = None
            buf_ptr = None
        else:
            if datatype == DATA_TYPE.INT8_T:
                ctype = ctypes.c_int8
            elif datatype == DATA_TYPE.INT16_T:
                ctype = ctypes.c_int16
            elif datatype == DATA_TYPE.INT32_T:
                ctype = ctypes.c_int32
            elif datatype == DATA_TYPE.INT64_T:
                ctype = ctypes.c_int64
            elif datatype == DATA_TYPE.UINT32_T:
                ctype = ctypes.c_uint32
            else:
                raise PicoSDKException("Invalid datatype selected for buffer")

            buffer = (ctype * samples)()
            buf_ptr = ctypes.byref(buffer)

        self._call_attr_function(
            "SetDataBuffer",
            self.handle,
            channel,
            buf_ptr,
            samples,
            datatype,
            segment,
            ratio_mode,
            action,
        )
        return buffer

    def _set_data_buffers_ps6000a(
        self,
        channel,
        samples,
        segment=0,
        datatype=DATA_TYPE.INT16_T,
        ratio_mode=RATIO_MODE.AGGREGATE,
        action=ACTION.CLEAR_ALL | ACTION.ADD,
    ) -> tuple[ctypes.Array, ctypes.Array]:
        """Allocate and assign max and min data buffers (6000A)."""

        if datatype == DATA_TYPE.INT8_T:
            ctype = ctypes.c_int8
        elif datatype == DATA_TYPE.INT16_T:
            ctype = ctypes.c_int16
        elif datatype == DATA_TYPE.INT32_T:
            ctype = ctypes.c_int32
        elif datatype == DATA_TYPE.INT64_T:
            ctype = ctypes.c_int64
        elif datatype == DATA_TYPE.UINT32_T:
            ctype = ctypes.c_uint32
        else:
            raise PicoSDKException("Invalid datatype selected for buffer")

        buffer_max = (ctype * samples)()
        buffer_min = (ctype * samples)()

        self._call_attr_function(
            "SetDataBuffers",
            self.handle,
            channel,
            ctypes.byref(buffer_max),
            ctypes.byref(buffer_min),
            samples,
            datatype,
            segment,
            ratio_mode,
            action,
        )

        return buffer_max, buffer_min
    
    # Run functions
    def run_block_capture(self, timebase, samples, pre_trig_percent=50, segment=0) -> int:
        """
        Runs a block capture using the specified timebase and number of samples.

        This sets up the PicoScope to begin collecting a block of data, divided into
        pre-trigger and post-trigger samples. It uses the PicoSDK `RunBlock` function.

        Args:
                timebase (int): Timebase value determining sample interval (refer to PicoSDK guide).
                samples (int): Total number of samples to capture.
                pre_trig_percent (int, optional): Percentage of samples to capture before the trigger. 
                segment (int, optional): Memory segment index to use.

        Returns:
                int: Estimated time (in milliseconds) the device will be busy capturing data.
        """

        pre_samples = int((samples * pre_trig_percent) / 100)
        post_samples = int(samples - pre_samples)
        time_indisposed_ms = ctypes.c_int32()
        self._call_attr_function(
            'RunBlock',
            self.handle,
            pre_samples,
            post_samples,
            timebase,
            ctypes.byref(time_indisposed_ms),
            segment,
            None,
            None
        )
        return time_indisposed_ms.value
    
    def get_enumerated_units(self) -> tuple[int, str, int]:
        """
        Returns count, serials and serial string length of a specific PicoScope unit.

        Returns:
            Number of devices of this type
            Comma separated string of all serials
            Length of string
        """
        string_buffer_length = 256
        count = ctypes.c_int16()
        serials = ctypes.create_string_buffer(string_buffer_length)
        serial_length = ctypes.c_int16(string_buffer_length)
        self._call_attr_function(
            'EnumerateUnits',
            ctypes.byref(count),
            ctypes.byref(serials),
            ctypes.byref(serial_length)
        )
        return count.value, serials.value.decode(), serial_length.value
    
    def get_values(self, samples, start_index=0, segment=0, ratio=0, ratio_mode=RATIO_MODE.RAW) -> int:
        """
        Retrieves a block of captured samples from the device once it's ready.
        If a channel goes over-range a warning will appear.

        This function should be called after confirming the device is ready using `is_ready()`.
        It invokes the underlying PicoSDK `GetValues` function to read the data into memory.

        Args:
                samples (int): Number of samples to retrieve.
                start_index (int, optional): Starting index in the buffer.
                segment (int, optional): Memory segment index to retrieve data from.
                ratio (int, optional): Downsampling ratio.
                ratio_mode (RATIO_MODE, optional): Ratio mode for downsampling. 

        Returns:
                int: Actual number of samples retrieved.
        """

        self.is_ready()
        total_samples = ctypes.c_uint32(samples)
        over_range = ctypes.c_int16()
        self._call_attr_function(
            'GetValues',
            self.handle, 
            start_index,
            ctypes.byref(total_samples),
            ratio,
            ratio_mode,
            segment,
            ctypes.byref(over_range)
        )
        self.over_range = over_range.value
        self.is_over_range()
        return total_samples.value
    
    def is_over_range(self) -> list:
        """
        Logs and prints a warning if any channel has been over range.

        Returns:
            list: List of channels that have been over range
        """

        over_range_channels = [CHANNEL_NAMES[i] for i in range(8) if self.over_range & (1 << i)]
    
        if over_range_channels:
            warnings.warn(
                f"Overrange detected on channels: {', '.join(over_range_channels)}.",
                OverrangeWarning
            )
        return over_range_channels
        
    
    def run_simple_block_capture(self) -> dict:
        raise NotImplementedError("This method is not yet implemented in this PicoScope")
    
    # Siggen Functions
    def _siggen_apply(self, enabled=1, sweep_enabled=0, trigger_enabled=0, 
                     auto_clock_optimise_enabled=0, override_auto_clock_prescale=0) -> dict:
        """
        Sets the signal generator running using parameters previously configured.

        Args:
                enabled (int, optional): SigGen Enabled, 
                sweep_enabled (int, optional): Sweep Enabled,
                trigger_enabled (int, optional): SigGen trigger enabled,
                auto_clock_optimise_enabled (int, optional): Auto Clock Optimisation,
                override_auto_clock_prescale (int, optional): Override Clock Prescale,

        Returns:
                dict: Returns dictionary of the actual achieved values.
        """
        c_frequency = ctypes.c_double()
        c_stop_freq = ctypes.c_double()
        c_freq_incr = ctypes.c_double()
        c_dwell_time = ctypes.c_double()
        self._call_attr_function(
            'SigGenApply',
            self.handle,
            enabled,
            sweep_enabled,
            trigger_enabled,
            auto_clock_optimise_enabled,
            override_auto_clock_prescale,
            ctypes.byref(c_frequency),
            ctypes.byref(c_stop_freq),
            ctypes.byref(c_freq_incr),
            ctypes.byref(c_dwell_time)
        )
        return {'Freq': c_frequency.value,
                'StopFreq': c_stop_freq.value,
                'FreqInc': c_freq_incr.value,
                'dwelltime': c_dwell_time.value}
    
    def _siggen_set_frequency(self, frequency:float) -> None:
        """
        Set frequency of SigGen in Hz.

        Args:
                frequency (int): Frequency in Hz.
        """   
        self._call_attr_function(
            'SigGenFrequency',
            self.handle,
            ctypes.c_double(frequency)
        )

    def _siggen_set_duty_cycle(self, duty:float) -> None:
        """
        Set duty cycle of SigGen in percentage

        Args:
                Duty cycle (int): Duty cycle in %.
        """   
        self._call_attr_function(
            'SigGenWaveformDutyCycle',
            self.handle,
            ctypes.c_double(duty)
        )
    
    def _siggen_set_range(self, pk2pk:float, offset:float=0.0):
        """
        Set mV range of SigGen (6000A).

        Args:
                pk2pk (int): Peak to peak of signal in volts (V).
                offset (int, optional): Offset of signal in volts (V).
        """      
        self._call_attr_function(
            'SigGenRange',
            self.handle,
            ctypes.c_double(pk2pk),
            ctypes.c_double(offset)
        )
    
    def _siggen_set_waveform(self, wave_type: WAVEFORM):
        """
        Set waveform type for SigGen (6000A).

        Args:
                wave_type (WAVEFORM): Waveform type i.e. WAVEFORM.SINE.
        """
        self._call_attr_function(
            'SigGenWaveform',
            self.handle,
            wave_type,
            None,
            None
        )

    def set_siggen(self, *args):
        raise NotImplementedError("Method not yet available for this oscilloscope")



class ps6000a(PicoScopeBase):
    """PicoScope 6000 (A) API specific functions"""
    def __init__(self, *args, **kwargs):
        super().__init__("ps6000a", *args, **kwargs)


    def open_unit(self, serial_number:str=None, resolution:RESOLUTION = 0) -> None:
        """
        Open PicoScope unit.

        Args:
                serial_number (str, optional): Serial number of device.
                resolution (RESOLUTION, optional): Resolution of device.
        """
        super()._open_unit(serial_number, resolution)
        self.min_adc_value, self.max_adc_value =super()._get_adc_limits()

    def memory_segments(self, n_segments: int) -> int:
        """Configure the number of memory segments.

        This wraps the ``ps6000aMemorySegments`` API call.

        Args:
            n_segments: Desired number of memory segments.

        Returns:
            int: Number of samples available in each segment.
        """

        max_samples = ctypes.c_uint64()
        self._call_attr_function(
            "MemorySegments",
            self.handle,
            ctypes.c_uint64(n_segments),
            ctypes.byref(max_samples),
        )
        return max_samples.value

    def memory_segments_by_samples(self, n_samples: int) -> int:
        """Set the samples per memory segment.

        This wraps ``ps6000aMemorySegmentsBySamples`` which divides the
        capture memory so that each segment holds ``n_samples`` samples.

        Args:
            n_samples: Number of samples per segment.

        Returns:
            int: Number of segments the memory was divided into.
        """

        max_segments = ctypes.c_uint64()
        self._call_attr_function(
            "MemorySegmentsBySamples",
            self.handle,
            ctypes.c_uint64(n_samples),
            ctypes.byref(max_segments),
        )
        return max_segments.value

    def query_max_segments_by_samples(
        self,
        n_samples: int,
        n_channel_enabled: int,
    ) -> int:
        """Return the maximum number of segments for a given sample count.

        Wraps ``ps6000aQueryMaxSegmentsBySamples`` to query how many memory
        segments can be configured when each segment stores ``n_samples``
        samples.

        Args:
            n_samples: Number of samples per segment.
            n_channel_enabled: Number of enabled channels.

        Returns:
            int: Maximum number of segments available.

        Raises:
            PicoSDKException: If the device has not been opened.
        """

        if self.resolution is None:
            raise PicoSDKException("Device has not been initialized, use open_unit()")

        max_segments = ctypes.c_uint64()
        self._call_attr_function(
            "QueryMaxSegmentsBySamples",
            self.handle,
            ctypes.c_uint64(n_samples),
            ctypes.c_uint32(n_channel_enabled),
            ctypes.byref(max_segments),
            self.resolution,
        )
        return max_segments.value
    
    def get_timebase(self, timebase:int, samples:int, segment:int=0) -> None:
        """
        This function calculates the sampling rate and maximum number of 
        samples for a given timebase under the specified conditions.

        Args:
                timebase (int): Selected timebase multiplier (refer to programmer's guide).
                samples (int): Number of samples.
                segment (int, optional): The index of the memory segment to use.

        Returns:
                dict: Returns interval (ns) and max samples as a dictionary.
        """

        return super()._get_timebase(timebase, samples, segment)
    
    def set_channel(
        self,
        channel: CHANNEL,
        range: RANGE,
        enabled: bool = True,
        coupling: COUPLING = COUPLING.DC,
        offset: float = 0.0,
        bandwidth: BANDWIDTH_CH = BANDWIDTH_CH.FULL,
        probe_scale: float = 1.0,
    ) -> None:
        """
        Enable/disable a channel and specify certain variables i.e. range, coupling, offset, etc.
        
        For the ps6000a drivers, this combines _set_channel_on/off to a single function. 
        Set channel on/off by adding enabled=True/False

        Args:
                channel (CHANNEL): Channel to setup.
                range (RANGE): Voltage range of channel.
                enabled (bool, optional): Enable or disable channel.
                coupling (COUPLING, optional): AC/DC/DC 50 Ohm coupling of selected channel.
                offset (int, optional): Analog offset in volts (V) of selected channel.
                bandwidth (BANDWIDTH_CH, optional): Bandwidth of channel (selected models).
                probe_scale (float, optional): Probe attenuation factor such as 1 or 10.
        """
        self.probe_scale[channel] = probe_scale

        if enabled:
            super()._set_channel_on(channel, range, coupling, offset, bandwidth)
        else:
            super()._set_channel_off(channel)

    def set_digital_port_on(
        self,
        port: DIGITAL_PORT,
        logic_threshold_level: list[int],
        hysteresis: DIGITAL_PORT_HYSTERESIS,
    ) -> None:
        """Enable a digital port using ``ps6000aSetDigitalPortOn``.

        Args:
            port: Digital port to enable.
            logic_threshold_level: Threshold level for each pin in millivolts.
            hysteresis: Hysteresis level applied to all pins.
        """

        level_array = (ctypes.c_int16 * len(logic_threshold_level))(
            *logic_threshold_level
        )

        self._call_attr_function(
            "SetDigitalPortOn",
            self.handle,
            port,
            level_array,
            len(logic_threshold_level),
            hysteresis,
        )

    def set_digital_port_off(self, port: DIGITAL_PORT) -> None:
        """Disable a digital port using ``ps6000aSetDigitalPortOff``."""

        self._call_attr_function(
            "SetDigitalPortOff",
            self.handle,
            port,
        )

    def set_aux_io_mode(self, mode: AUXIO_MODE) -> None:

        """Configure the AUX IO connector using ``ps6000aSetAuxIoMode``.

        Args:
            mode: Requested AUXIO mode from :class:`~pypicosdk.constants.AUXIO_MODE`.
        """

        self._call_attr_function(
            "SetAuxIoMode",
            self.handle,
            mode,
        )

    def set_simple_trigger(self, channel, threshold_mv, enable=True, direction=TRIGGER_DIR.RISING, delay=0, auto_trigger_ms=5_000):
        """
        Sets up a simple trigger from a specified channel and threshold in mV

        Args:
            channel (int): The input channel to apply the trigger to.
            threshold_mv (float): Trigger threshold level in millivolts.
            enable (bool, optional): Enables or disables the trigger. 
            direction (TRIGGER_DIR, optional): Trigger direction (e.g., TRIGGER_DIR.RISING, TRIGGER_DIR.FALLING). 
            delay (int, optional): Delay in samples after the trigger condition is met before starting capture. 
            auto_trigger_ms (int, optional): Timeout in milliseconds after which data capture proceeds even if no trigger occurs. 
        """
        auto_trigger_us = auto_trigger_ms * 1000
        return super().set_simple_trigger(channel, threshold_mv, enable, direction, delay, auto_trigger_us)

    def set_trigger_channel_conditions(
        self,
        source: int,
        state: int,
        action: int = ACTION.CLEAR_ALL | ACTION.ADD,
    ) -> None:
        """Configure a trigger condition using ``ps6000aSetTriggerChannelConditions``.

        This method mirrors :meth:`PicoScopeBase.set_trigger_channel_conditions` while
        documenting the underlying API call specific to the 6000A series.

        Args:
            source: Input source for the condition as a :class:`CHANNEL` value.
            state: Desired trigger state from :class:`PICO_TRIGGER_STATE`.
            action: How to combine the condition with any existing configuration.
                Defaults to ``ACTION.CLEAR_ALL | ACTION.ADD``.
        """

        super().set_trigger_channel_conditions(source, state, action)

    def set_trigger_channel_properties(
        self,
        threshold_upper: int,
        hysteresis_upper: int,
        threshold_lower: int,
        hysteresis_lower: int,
        channel: int,
        aux_output_enable: int = 0,
        auto_trigger_us: int = 0,
    ) -> None:
        """Configure channel thresholds using ``ps6000aSetTriggerChannelProperties``.

        This method mirrors :meth:`PicoScopeBase.set_trigger_channel_properties` while
        documenting the underlying 6000A API call.

        Args:
            threshold_upper: ADC value for the upper trigger level.
            hysteresis_upper: Hysteresis for ``threshold_upper`` in ADC counts.
            threshold_lower: ADC value for the lower trigger level.
            hysteresis_lower: Hysteresis for ``threshold_lower`` in ADC counts.
            channel: Channel these settings apply to.
            aux_output_enable: Optional auxiliary output flag.
            auto_trigger_us: Auto-trigger timeout in microseconds.
        """

        super().set_trigger_channel_properties(
            threshold_upper,
            hysteresis_upper,
            threshold_lower,
            hysteresis_lower,
            channel,
            aux_output_enable,
            auto_trigger_us,
        )

    def set_trigger_channel_directions(
        self,
        channel: int,
        direction: int,
        threshold_mode: int,
    ) -> None:
        """Configure channel directions using ``ps6000aSetTriggerChannelDirections``."""

        super().set_trigger_channel_directions(channel, direction, threshold_mode)
    
    def set_data_buffer(self, channel:CHANNEL, samples:int, segment:int=0, datatype:DATA_TYPE=DATA_TYPE.INT16_T,
                        ratio_mode:RATIO_MODE=RATIO_MODE.RAW, action:ACTION=ACTION.CLEAR_ALL | ACTION.ADD) -> ctypes.Array:
        """
        Tells the driver where to store the data that will be populated when get_values() is called.
        This function works on a single buffer. For aggregation mode, call set_data_buffers instead.

        Args:
                channel (CHANNEL): Channel you want to use with the buffer.
                samples (int): Number of samples/length of the buffer.
                segment (int, optional): Location of the buffer.
                datatype (DATATYPE, optional): C datatype of the data.
                ratio_mode (RATIO_MODE, optional): Down-sampling mode.
                action (ACTION, optional): Method to use when creating a buffer.

        Returns:
                ctypes.Array: Array that will be populated when get_values() is called.
        """
        return super()._set_data_buffer_ps6000a(channel, samples, segment, datatype, ratio_mode, action)

    def set_data_buffers(
        self,
        channel: CHANNEL,
        samples: int,
        segment: int = 0,
        datatype: DATA_TYPE = DATA_TYPE.INT16_T,
        ratio_mode: RATIO_MODE = RATIO_MODE.AGGREGATE,
        action: ACTION = ACTION.CLEAR_ALL | ACTION.ADD,
    ) -> tuple[ctypes.Array, ctypes.Array]:
        """Configure both maximum and minimum data buffers for a channel.

        Use this when downsampling in aggregation mode or requesting
        post-capture aggregated values. It allocates two buffers - one to hold
        the maximum values and another for the minimum values - and registers
        them with ``ps6000aSetDataBuffers``.

        Args:
            channel (CHANNEL): Channel you want to use with the buffers.
            samples (int): Number of samples/length of each buffer.
            segment (int, optional): Memory segment index for the buffers.
            datatype (DATA_TYPE, optional): C datatype of the data stored in the
                buffers.
            ratio_mode (RATIO_MODE, optional): Downsampling mode. Typically
                ``RATIO_MODE.AGGREGATE`` when both buffers are required.
            action (ACTION, optional): Method used when creating or updating the
                buffers.

        Returns:
            tuple[ctypes.Array, ctypes.Array]: ``(buffer_max, buffer_min)`` that
            will be populated when :meth:`get_values` is called.
        """

        return super()._set_data_buffers_ps6000a(
            channel,
            samples,
            segment,
            datatype,
            ratio_mode,
            action,
        )
    
    def set_data_buffer_for_enabled_channels(self, samples:int, segment:int=0, datatype=DATA_TYPE.INT16_T, 
                                             ratio_mode=RATIO_MODE.RAW) -> dict:
        """
        Sets data buffers for enabled channels set by picosdk.set_channel()

        Args:
            samples (int): The sample buffer or size to allocate.
            segment (int): The memory segment index.
            datatype (DATA_TYPE): The data type used for the buffer.
            ratio_mode (RATIO_MODE): The ratio mode (e.g., RAW, AVERAGE).

        Returns:
            dict: A dictionary mapping each channel to its associated data buffer.
        """
        # Clear the buffer
        super()._set_data_buffer_ps6000a(0, 0, 0, 0, 0, ACTION.CLEAR_ALL)
        channels_buffer = {}
        for channel in self.range:
            channels_buffer[channel] = super()._set_data_buffer_ps6000a(channel, samples, segment, datatype, ratio_mode, action=ACTION.ADD)
        return channels_buffer
    
    def set_siggen(self, frequency:float, pk2pk:float, wave_type:WAVEFORM, offset:float=0.0, duty:float=50) -> dict:
        """Configures and applies the signal generator settings.

        Sets up the signal generator with the specified waveform type, frequency,
        amplitude (peak-to-peak), offset, and duty cycle.

        Args:
            frequency (float): Signal frequency in hertz (Hz).
            pk2pk (float): Peak-to-peak voltage in volts (V).
            wave_type (WAVEFORM): Waveform type (e.g., WAVEFORM.SINE, WAVEFORM.SQUARE).
            offset (float, optional): Voltage offset in volts (V).
            duty (int or float, optional): Duty cycle as a percentage (0–100).

        Returns:
            dict: Returns dictionary of the actual achieved values.
        """
        self._siggen_set_waveform(wave_type)
        self._siggen_set_range(pk2pk, offset)
        self._siggen_set_frequency(frequency)
        self._siggen_set_duty_cycle(duty)
        return self._siggen_apply()
    
    def run_simple_block_capture(
        self,
        timebase: int,
        samples: int,
        segment: int = 0,
        start_index: int = 0,
        datatype: DATA_TYPE = DATA_TYPE.INT16_T,
        ratio: int = 0,
        ratio_mode: RATIO_MODE = RATIO_MODE.RAW,
        pre_trig_percent: int = 50,
    ) -> tuple[dict, list]:
        """Perform a complete single block capture.

        When ``ratio_mode`` is ``RATIO_MODE.TRIGGER`` the driver requires a
        separate buffer to store the trigger samples. This helper allocates an
        additional buffer internally and reads the trigger data before querying
        the trigger time offset.

        Args:
            timebase: PicoScope timebase value.
            samples: Number of samples to capture.
            segment: Memory segment index to use.
            start_index: Starting index in the buffer.
            datatype: Data type to use for the capture buffer.
            ratio: Downsampling ratio.
            ratio_mode: Downsampling mode. If ``RATIO_MODE.TRIGGER`` is
                specified, ``ratio`` is forced to ``1`` for the trigger-data
                retrieval call.
            pre_trig_percent: Percentage of samples to capture before the
                trigger.

        Returns:
            tuple[dict, list]: Dictionary of channel buffers (in mV) and the time
            axis in seconds.

        Examples:
            >>> scope.set_channel(CHANNEL.A, RANGE.V1)
            >>> scope.set_simple_trigger(CHANNEL.A, threshold_mv=500)
            >>> buffers = scope.run_simple_block_capture(timebase=3, samples=1000)
        """

        # Clear data buffers on ps6000a
        super()._set_data_buffer_ps6000a(0, 0, 0, 0, 0, ACTION.CLEAR_ALL)

        # If ratio_mode is TRIGGER, change ratio_mode to RAW
        if ratio_mode == RATIO_MODE.TRIGGER:
            trigger_ratio = ratio or 1
            main_ratio_mode = RATIO_MODE.RAW
            main_ratio = 0
        else:
            trigger_ratio = None
            main_ratio_mode = ratio_mode
            main_ratio = ratio

        # Manually create channels_buffer dependant on ratio mode and action
        channels_buffer: dict = {}
        trigger_buffer: dict | None = {} if trigger_ratio else None
        for ch in self.range:
            buf = super()._set_data_buffer_ps6000a(
                ch,
                samples,
                segment,
                datatype,
                main_ratio_mode,
                action=ACTION.ADD,
            )
            channels_buffer[ch] = buf
            if trigger_buffer is not None:
                tbuf = super()._set_data_buffer_ps6000a(
                    ch,
                    samples,
                    segment,
                    datatype,
                    RATIO_MODE.TRIGGER,
                    action=ACTION.ADD,
                )
                trigger_buffer[ch] = tbuf


        # Start block capture
        self.run_block_capture(timebase, samples, pre_trig_percent, segment)

        # Get values from PicoScope (returning actual samples for time_axis)
        actual_samples = self.get_values(samples, start_index, segment, main_ratio, main_ratio_mode)

        if trigger_buffer is not None:
            self.get_values(samples, 0, segment, trigger_ratio, RATIO_MODE.TRIGGER)

        # Convert from ADC to mV values
        channels_buffer = self.channels_buffer_adc_to_mv(channels_buffer)

        # Generate the time axis based on actual samples and timebase
        time_axis = self.get_time_axis(timebase, actual_samples)

        return channels_buffer, time_axis

    def run_simple_rapid_block_capture(
        self,
        timebase: int,
        samples: int,
        n_captures: int,
        start_index: int = 0,
        datatype: DATA_TYPE = DATA_TYPE.INT16_T,
        ratio: int = 0,
        ratio_mode: RATIO_MODE = RATIO_MODE.RAW,
        pre_trig_percent: int = 50,
    ) -> tuple[dict, list]:
        """Perform a basic rapid block capture.

        If ``ratio_mode`` is ``RATIO_MODE.TRIGGER`` an additional set of data
        buffers is used internally to retrieve the trigger samples. The returned
        waveform data always uses ``RATIO_MODE.RAW``. ``ratio`` is forced to
        ``1`` for the trigger-data retrieval call when required.
        """

        self.memory_segments(n_captures)
        self.set_no_of_captures(n_captures)

        super()._set_data_buffer_ps6000a(0, 0, 0, 0, 0, ACTION.CLEAR_ALL)


        if ratio_mode == RATIO_MODE.TRIGGER:
            trigger_ratio = ratio or 1
            main_ratio_mode = RATIO_MODE.RAW
            main_ratio = 0
        else:
            trigger_ratio = None
            main_ratio_mode = ratio_mode
            main_ratio = ratio

        channels_buffer: dict = {ch: [] for ch in self.range}
        trigger_buffer: dict | None = {ch: [] for ch in self.range} if trigger_ratio else None
        for segment in range(n_captures):
            for ch in self.range:
                buf = super()._set_data_buffer_ps6000a(
                    ch,
                    samples,
                    segment,
                    datatype,
                    main_ratio_mode,
                    action=ACTION.ADD,
                )
                channels_buffer[ch].append(buf)
                if trigger_buffer is not None:
                    tbuf = super()._set_data_buffer_ps6000a(
                        ch,
                        samples,
                        segment,
                        datatype,
                        RATIO_MODE.TRIGGER,
                        action=ACTION.ADD,
                    )
                    trigger_buffer[ch].append(tbuf)

        self.run_block_capture(timebase, samples, pre_trig_percent, 0)

        overflow = ctypes.c_int16()
        actual_samples = self.get_values_bulk(
            start_index,
            samples,
            0,
            n_captures - 1,
            main_ratio,
            main_ratio_mode,
            overflow,
        )

        if trigger_buffer is not None:
            self.get_values_bulk(
                0,
                samples,
                0,
                n_captures - 1,
                trigger_ratio,
                RATIO_MODE.TRIGGER,
                overflow,
            )

        for ch in channels_buffer:
            for i in range(n_captures):
                data_list = self.buffer_ctypes_to_list(channels_buffer[ch][i])
                channels_buffer[ch][i] = self.buffer_adc_to_mv(data_list, ch)

        time_axis = self.get_time_axis(timebase, actual_samples)

        return channels_buffer, time_axis

    
class ps5000a(PicoScopeBase):
    def __init__(self, *args, **kwargs):
        super().__init__("ps5000a", *args, **kwargs)

    def open_unit(self, serial_number=None, resolution=RESOLUTION):
        status = super()._open_unit(serial_number, resolution)
        self.max_adc_value = super()._get_maximum_adc_value()
        return status

    def set_channel(
        self,
        channel,
        range,
        enabled=True,
        coupling=COUPLING.DC,
        offset=0,
        probe_scale: float = 1.0,
    ):
        """Configure an analog channel.

        Args:
            channel: Channel to configure.
            range: Input range for the channel.
            enabled: Enable or disable the channel.
            coupling: Input coupling type.
            offset: Analog offset in volts.
            probe_scale: Probe attenuation factor such as 1 or 10.
        """
        self.probe_scale[channel] = probe_scale
        return super()._set_channel(channel, range, enabled, coupling, offset)
    
    def get_timebase(self, timebase, samples, segment=0):
        return super()._get_timebase_2(timebase, samples, segment)
    
    def set_simple_trigger(self, channel, threshold_mv, enable=True, direction=TRIGGER_DIR.RISING, delay=0, auto_trigger_ms=5000):
        """
        Sets up a simple trigger from a specified channel and threshold in mV

        Args:
            channel (int): The input channel to apply the trigger to.
            threshold_mv (float): Trigger threshold level in millivolts.
            enable (bool, optional): Enables or disables the trigger.
            direction (TRIGGER_DIR, optional): Trigger direction (e.g., TRIGGER_DIR.RISING, TRIGGER_DIR.FALLING).
            delay (int, optional): Delay in samples after the trigger condition is met before starting capture.
            auto_trigger_ms (int, optional): Timeout in milliseconds after which data capture proceeds even if no trigger occurs.
        """
        return super().set_simple_trigger(channel, threshold_mv, enable, direction, delay, auto_trigger_ms)
    
    def set_data_buffer(self, channel, samples, segment=0, ratio_mode=0):
        return super()._set_data_buffer_ps5000a(channel, samples, segment, ratio_mode)
    
    def set_data_buffer_for_enabled_channels(self, samples, segment=0, ratio_mode=0):
        channels_buffer = {}
        for channel in self.range:
            channels_buffer[channel] = super()._set_data_buffer_ps5000a(channel, samples, segment, ratio_mode)
        return channels_buffer
    
    def change_power_source(self, state):
        return super()._change_power_source(state)
