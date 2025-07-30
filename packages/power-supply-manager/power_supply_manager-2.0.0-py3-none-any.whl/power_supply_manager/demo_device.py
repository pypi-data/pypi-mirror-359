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

import threading
import time
import random
import numpy as np

from power_supply_manager.logger import logger

BUF_SIZE = 120


class DemoChannel:
    def __init__(self, channel_num: int, noise_level: float = 0.01):
        self.num: int = channel_num
        self.name: str = ""
        self.output_on: bool = False
        self.voltage_set: float = 5.0
        self.voltage_meas: float = 0.0
        self.current_set: float = 0.5
        self.current_meas: float = 0.0
        self.sense_meas: bool = False
        self.voltage_buffer = np.zeros(BUF_SIZE)
        self.current_buffer = np.zeros(BUF_SIZE)
        self.base_current = random.uniform(0.1, max(0.1, self.current_set - 0.1))
        self.noise_level = noise_level
        self.shorted: bool = False

        # For power sequencing
        self.seq_on: int = -1
        self.seq_off: int = -1


class DemoPowerSupply:
    def __init__(self, host: str, ps_num: int, num_channels: int):
        self.num = ps_num
        self.lock = threading.Lock()
        self.thread = threading.Thread(target=self._bg_updater)
        self.host: str = host
        self.step_count = 0  # Measurement counter
        self.sample_rate = 1

        self.idn: str = "Demo Power Supply Device"
        logger.info(f"Connected to instrument (host {host}):\n\t{self.idn}")

        self.channels = [DemoChannel(i) for i in range(1, num_channels + 1)]
        self.init_done: bool = False

        # Start background updater thread
        self.thread.start()

    def close(self):
        """Destructor to ensure the background thread is stopped"""
        if self.thread.is_alive():
            logger.debug("Stopping background updater thread...")
            self.thread.join(timeout=1)
            if self.thread.is_alive():
                logger.warning("Background updater thread did not stop in time!")
        logger.info(f"Closed connection to {self.host} power supply.")
        self.init_done = False

    def _bg_updater(self):
        """Background thread loop"""
        while True:
            self.read_values()
            time.sleep(self.sample_rate)
            self.init_done = True

    def configure(self, config: dict) -> None:
        """Set instrument registers based on the provided dict of values"""
        logger.debug("Setting PS configuration...")
        for i, ch_cfg in enumerate(config.get("channels")):
            ch = self.channels[i]
            logger.info(f"Loading configuration for {self.host} channel {ch.num}...")
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
            if (ovp := ch_cfg.get("ovp")) and ovp != ch.ovp_set:
                logger.info(f"Changing OVP from {ch.ovp_set} to {ovp}")
                self.set_ovp(i + 1, ovp)
            if (ovp_on := ch_cfg.get("ovp_on")) and ovp_on != ch.ovp_on:
                logger.info(f"Changing OVP state from {ch.ovp_on} to {ovp_on}")
                self.set_ovp_state(i + 1, ovp_on)
            if (ocp := ch_cfg.get("ocp")) and ocp != ch.ocp_set:
                logger.info(f"Changing OCP from {ch.ocp_set} to {ocp}")
                self.set_ocp(i + 1, ocp)
            if (ocp_on := ch_cfg.get("ocp_on")) and ocp_on != ch.ocp_on:
                logger.info(f"Changing OCP state from {ch.ocp_on} to {ocp_on}")
                self.set_ocp_state(i + 1, ocp_on)
            if (seq_on := ch_cfg.get("seq_on")) and seq_on != ch.seq_on:
                logger.info(f"Changing sequence on state from {ch.seq_on} to {seq_on}")
                ch.seq_on = seq_on
            if (seq_off := ch_cfg.get("seq_off")) and seq_off != ch.seq_off:
                logger.info(
                    f"Changing sequence off state from {ch.seq_off} to {seq_off}"
                )
                ch.seq_off = seq_off

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
        self.step_count += 1

        # Simulate instrument readings based on state
        for ch in self.channels:
            if ch.output_on:
                ch.voltage_meas = ch.voltage_set - 0.01
                if "short" in ch.name.lower() and not ch.shorted:
                    ch.shorted = True
                    logger.info(
                        f"Special name handling for channel name - shorting current"
                    )
                    ch.current_meas = ch.current_set
                elif not "short" in ch.name.lower():
                    ch.current_meas = ch.base_current + random.uniform(
                        -ch.noise_level, ch.noise_level
                    )
            else:
                ch.voltage_meas = 0.0
                ch.current_meas = 0.0
        self.update_measurement_buffer()

    def set_output_state(self, channel_num: int, on: bool) -> None:
        self.channels[channel_num - 1].output_on = on

    def group_power_state(self, channels: list[int], on: bool) -> None:
        for channel in channels:
            self.channels[channel - 1].output_on = on

    def set_voltage(self, channel_num: int, voltage: float) -> None:
        self.channels[channel_num - 1].voltage_set = voltage

    def set_current(self, channel_num: int, current: float) -> None:
        self.channels[channel_num - 1].current_set = current

    def toggle_4wire(self, channel_num: int) -> None:
        ch = self.channels[channel_num - 1]
        ch.sense_meas = not ch.sense_meas

    def clear_latchup(
        self, channel_num: int, v_step_size: float = 0.1, step_interval_s: float = 0.5
    ) -> None:
        """Clear latchup state for the specified channel"""
        pass

    def power_cycle_channel(self, channel_num: int, cycle_time_s: float = 1.0) -> None:
        """Power cycle the specified channel"""
        self.set_output_state(channel_num, False)
        time.sleep(cycle_time_s)
        self.set_output_state(channel_num, True)
