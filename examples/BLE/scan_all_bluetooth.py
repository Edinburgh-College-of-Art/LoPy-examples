#===============================================================================
# This is a simple script that will send a value over BLE
# Use LightBlue for macOS to debug
#===============================================================================
from network import Bluetooth
import pycom
import ubinascii
import os
import machine
import time
# import _thread
#===============================================================================
pycom.heartbeat(False)
#===============================================================================
bluetooth = Bluetooth()
bluetooth.set_advertisement(name='Matt\'s LoPy 1',manufacturer_data='Pycom', service_data='Wibble')
bluetooth.start_scan(-1)
pycom.rgbled(0x00000f)  # Blue
#===============================================================================
# Deinfe Some Functions to get info about bluetooth devices

def get_all_devices():
    """
    print a list of all BLE devices advertising and return a list of the
    MAC Addresses as a binary string
    """
    print('####################################')
    mac_list = list()
    raw_macs = list()
    adv = bluetooth.get_advertisements()
    adv.sort(key=lambda tup: tup[3])
    for device in adv:
        device_mac  = str(ubinascii.hexlify(device.mac).decode())
        if (device_mac in mac_list or device_mac == '72c963984f31' or device_mac == '8c8590bdcedc'): #or device_mac == '8c8590bdcedc'
            pass
        else:
            raw_macs.append(device.mac)
            mac_list.append(device_mac)
            device_name = str(bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_NAME_CMPL))
            devie_rssi  = str(device.rssi)
            print (device_name + " " + device_mac + " " + devie_rssi)
            print ("binary mac: " + str(device.mac))
            print(bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_FLAG))
            print(bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_NAME_CMPL))
            #print(bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_TX_PWR))
            raw_mfg = bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_MANUFACTURER_DATA)
            if (raw_mfg[0:2] == b'L\x00'):
                print("Apple")
                print("Data Type: {} Data Bytes: {}".format(raw_mfg[2],raw_mfg[3]))
                #Apple service 180A: characteristic 2A24
            elif (raw_mfg[0:2] == b'\x06\x00'):
                print("Microsoft")
            print(len(raw_mfg[4:]))
            print(ubinascii.hexlify(raw_mfg[4:]))
            print("")
    return raw_macs
#===============================================================================
def connect_to_device(mac):
    """
    Attempt to connect to a BLE device. If it is an Apple device, pick out the service
    and characteristic associated with the model and print out the details

    The GATT connection needs to be disconnected at the end, otherwise the reference will be deleted
    but the connection will still be active. This will cause sonme odd behaviour
    """
    try:
        gatt_connection = bluetooth.connect(mac)
        print(ubinascii.hexlify(mac).decode())
        try:
            services = gatt_connection.services()
            for service in services:
                if (service.uuid() == 6154): # Apple service 180A: characteristic 2A24
                    characteristics = service.characteristics()
                    for characteristic in characteristics:
                        if (characteristic.uuid() == 10788):
                            print("Read characteristic: " + str(characteristic.read().decode()))
            gatt_connection.disconnect()
        except:
            gatt_connection.disconnect()
    except:
        print("cannot connect\n")
        if not bluetooth.isscanning(): # when a connection is unsuccessful, it will stop the scannning
            bluetooth.start_scan(-1)
#===============================================================================
def get_all_macs():
    """
    get a list of all available BLE MAC addresses as a binary string array
    """
    mac_list = list()
    raw_macs = list()
    adv = bluetooth.get_advertisements()
    for device in adv:
        device_mac  = str(ubinascii.hexlify(device.mac).decode())
        if (device_mac in mac_list):  # or device_mac == '72c963984f31' or device_mac == '8c8590bdcedc'
            pass
        else:
            raw_macs.append(device.mac)
            mac_list.append(device_mac)
    return raw_macs
#===============================================================================
def try_all_devices():
    """
    Attempt to connect to all BLE devices and print out some infor about them
    """
    macs = get_all_macs()
    for mac in macs:
        connect_to_device(mac)
    print('End Try All Devices')
    if not bluetooth.isscanning():
        bluetooth.start_scan(-1)
#===============================================================================
get_all_devices()
try_all_devices()
