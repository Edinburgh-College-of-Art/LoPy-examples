#===============================================================================
# This is a simple script that will print out a list of BLE devices and some
# information about them
#
# This is triggered on a read request to the LoPy
#
# Use LightBlue for macOS to debug
#===============================================================================
from network import Bluetooth
import pycom
import ubinascii
import machine
#===============================================================================
pycom.heartbeat(False)
#===============================================================================
bluetooth = Bluetooth()
bluetooth.set_advertisement(name='LoPy',manufacturer_data='Pycom', service_data='BLE')
bluetooth.start_scan(-1)
pycom.rgbled(0x00007f)  # Blue
#===============================================================================
srv1 = bluetooth.service(uuid=b'1234567890123456', isprimary=True)
char1 = srv1.characteristic(uuid=b'ab34567890123456', value='LoPy_BLE')
#===============================================================================
def char1_cb_handler(char1):
    global char1_read_counter
    print('####################################')
    mac_list = list()
    adv = bluetooth.get_advertisements()
    adv.sort(key=lambda tup: tup[3])
    for device in adv:
        device_mac  = str(ubinascii.hexlify(device.mac).decode())
        if (device_mac in mac_list or device_mac == '72c963984f31' or device_mac == '8c8590bdcedc'): #or device_mac == '8c8590bdcedc'
            pass
        else:
            mac_list.append(device_mac)
            device_name = str(bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_NAME_CMPL))
            devie_rssi  = str(device.rssi)
            print ("Name: " + device_name + " MAC: " + device_mac + " RSSI: " + devie_rssi)
            print(bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_FLAG))
            print(bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_NAME_CMPL))
            #print(bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_TX_PWR))
            raw_mfg = bluetooth.resolve_adv_data(device.data, Bluetooth.ADV_MANUFACTURER_DATA)
            if (raw_mfg[0:2] == b'L\x00'):
                print("Apple")
                print("Data Type: {} Data Bytes: {}".format(raw_mfg[2],raw_mfg[3]))
            elif (raw_mfg[0:2] == b'\x06\x00'):
                print("Microsoft")
            print(ubinascii.hexlify(raw_mfg[4:]))
            print("")
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
