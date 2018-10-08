#===============================================================================
# Helper Functions for debugging and learning the Pycom Lopy micropython platform
#===============================================================================
from machine import Pin
import os
#===============================================================================
def get_list_of_p_pins():
    """
    return a string list of P* number pins of Pycom Expanision board
    P0 and P1 appear to crash the board when declared

    P9 is attached to the onboard LED, setting LOW will turn it on
    """
    list_of_pins = []
    for number in range(2,24):
        list_of_pins.append('P' + str(number))
    return list_of_pins

def get_list_of_g_pins():
    """
    return a string list of G* number pins

    seems to freak out with G0 and G1
    """
    list_of_pins = []
    pin_indeces = list(range(2,18)) + [22,23,24,28,30,31]
    for index in pin_indeces:
        list_of_pins.append('G' + str(index))
    return list_of_pins

def get_exp_pin_map():
    """
    return a dictionary of the G pin to P pin map
    """
    list_of_pins = get_list_of_g_pins()
    pin_map = {}
    for g_pin in list_of_pins:
        pin_map[g_pin] = Pin(g_pin, mode=Pin.IN, pull=None, alt=-1).id()
    return pin_map

def set_all_pins(pin_value):
    """
    set all Expanision board pins to a value given by pin_value
    """
    list_of_pins = get_list_of_p_pins()
    for pin in list_of_pins:
        Pin(pin, mode=Pin.OUT, pull=None, alt=-1).value(pin_value)

def wipe_flash_storage():
    """format the internal storage"""
    os.mkfs('/flash') # format flash
