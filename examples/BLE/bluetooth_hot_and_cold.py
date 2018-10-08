#===============================================================================
# This is a simple script that will send a value over BLE
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
pycom.heartbeat(False)
#===============================================================================
bluetooth = Bluetooth()
bluetooth.set_advertisement(name='LoPy',manufacturer_data='Pycom', service_data='BLE')
bluetooth.start_scan(-1)
pycom.rgbled(0x00007f)  # Blue
#===============================================================================
srv1 = bluetooth.service(uuid=b'1234567890123456', isprimary=True)
char1 = srv1.characteristic(uuid=b'ab34567890123456', value='LoPy 1 BLE')
#===============================================================================
current_search_mac = '' # initialise globally MAC to search for.
#===============================================================================
def char1_cb_handler(char1):
    global char1_read_counter
    global current_search_mac
    #---------------------------------------------------------------------------
    events = char1.events()
    mac_list = list()
    device = bluetooth.get_adv()
    #---------------------------------------------------------------------------
    if (device == None):
        return
    #---------------------------------------------------------------------------
    device_mac  = str(ubinascii.hexlify(device.mac).decode())
    current_search_mac = device_mac
    device_name = str(bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_NAME_CMPL))
    devie_rssi  = str(device.rssi)
    #---------------------------------------------------------------------------
    print('####################################')
    print (device_name + " " + device_mac + " " + devie_rssi)
    print(bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_FLAG))
    print(bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_NAME_CMPL))
    #---------------------------------------------------------------------------
    raw_mfg = bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_MANUFACTURER_DATA)
    if (raw_mfg[0:2] == b'L\x00'):
        print("Apple")
        print("Data Type: {} Data Bytes: {}".format(raw_mfg[2],raw_mfg[3]))
    elif (raw_mfg[0:2] == b'\x06\x00'):
        print("Microsoft")
    print(len(raw_mfg[4:]))
    print(ubinascii.hexlify(raw_mfg[4:]))
    print("")
    #---------------------------------------------------------------------------
#===============================================================================
char1_cb = char1.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=char1_cb_handler)
srv1.start()
#===============================================================================
def conn_cb (bt_o):
    events = bt_o.events()   # this method returns the flags and clears the internal registry
    if events & Bluetooth.CLIENT_CONNECTED:
        print("Client connected blah blah")
        pycom.rgbled(0x007f00) # green
    elif events & Bluetooth.CLIENT_DISCONNECTED:
        print("Client disconnected yada yada")
        pycom.rgbled(0x7f0000) # red
#===============================================================================
bluetooth.callback(trigger=Bluetooth.CLIENT_CONNECTED | Bluetooth.CLIENT_DISCONNECTED, handler=conn_cb)
bluetooth.advertise(True)
#===============================================================================
# Thread that will search for the latest advertised MAC and change RGB LED accordingly
def th_func():
    while (True):
        #-----------------------------------------------------------------------
        global current_search_mac
        avg_rssi = float()
        device_read = False
        current_rssi = list()
        adv = bluetooth.get_advertisements()
        #-----------------------------------------------------------------------
        for device in adv:
            device_mac  = str(ubinascii.hexlify(device.mac).decode())
            if (device_mac == current_search_mac and not device_read):
                current_rssi.append(device.rssi)
        #-----------------------------------------------------------------------
        if (len(current_rssi) != 0):
            avg_rssi = sum(current_rssi)/len(current_rssi)
            green = (int((1-(avg_rssi/-93)) * 255) << 8)
            red = (int((avg_rssi/-93) * 255) << 16)
            pycom.rgbled(green+red)
            print(avg_rssi)
        #-----------------------------------------------------------------------
        time.sleep(2)
#===============================================================================
_thread.start_new_thread(th_func, ())
