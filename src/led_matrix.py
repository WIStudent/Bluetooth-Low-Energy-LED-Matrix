import dbus
import dbus.mainloop.glib

try:
    from gi.repository import GObject
except ImportError:
    import gobject as GObject

from Adafruit_LED_Backpack import BicolorMatrix8x8

from bluez_components import *

mainloop = None

COLOR_TABLE = {
    0: BicolorMatrix8x8.OFF,
    1: BicolorMatrix8x8.RED,
    2: BicolorMatrix8x8.GREEN,
    3: BicolorMatrix8x8.YELLOW
}


def int_to_hex(int_value):
    return {
        0: '0',
        1: '1',
        2: '2',
        3: '3',
        4: '4',
        5: '5',
        6: '6',
        7: '7',
        8: '8',
        9: '9',
        10: 'a',
        11: 'b',
        12: 'c',
        13: 'd',
        14: 'e',
        15: 'f'
    }.get(int_value, '0')


def set_display_pixel(display, row, column, value):
    display.set_pixel(column, row, COLOR_TABLE[value])


def set_display_row(display, row, byte_values):
    """
    The color of each pixel is encoded in two bits.
    00: off
    01: red
    10: green
    11: yellow
    Each row consists of 8 pixel and therefore of 2 bytes.
    Pixel  |  0  |  1  |  2  |  3  |  4  |  5  |  6  |  7
    -------+-----+-----+-----+-----+-----+-----+-----+----
    Bit    | 7 6 | 5 4 | 3 2 | 1 0 | 7 6 | 5 4 | 3 2 | 1 0
    -------+-----+-----+-----+-----+-----+-----+-----+-----
    Byte   |           0           |           1
    """
    pixel_0 = byte_values[0] >> 6
    pixel_1 = (byte_values[0] & 0x30) >> 4
    pixel_2 = (byte_values[0] & 0x0c) >> 2
    pixel_3 = (byte_values[0] & 0x03)

    pixel_4 = byte_values[1] >> 6
    pixel_5 = (byte_values[1] & 0x30) >> 4
    pixel_6 = (byte_values[1] & 0x0c) >> 2
    pixel_7 = (byte_values[1] & 0x03)

    set_display_pixel(display, row, 0, pixel_0)
    set_display_pixel(display, row, 1, pixel_1)
    set_display_pixel(display, row, 2, pixel_2)
    set_display_pixel(display, row, 3, pixel_3)
    set_display_pixel(display, row, 4, pixel_4)
    set_display_pixel(display, row, 5, pixel_5)
    set_display_pixel(display, row, 6, pixel_6)
    set_display_pixel(display, row, 7, pixel_7)
    display.write_display()


class RowChrc(Characteristic):
    ROW_UUID = '12345678-1234-5678-1234-56789abc000'

    def __init__(self, bus, index, service, row, display):
        Characteristic.__init__(
            self, bus, index,
            self.ROW_UUID + int_to_hex(row),  # use the row number to build the UUID
            ['read', 'write'],
            service)
        self.value = [0x00, 0x00]
        self.row = row
        self.display = display

    def ReadValue(self, options):
        print('RowCharacteristic Read: Row: ' + str(self.row) + ' ' + repr(self.value))
        return self.value

    def WriteValue(self, value, options):
        print('RowCharacteristic Write: Row: ' + str(self.row) + ' ' + repr(value))
        set_display_row(self.display, self.row, value[:2])
        self.value = value[:2]


class LedService(Service):
    LED_SVC_UUID = '12345678-1234-5678-1234-56789abc0010'

    def __init__(self, bus, index, display):
        Service.__init__(self, bus, index, self.LED_SVC_UUID, True)
        self.add_characteristic(RowChrc(bus, 0, self, 0, display))
        self.add_characteristic(RowChrc(bus, 1, self, 1, display))
        self.add_characteristic(RowChrc(bus, 2, self, 2, display))
        self.add_characteristic(RowChrc(bus, 3, self, 3, display))
        self.add_characteristic(RowChrc(bus, 4, self, 4, display))
        self.add_characteristic(RowChrc(bus, 5, self, 5, display))
        self.add_characteristic(RowChrc(bus, 6, self, 6, display))
        self.add_characteristic(RowChrc(bus, 7, self, 7, display))


class LedApplication(Application):
    def __init__(self, bus, display):
        Application.__init__(self, bus)
        self.add_service(LedService(bus, 0, display))


class LedAdvertisement(Advertisement):
    def __init__(self, bus, index):
        Advertisement.__init__(self, bus, index, 'peripheral')
        self.add_service_uuid(LedService.LED_SVC_UUID)
        self.include_tx_power = True


def setup_display():
    display = BicolorMatrix8x8.BicolorMatrix8x8()
    display.begin()
    display.clear()
    display.write_display()
    return display


def register_ad_cb():
    """
    Callback if registering advertisement was successful
    """
    print('Advertisement registered')


def register_ad_error_cb(error):
    """
    Callback if registering advertisement failed
    """
    print('Failed to register advertisement: ' + str(error))
    mainloop.quit()


def register_app_cb():
    """
    Callback if registering GATT application was successful
    """
    print('GATT application registered')


def register_app_error_cb(error):
    """
    Callback if registering GATT application failed.
    """
    print('Failed to register application: ' + str(error))
    mainloop.quit()


def main():
    global mainloop
    global display

    dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)

    bus = dbus.SystemBus()

    # Get ServiceManager and AdvertisingManager
    service_manager = get_service_manager(bus)
    ad_manager = get_ad_manager(bus)

    # Create gatt services
    display = setup_display()
    app = LedApplication(bus, display)

    # Create advertisement
    test_advertisement = LedAdvertisement(bus, 0)

    mainloop = GObject.MainLoop()

    # Register gatt services
    service_manager.RegisterApplication(app.get_path(), {},
                                        reply_handler=register_app_cb,
                                        error_handler=register_app_error_cb)

    # Register advertisement
    ad_manager.RegisterAdvertisement(test_advertisement.get_path(), {},
                                     reply_handler=register_ad_cb,
                                     error_handler=register_ad_error_cb)

    try:
        mainloop.run()
    except KeyboardInterrupt:
        display.clear()
        display.write_display()


if __name__ == '__main__':
    main()
