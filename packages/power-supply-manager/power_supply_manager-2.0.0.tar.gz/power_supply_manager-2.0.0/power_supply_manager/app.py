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

import dearpygui.dearpygui as dpg
from datetime import datetime
import numpy as np

from power_supply_manager.state import *

state = GuiState()


logo_width = 0
logo_height = 0
logo_image_id = None


def app():
    dpg.create_context()
    dpg.create_viewport(
        title="DevBuildZero Power Supply Manager", width=1240, height=760
    )
    dpg.setup_dearpygui()
    dpg.show_viewport()
    _show_gui()
    dpg.set_primary_window("_primary_wnd", True)
    while dpg.is_dearpygui_running():
        trigger_update = state.timer.update()
        if trigger_update:
            _update_app_content()
        dpg.render_dearpygui_frame()
    dpg.destroy_context()


def update_logo_position():
    global logo_width, logo_height, logo_image_id
    win_width = dpg.get_item_width("_primary_wnd")
    win_height = dpg.get_item_height("_primary_wnd")
    x = win_width - logo_width - 20
    y = win_height - logo_height - 20
    dpg.set_item_pos(logo_image_id, [x, y])


def on_resize(sender, app_data, user_data):
    update_logo_position()


def _show_gui():
    global logo_width, logo_height, logo_image_id
    with dpg.window(
        on_close=state.on_gui_close,
        pos=(0, 0),
        tag="_primary_wnd",
    ):
        with dpg.theme() as global_theme:
            with dpg.theme_component(dpg.mvAll):
                dpg.add_theme_color(dpg.mvThemeCol_WindowBg, state.theme.bg)
                dpg.add_theme_color(dpg.mvThemeCol_ChildBg, state.theme.bg)
                dpg.add_theme_color(dpg.mvThemeCol_PopupBg, state.theme.bg)
                dpg.add_theme_color(dpg.mvThemeCol_TitleBgCollapsed, state.theme.bg)
                dpg.add_theme_color(dpg.mvThemeCol_Button, state.theme.header)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBg, state.theme.header)
                dpg.add_theme_color(dpg.mvThemeCol_MenuBarBg, state.theme.header)
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, state.theme.header)
                dpg.add_theme_color(dpg.mvThemeCol_Header, state.theme.header)
                dpg.add_theme_color(
                    dpg.mvThemeCol_ResizeGripHovered, state.theme.header
                )
                dpg.add_theme_color(dpg.mvThemeCol_ResizeGripActive, state.theme.header)
                dpg.add_theme_color(dpg.mvThemeCol_Tab, state.theme.header)
                dpg.add_theme_color(dpg.mvThemeCol_TabUnfocused, state.theme.header)
                dpg.add_theme_color(dpg.mvThemeCol_CheckMark, state.theme.check)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, state.theme.check)
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrabActive, state.theme.check)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, state.theme.check)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, state.theme.check)
                dpg.add_theme_color(dpg.mvThemeCol_TabActive, state.theme.check)
                dpg.add_theme_color(
                    dpg.mvThemeCol_TabUnfocusedActive, state.theme.check
                )
                dpg.add_theme_color(dpg.mvThemeCol_PlotLines, state.theme.check)
                dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, state.theme.check)
                dpg.add_theme_color(dpg.mvThemeCol_TextSelectedBg, state.theme.check)
                dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, state.theme.hover)
                dpg.add_theme_color(dpg.mvThemeCol_SliderGrab, state.theme.hover)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, state.theme.hover)
                dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, state.theme.hover)
                dpg.add_theme_color(dpg.mvThemeCol_TabHovered, state.theme.hover)
                dpg.add_theme_color(dpg.mvThemeCol_PlotLinesHovered, state.theme.hover)
                dpg.add_theme_color(
                    dpg.mvThemeCol_PlotHistogramHovered, state.theme.hover
                )
                dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, state.theme.scrollbar)
                dpg.add_theme_color(
                    dpg.mvThemeCol_ScrollbarGrabHovered, state.theme.scrollbar_active
                )
                dpg.add_theme_color(
                    dpg.mvThemeCol_ScrollbarGrabActive, state.theme.scrollbar_active
                )
        dpg.bind_theme(global_theme)

        with dpg.menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(
                    label="Load Config", callback=lambda: dpg.show_item("file_dialog")
                )
                dpg.add_menu_item(
                    label="Save Config",
                    callback=lambda: dpg.show_item("save_dialog"),
                )
            with dpg.menu(label="Tools"):
                dpg.add_menu_item(
                    label="Plot Log CSV", callback=lambda: dpg.show_item("plot_dialog")
                )
                dpg.add_menu_item(
                    label="Toggle Latchup Control Mode",
                    callback=lambda: state.toggle_latchup_toolbar(),
                )
            with dpg.menu(label="Window"):
                dpg.add_menu_item(
                    label="Toggle Fullscreen",
                    callback=lambda: dpg.toggle_viewport_fullscreen(),
                )
            with dpg.menu(label="Help"):
                dpg.add_menu_item(
                    label="About",
                    callback=lambda: dpg.configure_item("about_tag", show=True),
                )
                dpg.add_menu_item(
                    label="Show Metrics",
                    callback=lambda: dpg.show_tool(dpg.mvTool_Metrics),
                )

        with dpg.file_dialog(
            directory_selector=False,
            show=False,
            callback=state.config_selection,
            tag="file_dialog",
            width=600,
            height=600,
        ):
            dpg.add_file_extension(".json")

        with dpg.file_dialog(
            directory_selector=True,
            show=False,
            callback=state.dump_config,
            tag="save_dialog",
            width=800,
            height=600,
        ):
            with dpg.group():
                dpg.add_text("Choose filename to save config:")
                dpg.add_input_text(
                    default_value="my_config",
                    width=150,
                    callback=state.store_config_filename,
                )

        with dpg.file_dialog(
            directory_selector=False,
            show=False,
            callback=state.plot_log_callback,
            tag="plot_dialog",
            width=800,
            height=600,
        ):
            dpg.add_file_extension(".csv")

        with dpg.window(
            label="About Power Supply Manager",
            modal=True,
            show=False,
            tag="about_tag",
            no_title_bar=True,
            pos=(200, 200),
        ):
            dpg.add_text(
                "This application was developed by DevBuildZero (devbuildzero.com) and is provided\nfor free under the MIT open source license:"
            )
            dpg.add_separator()
            dpg.add_text(
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
            )
            dpg.add_separator()
            with dpg.group(horizontal=True):
                dpg.add_button(
                    label="Close",
                    width=75,
                    callback=lambda: dpg.configure_item("about_tag", show=False),
                )

        with dpg.collapsing_header(label="Controls", default_open=True):
            btn_on_theme = "btn_on_theme"
            state.theme.set_header_btn_theme(btn_on_theme, state.theme.green)
            btn_off_theme = "btn_off_theme"
            state.theme.set_header_btn_theme(btn_off_theme, state.theme.red)
            btn_new_theme = "btn_new_theme"
            state.theme.set_header_btn_theme(btn_new_theme, state.theme.orange)
            with dpg.group(horizontal=True):
                with dpg.child_window(width=140, height=42):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Supplies:")
                        state.help("Add a new power supply.")
                        dpg.add_button(label=" New ", callback=state.add_ps_header)
                        dpg.bind_item_theme(dpg.last_item(), btn_new_theme)
                with dpg.child_window(width=300, height=42):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Logging:")
                        dpg.add_input_text(
                            width=100,
                            callback=state.log_prefix,
                            hint="log prefix",
                        )
                        state.help(
                            "Start/stop logging supply measurements to a CSV file."
                        )
                        dpg.add_button(
                            label="Start",
                            callback=state.start_logging,
                        )
                        dpg.bind_item_theme(dpg.last_item(), btn_on_theme)

                        dpg.add_button(
                            label="Stop",
                            callback=state.stop_logging,
                        )
                        dpg.bind_item_theme(dpg.last_item(), btn_off_theme)
                with dpg.child_window(width=155, height=42):
                    with dpg.group(horizontal=True):
                        dpg.add_text("All:")
                        state.help("Power on/off all supply channels.")

                        dpg.add_button(
                            label=" On ",
                            callback=state.all_on,
                        )
                        dpg.bind_item_theme(dpg.last_item(), btn_on_theme)

                        dpg.add_button(
                            label=" Off ",
                            callback=state.all_off,
                        )
                        dpg.bind_item_theme(dpg.last_item(), btn_off_theme)

                with dpg.child_window(width=165, height=42):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Group:")
                        state.help(
                            "Power on/off all channels that have the Group checkbox selected."
                        )
                        dpg.add_button(
                            label=" On ",
                            callback=state.group_on,
                        )
                        dpg.bind_item_theme(dpg.last_item(), btn_on_theme)
                        dpg.add_button(
                            label=" Off ",
                            callback=state.group_off,
                        )
                        dpg.bind_item_theme(dpg.last_item(), btn_off_theme)

                with dpg.child_window(width=185, height=42):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Sequence:")
                        state.help(
                            "Execute power supply sequence. If a sequence value is set, each channel will turn on/off after <value> seconds. Use this to control the order in which channels are powered."
                        )
                        dpg.add_button(
                            label=" On ",
                            callback=state.sequence_on,
                        )
                        dpg.bind_item_theme(dpg.last_item(), btn_on_theme)
                        dpg.add_button(
                            label=" Off ",
                            callback=state.sequence_off,
                        )
                        dpg.bind_item_theme(dpg.last_item(), btn_off_theme)

                with dpg.child_window(width=150, height=42):
                    with dpg.group(horizontal=True):
                        dpg.add_text("Sample Rate:")
                        state.help("Set power supply sample rate.")
                        dpg.add_input_text(
                            width=40,
                            default_value="1",
                            callback=state.set_sample_rate,
                            on_enter=True,
                        )

        # Load the logo image as a texture
        try:
            logo_width, logo_height, _, logo_data = dpg.load_image("static/logo.png")
        except Exception:
            logo_width, logo_height, _, logo_data = dpg.load_image(
                "./_internal/static/logo.png"
            )
        with dpg.texture_registry():
            dpg.add_static_texture(
                logo_width, logo_height, logo_data, tag="logo_texture"
            )

        # Add the logo image as the last child so it's on top
        logo_image_id = dpg.add_image(
            "logo_texture", width=logo_width, height=logo_height, parent="_primary_wnd"
        )

    dpg.set_viewport_resize_callback(on_resize)
    dpg.set_frame_callback(30, lambda: update_logo_position())


def _update_app_content():
    # Build row of data for data logging
    datestamp = str(datetime.now().isoformat()).replace(":", "-")
    data_row = [datestamp]
    for i in range(len(state.supplies)):
        # Only update supplies elements that are not None
        ps = state.supplies[i]
        if ps and ps.channels and ps.init_done:
            for ch in ps.channels:
                # This will error out if we delete a supply during an update
                try:
                    # Set power button appearance based on current power state
                    state.set_power_btn(f"p{ps.num}c{ch.num}_pwr", ch.output_on)

                    state.set_sense_btn(
                        f"p{ps.num}c{ch.num}_sense",
                        ch.sense_meas,
                    )

                    # Set voltage and current text color based on current value
                    state.set_voltage_color(
                        f"p{ps.num}c{ch.num}_voltage_meas",
                        ch.output_on,
                        ch.voltage_set,
                        ch.voltage_meas,
                    )
                    state.set_current_color(
                        f"p{ps.num}c{ch.num}_current_meas",
                        ch.output_on,
                        ch.current_set,
                        ch.current_meas,
                    )

                    # Check for channel values that have changed and update GUI
                    dpg.set_value(f"p{ps.num}c{ch.num}_name", ch.name)
                    dpg.set_value(f"p{ps.num}c{ch.num}_voltage_set", ch.voltage_set)
                    dpg.set_value(
                        f"p{ps.num}c{ch.num}_voltage_meas",
                        f"{format_value(ch.voltage_meas)}V",
                    )
                    dpg.set_value(f"p{ps.num}c{ch.num}_current_set", ch.current_set)
                    dpg.set_value(
                        f"p{ps.num}c{ch.num}_current_meas",
                        f"{format_value(ch.current_meas)}A",
                    )
                    if ch.seq_on >= 0:
                        dpg.set_value(f"p{ps.num}c{ch.num}_seq_on", ch.seq_on)
                    if ch.seq_off >= 0:
                        dpg.set_value(f"p{ps.num}c{ch.num}_seq_off", ch.seq_off)
                    dpg.set_value(
                        f"p{ps.num}c{ch.num}_v",
                        [np.arange(0, BUF_SIZE), ch.voltage_buffer],
                    )
                    dpg.set_value(
                        f"p{ps.num}c{ch.num}_i",
                        [np.arange(0, BUF_SIZE), ch.current_buffer],
                    )
                    dpg.set_axis_limits(
                        f"p{ps.num}c{ch.num}_y_v",
                        np.min(ch.voltage_buffer) - 0.5,
                        np.max(ch.voltage_buffer) + 0.5,
                    )
                    dpg.set_axis_limits(
                        f"p{ps.num}c{ch.num}_y_i",
                        np.min(ch.current_buffer) - 0.2,
                        np.max(ch.current_buffer) + 0.2,
                    )
                    if ch.name:
                        plot_title = f"Channel {ch.num}: {ch.name}"
                    else:
                        plot_title = f"Channel {ch.num}"
                    dpg.set_value(f"p{ps.num}c{ch.num}_title", plot_title)
                    dpg.configure_item(
                        f"p{ps.num}c{ch.num}_v",
                        label=f"v = {format_value(ch.voltage_meas)}V",
                    )
                    dpg.configure_item(
                        f"p{ps.num}c{ch.num}_i",
                        label=f"i = {format_value(ch.current_meas)}A",
                    )
                    data_row.append(ch.voltage_meas)
                    data_row.append(ch.current_meas)
                except:
                    logger.debug(f"DPG items for PS {ps.num} do not exist.")
    # Log data, if log is open
    if state.csv and len(data_row) > 1:
        state.csv.writerow(data_row)

    if state.latchup_mode:
        if state.last_power_cycle_time:
            # Update how long ago the last power cycle event occurred
            # e.g. "2 minutes ago"
            time_since_last_cycle = datetime.now() - state.last_power_cycle_time
            if dpg.does_item_exist("_last_power_cycle_event"):
                if time_since_last_cycle.total_seconds() < 60:
                    dpg.set_value(
                        "_last_power_cycle_event",
                        f"{state.power_cycle_events} (last event: {int(time_since_last_cycle.total_seconds())} sec ago)",
                    )
                elif time_since_last_cycle.total_seconds() < 3600:
                    dpg.set_value(
                        "_last_power_cycle_event",
                        f"{state.power_cycle_events} (last power cycle event: {int(time_since_last_cycle.total_seconds() // 60)} min {int(time_since_last_cycle.total_seconds() % 60)} sec ago)",
                    )
        else:
            if dpg.does_item_exist("_last_power_cycle_event"):
                dpg.set_value("_last_power_cycle_event", "0")

        if state.current_limit_reset:
            state.check_for_power_cycle()


def format_value(value) -> str:
    """Returns a string of the provided value in a user-friendly format
    (e.g. 350 mV instead of 0.350 V)"""
    if value < 0:
        return f"0.00 m"
    if value < 1:
        return f"{value * 1000:.2f} m"
    return f"{value:.2f} "


if __name__ == "__main__":
    app()
