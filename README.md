# Bluetooth Low Energy LED Matrix
&copy; 2015 [Tobias Trumm](mailto:tobiastrumm@uni-muenster.de) licensed under GPLv2

This project uses BlueZ's D-Bus API to turn your Raspberry Pi 3 into a Low Energy peripheral. It provides a GATT service that allows you to control the [Adafruit Bicolor LED Square Pixel Matrix](https://www.adafruit.com/products/902).

## Dependencies
- [BlueZ](http://www.bluez.org/) 4.51 or newer. Older versions might also work, but I have not tested it. See this [tutorial from Adafruit](https://learn.adafruit.com/install-bluez-on-the-raspberry-pi/installation) on how to install the latest Bluez version on your Raspberry Pi.
- [dbus-python](https://pypi.python.org/pypi/dbus-python/). Needed to access the D-Bus API.
- [PyGObject](https://wiki.gnome.org/action/show/Projects/PyGObject). Needed to access the D-Bus API.
- [Adafruit Python LED Backpack](https://github.com/adafruit/Adafruit_Python_LED_Backpack). Needed to control the LED matrix.