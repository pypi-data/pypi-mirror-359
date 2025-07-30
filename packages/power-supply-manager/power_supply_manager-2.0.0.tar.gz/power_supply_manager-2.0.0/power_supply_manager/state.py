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

import json
import os
import time
import csv
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt
import dearpygui.dearpygui as dpg

from power_supply_manager.device import PowerSupply, BUF_SIZE
from power_supply_manager.demo_device import DemoPowerSupply
from power_supply_manager.logger import logger

VOLTAGE_TOL_PCT = 0.10
CURRENT_TOL_PCT = 0.10


class GuiState:
    """Stores state variables for the application"""

    def __init__(self):
        self.timer = Timer()
        self.theme = GuiTheme()
        # Initialize an empty array to hold PowerSupply objects
        self.supplies = [None] * 10
        self.hosts = [None] * 10
        self.config: dict = {}
        self.groups = []
        # Holds value of Channels input box before PS is created
        self.channels_input = []
        # Used for saving config files
        self.config_filename = "my_config"
        # Data logging
        self.file_handle = None
        self.csv = None
        self.filename_prefix = None
        # Latchup config
        self.latchup_mode = False
        self.current_limit_reset = False
        self.reset_cycle_time_s = 1.0
        self.power_cycle_events = 0
        self.last_power_cycle_time = None

        self.font_registry_set = False
        # Store channel names from config for later use
        self.channel_names_from_config = {}

    def load_font_registry(self):
        if not self.font_registry_set:
            with dpg.font_registry():
                try:
                    self.large_font = dpg.add_font(
                        "./static/OpenSans-Bold.ttf", 28, tag="_large_font"
                    )
                except Exception:
                    # Try fallback path
                    self.large_font = dpg.add_font(
                        "./_internal/static/OpenSans-Bold.ttf", 28, tag="_large_font"
                    )
        self.font_registry_set = True

    def help(self, message):
        """Creates a GUI tooltip dialog for the last_item"""
        last_item = dpg.last_item()
        group = dpg.add_group(horizontal=True)
        dpg.move_item(last_item, parent=group)
        with dpg.tooltip(last_item):
            dpg.add_text(self._split_message(message))

    def _split_message(self, message: str, max_line_length=50) -> str:
        """Splits a tooltip message into multiple lines"""
        if len(message) > max_line_length:
            message = "\n".join(
                message[i : i + max_line_length]
                for i in range(0, len(message), max_line_length)
            )
        return message

    def load_config(self, filepath: str) -> None:
        """Loads device configuration from file and removes any existing devices"""
        logger.debug(f"Deleting existing supplies...")
        self.channels_input.clear()
        # Delete all existing supplies
        for i in range(1, len(self.supplies) + 1):
            self._delete_supply(i)
            if dpg.does_item_exist(f"ps{i}"):
                dpg.delete_item(f"ps{i}")
        logger.debug(f"Loading configuration state...")
        # Read config from file
        with open(filepath, "r") as json_file:
            self.config = json.load(json_file)

        # Store channel names from config for later use
        self.channel_names_from_config = {}
        for ps_idx, ps_cfg in enumerate(self.config):
            if "channels" in ps_cfg:
                for ch_idx, ch_cfg in enumerate(ps_cfg["channels"]):
                    name = ch_cfg.get("name", "")
                    self.channel_names_from_config[(ps_idx + 1, ch_idx + 1)] = name

        # Create new PS headers
        for i in range(len(self.config)):
            self.hosts[i] = self.config[i].get("host")
            self.add_ps_header()

        # Set channel names from config if GUI items already exist
        for (ps_id, ch_id), name in self.channel_names_from_config.items():
            tag = f"p{ps_id}c{ch_id}_name"
            if dpg.does_item_exist(tag):
                dpg.set_value(tag, name)
                # Also update the channel object if it exists
                ps = self.supplies[ps_id - 1]
                if ps and ch_id - 1 < len(ps.channels):
                    ps.channels[ch_id - 1].name = name

    def start_logging(self) -> None:
        """Logs measurements to CSV file. Format:
        CSV(timestamp, PS<num> CH<num> <name>, ...
             <time>, <voltage>, <current>
        """
        logger.debug(f"Entering start_logging callback...")
        datestamp = str(datetime.now().isoformat()).replace(":", "-")
        # Close existing handle, if open, and open new one
        self.stop_logging()
        if self.log_prefix:
            filename = f"{self.filename_prefix}_{datestamp}.csv"
        else:
            filename = f"{datestamp}.csv"
        self.file_handle = open(filename, "w", newline="")
        self.csv = csv.writer(self.file_handle)

        # Write header row
        header_row = ["Datestamp"]
        for ps in self.supplies:
            if ps:
                for ch in ps.channels:
                    prefix = f"PS{ps.num} CH{ch.num} {ch.name}".strip()
                    header_row.append(prefix + " Voltage")
                    header_row.append(prefix + " Current")
        self.csv.writerow(header_row)

    def stop_logging(self) -> None:
        """Stops CSV measurement logging"""
        logger.debug(f"Entering stop_logging callback...")
        if self.file_handle:
            filename = self.file_handle.name
            self.file_handle.close()
            self.file_handle = None
            self.csv = None
            # Save CSV to plot
            self.plot_log_file(filename, save=True, show=False)

    def log_prefix(self, sender, app_data, user_data) -> None:
        """Callback to append a text prefix to log CSV filenames"""
        logger.debug(f"Entering log_prefix callback...")
        self.filename_prefix = app_data

    def config_selection(self, sender, app_data, user_data) -> None:
        """Callback to select configuration file path to load from"""
        logger.debug(f"Entering config_selection callback...")
        self.load_config(app_data.get("file_path_name"))

    def store_config_filename(self, sender, app_data, user_data) -> None:
        """Callback to select configuration file path to save to"""
        logger.debug(f"Entering store_config_filename callback...")
        self.config_filename = dpg.get_value(sender)

    def set_current_limit_reset(self, sender, app_data, user_data) -> None:
        """Callback to reset all channels when latchup is detected"""
        logger.debug(f"Entering current_limit_reset callback...")
        self.current_limit_reset = dpg.get_value(sender)
        if self.current_limit_reset:
            logger.info("Current limit reset enabled.")
        else:
            logger.info("Current limit reset disabled.")

    def set_current_limit_cycle_time(self, sender, app_data, user_data) -> None:
        """Callback to set the latchup cycle time"""
        logger.debug(f"Entering set_latchup_cycle_time callback...")
        try:
            self.reset_cycle_time_s = float(dpg.get_value(sender))
            logger.info(f"Latchup cycle time set to {self.reset_cycle_time_s} s")
        except ValueError:
            logger.error("Invalid latchup cycle time value. Must be a float.")

    def toggle_4wire(self, sender, app_data, user_data) -> None:
        """Callback to toggle 4-wire sense mode for the provided channel"""
        logger.debug(f"Entering toggle_4wire callback...")
        assert len(user_data) == 2
        ps_num = user_data[0]
        channel_num = user_data[1]
        ps = self.supplies[ps_num - 1]
        if ps:
            ps.toggle_4wire(channel_num)

    def _add_latchup_button(self, ps_id, channel):
        """Adds a latchup button to an existing channel if not present."""
        theme_tag = f"p{ps_id}c{channel}_latchup_btn"
        button_tag = f"p{ps_id}c{channel}_latchup"
        parent_tag = f"p{ps_id}c{channel}_sense"
        if not dpg.does_item_exist(button_tag):
            self._create_btn_theme(theme_tag, self.theme.orange)
            # Find the parent child_window for this channel
            # The sense button is always present, so we can use its parent
            parent = dpg.get_item_parent(parent_tag)
            if parent is not None and parent != 0:
                dpg.add_spacer(
                    width=15, parent=parent, tag=f"p{ps_id}c{channel}_latchup_spacer"
                )
                dpg.add_text(
                    "Latchup:", parent=parent, tag=f"p{ps_id}c{channel}_latchup_text"
                )
                dpg.add_button(
                    label="Clear",
                    width=40,
                    tag=button_tag,
                    callback=self.clear_latchup,
                    user_data=(ps_id, channel),
                    parent=parent,
                )
                dpg.bind_item_theme(button_tag, theme_tag)
            else:
                logger.warning(
                    f"Parent item for tag '{parent_tag}' not found. Cannot add latchup button."
                )

    def toggle_latchup_toolbar(self) -> None:
        """Callback to show the latchup toolbar"""
        logger.debug(f"Entering toggle_latchup_toolbar callback...")
        if self.latchup_mode:
            self.latchup_mode = False
            if dpg.does_item_exist("_latchup_group"):
                dpg.delete_item("_latchup_group")
            if dpg.does_item_exist("_latchup_toolbar"):
                dpg.delete_item("_latchup_toolbar")
            # Remove all latchup buttons from existing supplies/channels
            for ps_idx, ps in enumerate(self.supplies, start=1):
                if ps:
                    for ch_idx in range(1, len(ps.channels) + 1):
                        button_tag = f"p{ps_idx}c{ch_idx}_latchup"
                        if dpg.does_item_exist(button_tag):
                            dpg.delete_item(button_tag)

                        text_tag = f"p{ps_idx}c{ch_idx}_latchup_text"
                        if dpg.does_item_exist(text_tag):
                            dpg.delete_item(text_tag)

                        theme_tag = f"p{ps_idx}c{ch_idx}_latchup_btn"
                        if dpg.does_item_exist(theme_tag):
                            dpg.delete_item(theme_tag)

                        spacer_tag = f"p{ps_idx}c{ch_idx}_latchup_spacer"
                        if dpg.does_item_exist(spacer_tag):
                            dpg.delete_item(spacer_tag)
        else:
            self.latchup_mode = True
            # Add latchup buttons to all existing supplies/channels
            for ps_idx, ps in enumerate(self.supplies, start=1):
                if ps:
                    for ch_idx in range(1, len(ps.channels) + 1):
                        self._add_latchup_button(ps_idx, ch_idx)
            # if dpg.does_item_exist("_latchup_toolbar"):
            #     dpg.delete_item("_latchup_toolbar")
            with dpg.collapsing_header(
                label="Latchup Toolbar",
                tag="_latchup_toolbar",
                default_open=True,
                parent="_primary_wnd",
            ):
                with dpg.group(horizontal=True, tag="_latchup_group"):
                    with dpg.child_window(width=900, height=42):
                        with dpg.group(horizontal=True):
                            dpg.add_text("Current Limit Reset:")
                            self.help(
                                "Reset all channels when current limit breach detected. This will power cycle all active channels."
                            )
                            dpg.add_checkbox(
                                label="",
                                tag="_current_limit_reset",
                                default_value=False,
                                callback=self.set_current_limit_reset,
                            )
                            dpg.add_spacer(width=10)
                            dpg.add_text("Power Cycle Time:")
                            self.help(
                                "Time to wait before resetting channels after current limit breach detected [s]."
                            )
                            dpg.add_input_text(
                                default_value="1.0",
                                width=40,
                                tag="_current_limit_cycle_time",
                                callback=self.set_current_limit_cycle_time,
                                on_enter=True,
                            )
                            dpg.add_spacer(width=10)
                            dpg.add_text("Power Cycle Events:")
                            self.help(
                                "Count of power cycle evenst (and time of the event). This is updated when a current limit breach is detected."
                            )
                            dpg.add_text(
                                "0",
                                tag="_last_power_cycle_event",
                            )

    def clear_latchup(self, sender, app_data, user_data) -> None:
        """Callback to clear latchup state for the provided channel"""
        logger.debug(f"Entering clear_latchup callback...")
        assert len(user_data) == 2
        ps_num = user_data[0]
        channel_num = user_data[1]
        ps = self.supplies[ps_num - 1]
        if ps:
            ch = ps.channels[channel_num - 1]
            logger.info(
                f"Clearing latchup state for PS{ps_num} CH{channel_num} {ch.name}"
            )
            ps.clear_latchup(channel_num)
            # Update last power cycle event
            self.power_cycle_events += 1
            self.last_power_cycle_time = datetime.now()

    def check_for_power_cycle(self) -> None:
        # Iterate through all supplies and channels to check for a current limit breach. Keep track of which channels are currently powered on.
        # If a breach is detected on any channel, power cycle all active channels.
        active_channels = []
        need_to_power_cycle = False
        for ps in self.supplies:
            if not ps:
                continue

            for channel in ps.channels:
                if channel.output_on:
                    active_channels.append((ps.num, channel.num))

                if channel.current_meas >= channel.current_set * (1 - CURRENT_TOL_PCT):
                    logger.warning(
                        f"Current limit exceeded on {ps.host} channel {channel.num}"
                    )
                    need_to_power_cycle = True

        if need_to_power_cycle:
            logger.info(
                f"Current limit breach detected. Power cycling all active channels."
            )
            self.power_cycle_events += 1
            self.last_power_cycle_time = datetime.now()

            # Power cycle all active channels
            for supply_num, channel_num in active_channels:
                ps = self.supplies[supply_num - 1]
                if ps:
                    ps.set_output_state(channel_num, False)
            time.sleep(self.reset_cycle_time_s)
            for supply_num, channel_num in active_channels:
                ps = self.supplies[supply_num - 1]
                if ps:
                    ps.set_output_state(channel_num, True)

    def plot_log_callback(self, sender, app_data, user_data) -> None:
        """Callback to plot log CSV file selected by user"""
        logger.debug(f"Entering plot_log_file callback...")
        self.plot_log_file(app_data.get("file_path_name"), save=True, show=False)

    def plot_log_file(
        self, filepath: str, save: bool = True, show: bool = False
    ) -> None:
        import pandas as pd

        df = pd.read_csv(filepath)
        df["Datestamp"] = pd.to_datetime(
            df["Datestamp"], format="%Y-%m-%dT%H-%M-%S.%f", errors="coerce"
        )
        # Split dataframes between Voltage and Current
        dfs = {
            i: df.filter(like=i)
            for i in df.columns.str.split(" ").str[-1]
            if i != "Datestamp"
        }
        _, axes = plt.subplots(nrows=2, ncols=1, sharex=True)
        axes[-1].set_xlabel("Time (s)")
        cnt = 0
        for title, d in dfs.items():
            # Cut off PS# and CH# from legend titles, if a channel name was added
            # PS1 CH1 Voltage
            d = d.copy(deep=True)
            d.rename(
                columns=lambda x: (
                    x if x == "Datestamp" else (x[8:-7] if len(x) > 16 else x[:-7])
                ),
                inplace=True,
            )
            d["Datestamp"] = df["Datestamp"]
            ax = d.plot(x="Datestamp", ax=axes[cnt])
            ax.set_ylabel(title)
            cnt += 1
        plt.tight_layout()
        if show:
            plt.show()
        if save:
            filestem = os.path.splitext(filepath)[0]
            plt.savefig(f"{filestem}.png")
            print(f"Saved plot log to {filestem}.png")
        plt.close()

    def dump_config(self, sender, app_data, user_data) -> None:
        """Dumps current configuration of devices in JSON format"""
        logger.debug(f"Entering dump_config callback...")
        filename = self.config_filename
        if not filename.endswith(".json"):
            filename = filename + ".json"
        filepath = os.path.join(app_data.get("file_path_name"), filename)
        config = []
        for ps in self.supplies:
            if ps:
                channels = []
                for ch in ps.channels:
                    channels.append(
                        {
                            "name": ch.name,
                            "voltage": ch.voltage_set,
                            "current": ch.current_set,
                            # "ovp": ch.ovp_set,
                            # "ocp": ch.ocp_set,
                            # "ovp_on": ch.ovp_on,
                            # "ocp_on": ch.ocp_on,
                            "seq_on": ch.seq_on,
                            "seq_off": ch.seq_off,
                        }
                    )
                config.append({"host": ps.host, "channels": channels})

        with open(filepath, "w") as json_file:
            json.dump(config, json_file)

    def on_gui_close(self, sender, app_data, user_data) -> None:
        """Callback for closing GUI"""
        logger.debug(f"Entering on_gui_close callback...")
        dpg.delete_item(sender)

    def all_on(self) -> None:
        """Powers on all channels of all supplies"""
        logger.debug(f"Entering all_on callback...")
        for supply in self.supplies:
            if supply:
                supply.group_power_state([ch.num for ch in supply.channels], True)

    def all_off(self) -> None:
        """Power off all channels of all supplies"""
        logger.debug(f"Entering all_off callback...")
        for supply in self.supplies:
            if supply:
                supply.group_power_state([ch.num for ch in supply.channels], False)

    def group_on(self) -> None:
        """Power on all Grouped channels"""
        logger.debug(f"Entering group_on callback...")
        self._group_control(power_on=True)

    def group_off(self) -> None:
        """Power off all Grouped channels"""
        logger.debug(f"Entering group_off callback...")
        self._group_control(power_on=False)

    def _group_control(self, power_on: bool) -> None:
        """Sets power state of all Grouped channels"""
        # Build query strings for each supply
        for supply in self.supplies:
            if supply:
                channels = []
                for t in self.groups:
                    if t[0] == supply.num:
                        channels.append(t[1])
                supply.group_power_state(channels, power_on)

    def sequence_on(self):
        """Begins power on sequence for sequenced channels"""
        logger.debug(f"Entering sequence_on callback...")
        self._sequence_control(power_on=True)

    def sequence_off(self):
        """Begins power off sequence for sequenced channels"""
        logger.debug(f"Entering sequence_off callback...")
        self._sequence_control(power_on=False)

    def _sequence_control(self, power_on: bool):
        """Executes power sequencing for sequenced channels"""
        # Build query strings for each supply
        logger.info(f"Beginning power {'on' if power_on else 'off'} sequence...")
        # Find max sequence delay
        max_delay = 0
        for supply in self.supplies:
            if supply and supply.channels:
                channels = []
                for ch in supply.channels:
                    if power_on and ch.seq_on > 0:
                        max_delay = ch.seq_on if ch.seq_on > max_delay else max_delay
                    elif not power_on and ch.seq_off > 0:
                        max_delay = ch.seq_off if ch.seq_off > max_delay else max_delay
        # Perform power sequence
        for i in range(max_delay + 1):
            for supply in self.supplies:
                if supply:
                    channels = []
                    for ch in supply.channels:
                        if power_on and ch.seq_on == i:
                            channels.append(ch.num)
                        elif not power_on and ch.seq_off == i:
                            channels.append(ch.num)
                    if channels:
                        logger.info(
                            f"Sequence step {i} / {max_delay}: Powering {'on' if power_on else 'off'} supply {supply.num} channels {channels}"
                        )
                        supply.group_power_state(channels, power_on)
            time.sleep(1)

    def add_ps_header(self) -> None:
        """Adds a GUI header for a new supply"""
        logger.debug(f"Entering add_ps_header callback...")
        id = len(self.channels_input) + 1
        # Get num_channels from config if it exists
        if self.config and self.config[id - 1]:
            default_num_channels = len(self.config[id - 1].get("channels"))
        else:
            default_num_channels = 2
        default_host = self.hosts[id - 1] if self.hosts[id - 1] else "demo"
        self.channels_input.append(default_num_channels)
        self.hosts[id - 1] = default_host
        channels_tag = f"ps{id}_num_channels"
        with dpg.collapsing_header(
            label=f"Power Supply {id}",
            default_open=True,
            parent="_primary_wnd",
            tag=f"ps{id}",
        ):
            with dpg.group(horizontal=True):
                dpg.add_text("Host / IP:")
                self.help("Hostname or IP address of the supply.")
                dpg.add_input_text(
                    default_value=default_host,
                    width=150,
                    callback=self.set_host,
                    user_data=id,
                )
                dpg.add_text("Channels:")
                self.help("Number of power supply channels to use.")
                dpg.add_input_text(
                    default_value=str(default_num_channels),
                    width=30,
                    tag=channels_tag,
                    callback=self.set_channels,
                    user_data=id,
                )
                dpg.add_button(
                    label="Connect",
                    callback=self.connect,
                    tag=f"ps{id}_connect",
                )

    def add_channels(self, ps_id: int, num_channels: int) -> None:
        """Add child windows to a power supply header for the provided number of channels"""
        logger.debug(f"Entering add_channels callback...")
        self.load_font_registry()
        box_height = 187
        with dpg.tab_bar(parent=f"ps{ps_id}", tag=f"ps{ps_id}_channels"):
            with dpg.tab(label="Configuration"):
                with dpg.group(horizontal=True, width=0):
                    for channel in range(1, num_channels + 1):
                        with dpg.child_window(width=300, height=box_height):
                            dpg.add_spacer(height=4)
                            with dpg.group(horizontal=True):
                                dpg.add_spacer(width=10)
                                dpg.add_text(f"Channel {channel}")
                                dpg.add_input_text(
                                    hint="Channel Name",
                                    width=130,
                                    tag=f"p{ps_id}c{channel}_name",
                                    callback=self.set_channel_name,
                                    user_data=(ps_id, channel),
                                )
                                # Set channel name from config if available
                                if hasattr(self, "channel_names_from_config"):
                                    name = self.channel_names_from_config.get(
                                        (ps_id, channel), None
                                    )
                                    if name is not None:
                                        dpg.set_value(f"p{ps_id}c{channel}_name", name)
                                        # Also update the channel object if it exists
                                        ps = self.supplies[ps_id - 1]
                                        if ps and channel - 1 < len(ps.channels):
                                            ps.channels[channel - 1].name = name
                                button_tag = f"p{ps_id}c{channel}_pwr"
                                theme_tag = button_tag + "_btn"
                                self._create_btn_theme(theme_tag, self.theme.gray)
                                dpg.add_button(
                                    tag=button_tag,
                                    label=" Off ",
                                    callback=self.set_output_state,
                                    user_data=(ps_id, channel),
                                )
                                dpg.bind_item_theme(dpg.last_item(), theme_tag)
                            dpg.add_spacer(height=9)
                            with dpg.group(horizontal=True):
                                dpg.add_spacer(width=10)
                                dpg.add_text("Group:")
                                self.help(
                                    "Add/remove channel from Group power control."
                                )
                                dpg.add_checkbox(
                                    label="",
                                    tag=f"p{ps_id}c{channel}_group",
                                    callback=self.manage_power_group,
                                    user_data=(ps_id, channel),
                                )
                                dpg.add_spacer(width=5)
                                dpg.add_text("Seq. On|Off:")
                                self.help(
                                    "Specify the delay (in seconds) for power sequencing for this channel."
                                )
                                dpg.add_input_text(
                                    hint="int",
                                    width=30,
                                    indent=200,
                                    tag=f"p{ps_id}c{channel}_seq_on",
                                    callback=self.set_seq_on,
                                    user_data=(ps_id, channel),
                                )
                                dpg.add_input_text(
                                    hint="int",
                                    width=30,
                                    indent=240,
                                    tag=f"p{ps_id}c{channel}_seq_off",
                                    callback=self.set_seq_off,
                                    user_data=(ps_id, channel),
                                )
                            dpg.add_spacer(height=2)
                            with dpg.group(horizontal=True):
                                dpg.add_spacer(width=10)
                                dpg.add_text("Sense: ")
                                self.help("Enable/disable 4-wire sense mode")
                                button_tag = f"p{ps_id}c{channel}_sense"
                                theme_tag = button_tag + "_btn"
                                self._create_btn_theme(theme_tag, self.theme.orange)
                                dpg.add_button(
                                    tag=button_tag,
                                    label=" 2-Wire ",
                                    callback=self.toggle_4wire,
                                    user_data=(ps_id, channel),
                                )
                                dpg.bind_item_theme(dpg.last_item(), theme_tag)
                                if self.latchup_mode:
                                    theme_tag = f"p{ps_id}c{channel}_latchup_btn"
                                    self._create_btn_theme(theme_tag, self.theme.orange)
                                    dpg.add_text(
                                        "Latchup:",
                                        indent=15,
                                        tag=f"p{ps_id}c{channel}_latchup_text",
                                    )
                                    self.help(
                                        "Attempt to clear latchup state for this channel. This will step down the voltage in 10% increments until the high current mode is cleared, and then return to the original voltage setting."
                                    )
                                    dpg.add_button(
                                        label="Clear",
                                        indent=230,
                                        tag=f"p{ps_id}c{channel}_latchup",
                                        callback=self.clear_latchup,
                                        user_data=(ps_id, channel),
                                    )
                                    dpg.bind_item_theme(dpg.last_item(), theme_tag)
                            dpg.add_spacer(height=2)
                            with dpg.group(horizontal=True):
                                dpg.add_spacer(width=10)
                                dpg.add_text("Set: ")
                                dpg.add_input_text(
                                    default_value="5.0",
                                    width=50,
                                    tag=f"p{ps_id}c{channel}_voltage_set",
                                    callback=self.set_voltage,
                                    user_data=(ps_id, channel),
                                    on_enter=True,
                                )
                                dpg.add_text("V")
                                dpg.add_spacer(width=10)
                                dpg.add_input_text(
                                    default_value="0.5",
                                    width=50,
                                    tag=f"p{ps_id}c{channel}_current_set",
                                    callback=self.set_current,
                                    user_data=(ps_id, channel),
                                    on_enter=True,
                                )
                                dpg.add_text("A")
                            dpg.add_spacer(height=2)
                            with dpg.group(horizontal=True):
                                dpg.add_spacer(width=10)
                                dpg.add_text(
                                    "0.00 V",
                                    tag=f"p{ps_id}c{channel}_voltage_meas",
                                    indent=0,
                                )
                                dpg.bind_item_font(dpg.last_item(), self.large_font)
                                dpg.add_text(
                                    "0.00 A",
                                    tag=f"p{ps_id}c{channel}_current_meas",
                                    indent=150,
                                )
                                dpg.bind_item_font(dpg.last_item(), self.large_font)
                                dpg.add_text("")

                            dpg.add_spacer(height=2)
            with dpg.tab(label="Monitor"):
                with dpg.group(horizontal=True, width=0):
                    for channel in range(1, num_channels + 1):
                        with dpg.child_window(width=420, height=340):
                            dpg.add_text(
                                f"Channel {channel}", tag=f"p{ps_id}c{channel}_title"
                            )
                            with dpg.plot(no_title=True):
                                dpg.add_plot_legend()
                                dpg.add_plot_axis(
                                    dpg.mvXAxis,
                                    tag=f"p{ps_id}c{channel}_x",
                                )
                                dpg.add_plot_axis(
                                    dpg.mvYAxis,
                                    tag=f"p{ps_id}c{channel}_y_v",
                                    label="Volts",
                                )
                                dpg.add_plot_axis(
                                    dpg.mvYAxis,
                                    tag=f"p{ps_id}c{channel}_y_i",
                                    label="Amps",
                                )
                                dpg.add_line_series(
                                    np.arange(0, BUF_SIZE),
                                    np.zeros(BUF_SIZE),
                                    parent=f"p{ps_id}c{channel}_y_v",
                                    tag=f"p{ps_id}c{channel}_v",
                                    label="v",
                                )
                                dpg.add_line_series(
                                    np.arange(0, BUF_SIZE),
                                    np.zeros(BUF_SIZE),
                                    parent=f"p{ps_id}c{channel}_y_i",
                                    tag=f"p{ps_id}c{channel}_i",
                                    label="i",
                                )

    def manage_power_group(self, sender, app_data, user_data) -> None:
        """Adds/removes channels from Group (based on Group checkbox state)"""
        logger.debug(f"Entering power_group callback...")
        assert len(user_data) == 2
        ps_num = user_data[0]
        channel_num = user_data[1]
        checked = dpg.get_value(sender)
        t = (ps_num, channel_num)
        if checked and t not in self.groups:
            self.groups.append(t)
        elif not checked and t in self.groups:
            self.groups.remove(t)

    def set_seq_on(self, sender, app_data, user_data) -> None:
        """Callback to set the power on sequence time for the provided channel"""
        logger.debug(f"Entering set_seq_on callback...")
        assert len(user_data) == 2
        ps_num = user_data[0]
        channel_num = user_data[1]
        try:
            value = int(dpg.get_value(sender))
            ps = self.supplies[ps_num - 1]
            if ps:
                ps.channels[channel_num - 1].seq_on = value
        except ValueError:
            # Ignore input if not an int
            return

    def set_seq_off(self, sender, app_data, user_data) -> None:
        """Callback to set the power off sequence time for the provided channel"""
        logger.debug(f"Entering set_seq_off callback...")
        assert len(user_data) == 2
        ps_num = user_data[0]
        channel_num = user_data[1]
        value = int(dpg.get_value(sender))
        ps = self.supplies[ps_num - 1]
        if ps:
            ps.channels[channel_num - 1].seq_off = value

    def set_host(self, sender, app_data, user_data) -> None:
        """Callback to set the host / IP of the provided supply"""
        logger.debug(f"Entering set_host callback...")
        ps_num = user_data
        self.hosts[ps_num - 1] = dpg.get_value(sender)
        logger.debug(f"Updated host for PS {ps_num} to {self.hosts[ps_num - 1]}")

    def _create_ps(self, ps_id: int, num_channels: int) -> PowerSupply:
        """Creates and configures a supply object"""
        ps_idx = ps_id - 1
        host = self.hosts[ps_idx]
        if host:
            ps = self._create_supply(ps_id, host, num_channels)

            # Reconfigure PS if we have a config for it
            if self.config and (cfg := self.config[ps_idx]):
                # Wait for PS init
                while not ps.init_done:
                    time.sleep(0.01)
                ps.configure(cfg)
            return ps

    def set_channel_name(self, sender, app_data, user_data) -> None:
        """Callback to set the name of the provided channel"""
        logger.debug(f"Entering set_channel_name callback...")
        assert len(user_data) == 2
        ps_num = user_data[0]
        channel_num = user_data[1]
        ps = self.supplies[ps_num - 1]
        if ps:
            ch = ps.channels[channel_num - 1]
            name = dpg.get_value(sender)
            ch.name = name

    def set_output_state(self, sender, app_data, user_data) -> None:
        """Callback to set the power state of the provided channel"""
        logger.debug(f"Entering set_output_state callback...")
        assert len(user_data) == 2
        ps_num = user_data[0]
        channel_num = user_data[1]
        # Infer desired power state from button color
        if dpg.get_value(sender + "_btn_color") == self.theme.gray[0]:
            # Currently off, set state to on
            mode_on = True
        else:
            mode_on = False
        ps = self.supplies[ps_num - 1]
        if ps:
            ps.set_output_state(channel_num, mode_on)

    def set_voltage(self, sender, app_data, user_data) -> None:
        """Callback to set the voltage of the provided channel"""
        logger.debug(f"Entering set_voltage callback...")
        assert len(user_data) == 2
        ps_num = user_data[0]
        channel_num = user_data[1]
        voltage = float(dpg.get_value(sender))
        ps = self.supplies[ps_num - 1]
        if ps:
            ps.set_voltage(channel_num, voltage)

    def set_current(self, sender, app_data, user_data) -> None:
        """Callback to set the current of the provided channel"""
        logger.debug(f"Entering set_current callback...")
        assert len(user_data) == 2
        ps_num = user_data[0]
        channel_num = user_data[1]
        current = float(dpg.get_value(sender))
        ps = self.supplies[ps_num - 1]
        if ps:
            ps.set_current(channel_num, current)

    def set_power_btn(self, button_tag: str, power_is_on: bool) -> None:
        """Sets the appearance of a channel's power button based
        on the current power state"""
        base_theme_tag = button_tag + "_btn_color"
        if power_is_on:
            self._set_btn_colors(base_theme_tag, self.theme.green)
            if dpg.does_item_exist(button_tag):
                dpg.configure_item(button_tag, label=" On ")
        else:
            self._set_btn_colors(base_theme_tag, self.theme.gray)
            if dpg.does_item_exist(button_tag):
                dpg.configure_item(button_tag, label=" Off ")

    def set_sense_btn(self, button_tag: str, is_4wire: bool) -> None:
        """Sets the appearance of a channel's 4-wire sense button based
        on the current sense mode"""
        if is_4wire:
            if dpg.does_item_exist(button_tag):
                dpg.configure_item(button_tag, label=" 4-Wire ")
        else:
            if dpg.does_item_exist(button_tag):
                dpg.configure_item(button_tag, label=" 2-Wire ")

    def set_voltage_color(
        self,
        tag: str,
        power_is_on: bool,
        v_set: float,
        v_meas: float,
        tol_pct: float = VOLTAGE_TOL_PCT,
    ) -> None:
        """Sets the color of a channel's voltage text based on the set and measured values"""
        if not power_is_on:
            self.theme.set_text_color(tag, self.theme.gray_text)
        elif abs(v_set - v_meas) <= tol_pct * v_set:
            self.theme.set_text_color(tag, self.theme.green_text)
        else:
            self.theme.set_text_color(tag, self.theme.red_text)

    def set_current_color(
        self,
        tag: str,
        power_is_on: bool,
        c_set: float,
        c_meas: float,
        tol_pct: float = CURRENT_TOL_PCT,
    ) -> None:
        """Sets the color of a channel's current text based on the set and measured values"""
        if not power_is_on:
            self.theme.set_text_color(tag, self.theme.gray_text)

        # If measured current is within tol_pct of set current, set to red, else green
        elif c_meas >= c_set * (1 - tol_pct):
            self.theme.set_text_color(tag, self.theme.red_text)
        else:
            self.theme.set_text_color(tag, self.theme.green_text)

    def set_channels(self, sender, app_data, user_data) -> None:
        """Callback to set the number of channels for the provided supply"""
        logger.debug(f"Entering set_channels callback...")
        ps_id = int(user_data)
        try:
            num_channels = int(dpg.get_value(sender))
            self.channels_input[ps_id - 1] = num_channels
        except:
            pass

    def set_sample_rate(self, sender, app_data, user_data) -> None:
        """Change sample rate"""
        logger.debug(f"Entering set_sample_rate callback...")
        self.sample_rate = float(app_data)
        logger.info(f"Set sample rate = {self.sample_rate}")
        self.timer.interval = self.sample_rate
        for ps in self.supplies:
            if ps:
                ps.sample_rate = self.sample_rate

    def connect(self, sender, app_data, user_data) -> None:
        """Callback to initiate connection to the provided supply"""
        # Get PS ID: Sender is of the form ps{id}_connect
        logger.debug(f"Entering connect callback...")
        id = int(sender.split("_")[0][2:])
        if dpg.get_item_label(sender) == "Connect":
            # Create new PowerSupply
            num_channels = self.channels_input[id - 1]
            ps = self._create_ps(id, num_channels)

            # Create channel content
            self.add_channels(id, num_channels)
            dpg.configure_item(sender, label="Disconnect")

            # Add PS IDN to header label
            dpg.configure_item(f"ps{id}", label=f"Power Supply {id}: {ps.idn}")
        else:
            self._delete_supply(id)
            dpg.configure_item(sender, label="Connect")

    def _create_supply(self, id: int, host: str, num_channels: int) -> PowerSupply:
        """Creates a new PowerSupply object at the specified index"""
        if host == "demo":
            ps = DemoPowerSupply(host, id, num_channels)
        else:
            ps = PowerSupply(host, id, num_channels)
        self.supplies[id - 1] = ps
        return ps

    def _delete_supply(self, id: int) -> None:
        """Deletes a PowerSupply object from the specified index"""
        # Delete PowerSupply object
        if self.supplies[id - 1]:
            ps = self.supplies[id - 1]
            if ps:
                ps.close()
                num_channels = len(ps.channels)
                # Delete channel content
                dpg.delete_item(f"ps{id}_channels")
                self.supplies.pop(id - 1)
                self.supplies.insert(id - 1, None)
                for ch in range(1, num_channels + 1):
                    dpg.delete_item(f"p{id}c{ch}_pwr_btn")
                    dpg.delete_item(f"p{id}c{ch}_sense")
                    dpg.delete_item(f"p{id}c{ch}_sense_btn")
                del ps

    def _set_btn_colors(self, base_tag: str, colors: tuple) -> None:
        """Changes the color of a button theme"""
        if dpg.does_item_exist(base_tag):
            dpg.set_value(base_tag, colors[0])
            dpg.set_value(base_tag + "_act", colors[2])
            dpg.set_value(base_tag + "_hov", colors[1])
        else:
            logger.debug(f"Button theme {base_tag} does not exist.")

    def _create_btn_theme(self, theme_tag: str, colors: tuple) -> None:
        """Defines a DPG button theme for the provided tag"""
        with dpg.theme(tag=theme_tag):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(
                    dpg.mvThemeCol_Button,
                    colors[0],
                    tag=theme_tag + "_color",
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_ButtonActive,
                    colors[2],
                    tag=theme_tag + "_color_act",
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_ButtonHovered,
                    colors[1],
                    tag=theme_tag + "_color_hov",
                )
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 5)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 3, 3)


class Timer:
    def __init__(self, interval: float = 1):
        self.total_time = None
        self.last_total_time = None
        self.interval: float = interval
        self.stored_interval: float = interval

    def update(self) -> bool:
        """Timer for GUI render loop"""
        self.total_time = dpg.get_total_time()
        if self.last_total_time:
            delta_time = dpg.get_total_time() - self.last_total_time
            if delta_time > self.interval:
                self.last_total_time = self.total_time
                return True
        else:
            self.last_total_time = self.total_time
        return False


class GuiTheme:
    def __init__(self):
        self.bg = (7, 12, 19)  # darkest color
        self.header = (24, 40, 63)  # lighter than bg
        self.check = (213, 140, 41)  # accent color
        self.tab = (213, 140, 41)  # accent color
        self.hover = (234, 150, 45)  # slightly lighter accent color
        self.scrollbar = (41, 67, 104)
        self.scrollbar_active = (22, 65, 134)

        self.red = ([153, 61, 61, 255], [178, 54, 54, 255], [204, 41, 41, 255])
        self.green = ([80, 153, 61, 255], [79, 179, 54, 255], [73, 204, 41, 255])
        self.orange = ([213, 140, 41, 255], [234, 150, 45, 255], [234, 150, 45, 200])
        self.gray = ([100, 100, 100, 255], [120, 120, 120, 255], [140, 140, 140, 255])

        self.red_text = (255, 0, 0, 255)
        self.green_text = (0, 255, 0, 255)
        self.orange_text = (255, 165, 0, 255)
        self.gray_text = (150, 150, 150, 255)

    def set_header_btn_theme(self, theme_tag: str, colors: tuple) -> None:
        """Sets the theme for the GUI header"""
        with dpg.theme(tag=theme_tag):
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(
                    dpg.mvThemeCol_Button,
                    colors[0],
                    tag=theme_tag + "_color",
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_ButtonActive,
                    colors[2],
                    tag=theme_tag + "_color_act",
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_ButtonHovered,
                    colors[1],
                    tag=theme_tag + "_color_hov",
                )
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 8)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 6, 6)

    def set_text_color(self, tag, color):
        # Change text color based on status
        with dpg.theme() as item_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(
                    dpg.mvThemeCol_Text, color, category=dpg.mvThemeCat_Core
                )
        dpg.bind_item_theme(tag, item_theme)
