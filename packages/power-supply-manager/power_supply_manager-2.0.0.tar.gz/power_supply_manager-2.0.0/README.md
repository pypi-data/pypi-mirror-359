
[![Pipeline](https://gitlab.com/d7406/power-supply-manager/badges/main/pipeline.svg)](https://gitlab.com/d7406/power-supply-manager/-/pipelines)
[![PyPI - Version](https://img.shields.io/pypi/v/power-supply-manager.svg)](https://pypi.org/project/power-supply-manager)
[![License](https://img.shields.io/badge/license-mit-blue)](https://gitlab.com/d7406/power-supply-manager/-/blob/main/LICENSE)


![Power Supply Manager](images/PowerSupplyManager.png)

Control multiple networked power supplies from the same graphical application. 

# Features

## 🌐 Remote Ethernet control

Connect to multiple bench-top power supply units over Ethernet (VXI11 or LXI protocols). Name each channel for easy identification.

![Overview](images/Overview.jpg)

## ⚡ Four ways to control power output

* Individual channel control.
* Power all channels on/off simultaneously.
* Group any combination of channels to control simultaneously.
* Define power on/off sequences with configurable time delays in between.

![Power Control](images/PSMPowerControl.gif)

## 🗠 Real-time voltage and current waveforms

View plots of the previous 10 minutes of voltage and current measurements for each channel.

![Plots](images/Plots.jpg)

## 🎛️ Easy power supply channel controls

Set voltage, current, and 2/4-wire sense mode.

![Supply Channel Controls](images/PSMChannelControls.gif)

## 🗒️ CSV logging and plotting

Log voltage and current measurements to CSV files. Plots are automatically generated from each CSV.

![Log Files](images/LogFiles.jpg)

## 🔄 Store GUI configuration

Save and load multi-device configuration files to quickly restore settings.

![Load Configuration](images/PSMLoadConfiguration.gif)

## 💥 [Advanced Mode] Latchup toolbar

* Automatically power cycle all active channels when a current limit is reached.
* Latchup Clear button automatically steps down channel voltage until latchup state is cleared and then returns to nominal voltage.
* Logs time and count of current limit events.

![Latchup Toolbar](images/PSMLatchupToolbar.gif)

# Installation

## From pre-built executable (recommended)

1. Download Windows or Linux executable from [Releases](https://gitlab.com/d7406/power-supply-manager/-/releases) or [Package Registry](https://gitlab.com/d7406/power-supply-manager/-/packages/).
2. Copy the entire `PowerSupplyManager` directory from `dist` to the desired location on your system.
3. Run the executable.

## From PyPI

1. Install pip package:
  ```
  pip install power-supply-manager
  ```

  Make sure the pip installation directory is on your system PATH:
  * Linux / MacOS: Typically `$HOME/.local/bin`, `/usr/bin`, or `/usr/local/bin`
  * Windows: Typically `<Python install dir>\Scripts` or `C:\Users\<username>\AppData\Roaming\Python\Python<vers>\Scripts`

2. Run application:
  ```
  power-supply-manager
  ```

## From source

1. Install the repository:

  ```
  git clone https://gitlab.com/d7406/power-supply-manager.git
  ```
2. Install [Poetry](https://python-poetry.org)
3. Setup virtual environment using Poetry:
  ```
  poetry install
  ```
4. Run application:
  ```
  poetry run python power_supply_manager/power_supply_manager.py
  ```

# Contributing
We welcome contributions and suggestions to improve this application. Please submit an issue or merge request [here](https://gitlab.com/d7406/power-supply-manager)

# Author
[DevBuildZero, LLC](http://devbuildzero.com)

# License
This software is provided for free under the MIT open source license:

Copyright 2025 DevBuildZero, LLC

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
