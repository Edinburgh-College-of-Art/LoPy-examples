#===============================================================================
# This is a class will send a value over BLE
#
# Thread that will search for the latest advertised MAC and change RGB LED accordingly
#
# The call back for reading the LoPy over BLE will update the mac address that
# is being searched.
#
# Use LightBlue for macOS to debug
#===============================================================================
from network import Bluetooth
import pycom
import ubinascii
import os
import machine
import time
import _thread
#===============================================================================
class BleHotCold:
    #---------------------------------------------------------------------------
    # Members
    bluetooth = Bluetooth()
    services = []
    characteristics = []
    current_target_mac = '' # initialise globally MAC to search for.
    characteristic_callback = None
    game_thread = _thread
    hot_shift = 16 # bit shift for hot colour
    cold_shift = 0 # bit shift for cold colour
    #---------------------------------------------------------------------------

    def __init__(self):
        """
        Constructor
        """
        pycom.heartbeat(False)
        pycom.rgbled(0x00007f)  # Blue

        self.bluetooth.set_advertisement(name='LoPy',manufacturer_data='Pycom', service_data='BLE')
        self.bluetooth.start_scan(-1)
        self.services.append(self.bluetooth.service(uuid=b'1234567890123456', isprimary=True))
        self.characteristics.append(self.services[0].characteristic(uuid=b'ab34567890123456', value='LoPy 1 BLE'))
    #---------------------------------------------------------------------------
    def setup_game(self):
        """
        sets up the class to advertise a service and characteristic with callbacks
        """
        self.bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=self.connection_callback)
        self.bluetooth.advertise(True)
        self.characteristics[0].callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=self.get_new_target_mac)
        self.services[0].start()
        self.get_new_target_mac()
        print("Target MAC: " + self.current_target_mac + "\n")

    #---------------------------------------------------------------------------

    def get_new_target_mac(self):
        """
        update the target MAC of the game
        """
        #-----------------------------------------------------------------------
        mac_list = list()
        device = self.bluetooth.get_adv()
        #-----------------------------------------------------------------------
        if (device is not None):
            device_mac  = str(ubinascii.hexlify(device.mac).decode())
            device_name = str(self.bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_NAME_CMPL))
            devie_rssi  = str(device.rssi)
            #-----------------------------------------------------------------------
            self.current_target_mac = device_mac
            #-----------------------------------------------------------------------
            print('####################################')
            print (device_name + " " + device_mac + " " + devie_rssi)
            print(self.bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_FLAG))
            print(self.bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_NAME_CMPL))
            #-----------------------------------------------------------------------
            raw_mfg = self.bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_MANUFACTURER_DATA)
            self.print_manufacturer_data(raw_mfg)
        else:
            return
        #-----------------------------------------------------------------------
    #---------------------------------------------------------------------------
    def connection_callback (bt_o):
        """
        callback when a client connects to the LoPy
        """
        events = bt_o.events()   # this method returns the flags and clears the internal registry
        if events & Bluetooth.CLIENT_CONNECTED:
            print("Client connected")
            pycom.rgbled(0x007f00) # green
        elif events & Bluetooth.CLIENT_DISCONNECTED:
            print("Client disconnected")
            pycom.rgbled(0x7f0000) # red
    #---------------------------------------------------------------------------
    def hot_cold_thread(self):
        """
        Thread that will search for the latest advertised MAC and change RGB LED
        accordingly
        """
        while (True):
            #-------------------------------------------------------------------
            avg_rssi = float()
            device_read = False
            current_rssi = list()
            adv = self.bluetooth.get_advertisements()
            #-------------------------------------------------------------------
            for device in adv:
                device_mac  = str(ubinascii.hexlify(device.mac).decode())
                if (device_mac == self.current_target_mac and not device_read):
                    current_rssi.append(device.rssi)
            #-------------------------------------------------------------------
            if (len(current_rssi) != 0):
                avg_rssi = sum(current_rssi)/len(current_rssi)
                green = (int((1-(avg_rssi/-93)) * 255) << self.hot_shift)
                red = (int((avg_rssi/-93) * 255) << self.cold_shift)
                pycom.rgbled(green+red)
                print(avg_rssi)
            #-------------------------------------------------------------------
            time.sleep(2)
    #---------------------------------------------------------------------------
    def end_game(self):
        pass

    def print_manufacturer_data(self, mfg):
        """
        """
        if (mfg[0:2] == b'L\x00'):
            print("Apple")
            print("Data Type: {} Data Bytes: {}".format(mfg[2], mfg[3]))
        elif (mfg[0:2] == b'\x06\x00'):
            print("Microsoft")
        print(len(mfg[4:]))
        print(ubinascii.hexlify(mfg[4:]))
        print("")


    def start_game(self):
        self.game_thread.start_new_thread(self.hot_cold_thread, ())

    def set_hot_colour(self, colour):
        if 'red':
            self.hot_shift = 16
        elif 'green':
            self.hot_shift = 8
        elif 'blue':
            self.hot_shift = 0

    def set_cold_colour(self, colour):
        if 'red':
            self.cold_shift = 16
        elif 'green':
            self.cold_shift = 8
        elif 'blue':
            self.cold_shift = 0

#===============================================================================
if __name__ == '__main__':
    hot_cold_game = BleHotCold()
    hot_cold_game.setup_game() # you may need to re_run this untill a MAC is picked up.
    hot_cold_game.start_game()
