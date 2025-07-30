"""
Copyright 2022 DevBuildZero, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

import vxi11
import threading
import time
import numpy as np

from power_supply_manager.logger import logger

BUF_SIZE = 120


class Channel:
    def __init__(self, channel_num: int):
        self.num: int = channel_num
        self.name: str = ""
        self.output_on: bool = False
        self.voltage_set: float = 0.0
        self.voltage_meas: float = 0.0
        self.current_set: float = 0.0
        self.current_meas: float = 0.0
        self.sense_meas: bool = False
        self.voltage_buffer = np.zeros(BUF_SIZE)
        self.current_buffer = np.zeros(BUF_SIZE)

        # For power sequencing
        self.seq_on: int = -1
        self.seq_off: int = -1


class PowerSupply:
    def __init__(self, host: str, ps_num: int, num_channels: int):
        self.num: int = ps_num
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._bg_updater)
        self.host: str = host
        self.step_count = 0  # Measurement counter
        self.sample_rate = 1

        # Connect to instrument and read ID
        self.instr = vxi11.Instrument(host)
        self.instr.timeout = 2
        self.idn = self.read("*IDN?")
        logger.info(f"Connected to instrument (host {host}):\n\t{self.idn}")

        self.channels = [Channel(i) for i in range(1, num_channels + 1)]
        # Create channel query string of the form @(1,2,3)
        self.all_channels: str = (
            f"(@{','.join([str(i) for i in range(1, num_channels+1)])})"
        )
        self.init_done: bool = False

        # Start background updater thread
        self.thread.start()

    def close(self):
        """Destructor to ensure the background thread is stopped"""
        # Close the instrument connection
        self.lock.acquire()
        if self.thread.is_alive():
            logger.debug("Stopping background updater thread...")
            self.thread.join(timeout=1)
            del self.thread
        self.lock.release()
        del self.instr
        logger.info(f"Closed connection to {self.host} power supply.")

    def _bg_updater(self):
        """Background thread loop"""
        while True:
            self.read_values()
            time.sleep(self.sample_rate)
            self.init_done = True

    def connect(self) -> None:
        """Connect to instrument"""
        self.instr = vxi11.Instrument(self.host)

    def configure(self, config: dict) -> None:
        """Set instrument registers based on the provided dict of values"""
        logger.debug("Setting PS configuration...")
        for i, ch_cfg in enumerate(config.get("channels")):
            ch = self.channels[i]
            logger.info(f"Loading configuration for {self.host} channel {ch.num}...")
            if name := ch_cfg.get("name"):
                logger.info(f"Setting channel name to {name}")
                ch.name = name
            if (voltage := ch_cfg.get("voltage")) and voltage != ch.voltage_set:
                logger.info(
                    f"Changing voltage from {ch.voltage_set} to {voltage} (making sure output is off first)"
                )
                self.set_output_state(i + 1, False)
                self.set_voltage(i + 1, voltage)
            if (current := ch_cfg.get("current")) and current != ch.current_set:
                logger.info(
                    f"Changing current from {ch.current_set} to {current} (making sure output is off first)"
                )
                self.set_output_state(i + 1, False)
                self.set_current(i + 1, current)
            # if (ovp := ch_cfg.get("ovp")) and ovp != ch.ovp_set:
            #     logger.info(f"Changing OVP from {ch.ovp_set} to {ovp}")
            #     self.set_ovp(i + 1, ovp)
            # if (ovp_on := ch_cfg.get("ovp_on")) and ovp_on != ch.ovp_on:
            #     logger.info(f"Changing OVP state from {ch.ovp_on} to {ovp_on}")
            #     self.set_ovp_state(i + 1, ovp_on)
            # if (ocp := ch_cfg.get("ocp")) and ocp != ch.ocp_set:
            #     logger.info(f"Changing OCP from {ch.ocp_set} to {ocp}")
            #     self.set_ocp(i + 1, ocp)
            # if (ocp_on := ch_cfg.get("ocp_on")) and ocp_on != ch.ocp_on:
            #     logger.info(f"Changing OCP state from {ch.ocp_on} to {ocp_on}")
            #     self.set_ocp_state(i + 1, ocp_on)
            if (seq_on := ch_cfg.get("seq_on")) and seq_on != ch.seq_on:
                logger.info(f"Changing sequence on state from {ch.seq_on} to {seq_on}")
                ch.seq_on = seq_on
            if (seq_off := ch_cfg.get("seq_off")) and seq_off != ch.seq_off:
                logger.info(
                    f"Changing sequence off state from {ch.seq_off} to {seq_off}"
                )
                ch.seq_off = seq_off

    def read(self, command: str) -> str:
        """Perform an instrument read operation (write and then read) with the provided command"""
        self.lock.acquire()
        try:
            resp = str(self.instr.ask(command))
        except:
            logger.error(f"Read operation failed for device {self.host}: {command}")
            resp = ""
        self.lock.release()
        return resp

    def write(self, command: str) -> None:
        """Perform an instrument write operation (no read after write) with the provided command"""
        self.lock.acquire()
        try:
            str(self.instr.write(command))
        except:
            logger.error(f"Write operation failed for device {self.host}: {command}")
        self.lock.release()

    def update_measurement_buffer(self) -> None:
        """Stores measurements in buffers for plotting"""
        if self.step_count <= BUF_SIZE:
            for ch in self.channels:
                ch.voltage_buffer[self.step_count - 1] = ch.voltage_meas
                ch.current_buffer[self.step_count - 1] = ch.current_meas
        else:
            # Roll buffer 1 frame and replace last frame with new
            for ch in self.channels:
                ch.voltage_buffer = np.roll(ch.voltage_buffer, -1)
                ch.voltage_buffer[-1] = ch.voltage_meas
                ch.current_buffer = np.roll(ch.current_buffer, -1)
                ch.current_buffer[-1] = ch.current_meas

    def read_values(self) -> None:
        """Read state of instrument registers"""
        try:
            self.step_count += 1
            # Read values from supply
            s = str(self.read(f"output:state? {self.all_channels}")).split(",")
            vs, cs = str(
                self.read(
                    f"source:voltage? {self.all_channels}; current? {self.all_channels}"
                )
            ).split(";")
            vm, cm = str(
                self.read(
                    f"measure:voltage? {self.all_channels}; current? {self.all_channels}"
                )
            ).split(";")
            sense_mode = str(self.read(f"source:voltage:sense? {self.all_channels}"))

            vs = vs.split(",")  # Convert str to list
            cs = cs.split(",")
            vm = vm.split(",")
            cm = cm.split(",")
            sense_mode = sense_mode.split(",")

            # Write values to channel object
            for i, ch in enumerate(self.channels):
                ch.output_on = True if int(s[i]) else False
                ch.voltage_set = float(vs[i])
                ch.current_set = float(cs[i])
                ch.voltage_meas = float(vm[i])
                ch.current_meas = float(cm[i])
                ch.sense_meas = True if "ext" in sense_mode[i].lower() else False

            self.update_measurement_buffer()
        except:
            logger.error("Connection to instrument failed. Attempting to reconnect...")
            self.connect()

    def set_output_state(self, channel_num: int, on: bool) -> None:
        self.write(f"output:state {int(on)}, (@{channel_num})")

    def group_power_state(self, channels: list[int], on: bool) -> None:
        self.write(f"output:state {int(on)}, (@{','.join(str(i) for i in channels)})")

    def set_voltage(self, channel_num: int, voltage: float) -> None:
        self.write(f"source:voltage {voltage}, (@{channel_num})")

    def set_current(self, channel_num: int, current: float) -> None:
        self.write(f"source:current {current}, (@{channel_num})")

    def toggle_4wire(self, channel_num: int) -> None:
        """Enable or disable 4-wire sense mode for the specified channel"""
        ch = self.channels[channel_num - 1]
        on = not ch.sense_meas  # Toggle sense mode
        self.write(f"source:voltage:sense {'EXT' if on else 'INT'}, (@{channel_num})")

    def channel_query(self, channels: list[int]) -> str:
        return f"(@{','.join([str(i) for i in channels])})"

    def clear_latchup(
        self, channel_num: int, v_step_size: float = 0.1, step_interval_s: float = 0.5
    ) -> None:
        """Clear latchup state for the specified channel"""
        ch = self.channels[channel_num - 1]

        # Step down channel voltage by intervals until either the latchup is cleared
        # (i.e. the current < current_limit) or we reach 0V
        original_voltage = ch.voltage_set
        while True:
            if ch.current_meas < ch.current_set * 0.9:
                logger.info(
                    f"Latchup cleared for channel {channel_num} at voltage {ch.voltage_set}. Returning to original voltage {original_voltage} V."
                )
                # Restore original voltage
                ch.voltage_set = original_voltage
                self.set_voltage(channel_num, ch.voltage_set)
                break

            if ch.voltage_set <= 0:
                logger.warning(
                    f"Unable to clear latchup for channel {channel_num}, reached 0V. Returning to original voltage {original_voltage} V."
                )
                ch.voltage_set = original_voltage
                self.set_voltage(channel_num, ch.voltage_set)
                break

            ch.voltage_set -= v_step_size
            self.set_voltage(channel_num, ch.voltage_set)
            time.sleep(step_interval_s)
            self.read_values()

    def power_cycle_channel(self, channel_num: int, cycle_time_s: float = 1.0) -> None:
        """Power cycle the specified channel"""
        self.set_output_state(channel_num, False)
        time.sleep(cycle_time_s)
        self.set_output_state(channel_num, True)
