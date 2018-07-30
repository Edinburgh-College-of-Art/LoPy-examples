#===============================================================================
# This is a simple script that will provide a value to be read over BLE
#
# For macOS you can use the LightBlue app to observe
#
# service characteristics are a maximum 2 bytes in size (i.e. 0xFFFF is the max value)
#===============================================================================
from network import Bluetooth
import pycom
import machine
#===============================================================================
pycom.heartbeat(False)
#===============================================================================
bluetooth = Bluetooth()
bluetooth.set_advertisement(name='LoPy',manufacturer_data='Pycom', service_data='Blutooth Low Energy')
bluetooth.start_scan(-1) # scan forever
pycom.rgbled(0x00007f)   # Blue
#===============================================================================
init_value = 0x20
char1_read_counter = 0
#===============================================================================
# UUID are READ LSB first (little endian)
# i.e.
# b'BLUTOOTH_SERVICE' = b'424c55544f4f54485f53455256494345'
# will appear as 45434956-5245-535F-4854-4F4F54554C42
b'BLUTOOTH_SERVICE'
srv1 = bluetooth.service(uuid=b'BLUTOOTH_SERVICE', isprimary=True)
char1 = srv1.characteristic(uuid=b'CHARACTERISTIC!!', value=40)
char1.value(init_value)
#===============================================================================
def char1_cb_handler(char1):
    global char1_read_counter
    events = char1.events()
    if  events & Bluetooth.CHAR_WRITE_EVENT:
        print("Write request with value = {}".format(char1.value()))
    if (char1_read_counter < 1):
        print('Read request on char 1')
    else:
        print('Read request on char 1')
        char1.value(init_value + char1_read_counter) # overwrite the characteristic value
    char1_read_counter += 1
#===============================================================================
char1.callback(trigger=Bluetooth.CHAR_WRITE_EVENT | Bluetooth.CHAR_READ_EVENT, handler=char1_cb_handler)
srv1.start()
#===============================================================================
# Call back triggered on connection events
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
