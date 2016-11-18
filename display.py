#!/usr/bin/python3

import signal
import sys
import os
import time
import threading
import Adafruit_CharLCD as LCD


main_finished = False


RED     = (1.0, 0.0, 0.0)
GREEN   = (0.0, 1.0, 0.0)
BLUE    = (0.0, 0.0, 1.0)
YELLOW  = (1.0, 1.0, 0.0)
CYAN    = (0.0, 1.0, 1.0)
MAGENTA = (1.0, 0.0, 1.0)
WHITE   = (1.0, 1.0, 1.0)
BLACK   = (0.0, 0.0, 0.0)

# http://www.quinapalus.com/hd44780udg.html
MUSIC_NOTE  = (2, 3, 2, 2, 14, 30, 12, 0)
CHECK_MARK  = (0, 1, 3, 22, 28, 8, 0, 0)
CLOCK       = (0, 14, 21, 23, 17, 14, 0, 0)
HOURGLASS   = (31, 17, 10, 4, 10, 17, 31, 0)
ARROW_LEFT  = (2, 6, 10, 18, 10, 6, 2, 0)
ARROW_RIGHT = (8, 12, 10, 9, 10, 12, 8, 0)
DEGREE      = (14, 10, 14, 0, 0, 0, 0, 0)
FILL        = (31, 31, 31, 31, 31, 31, 31, 31)


def exit_blank(lcd):
    lcd.create_char(1, (31, 31, 31, 31, 31, 31, 31, 31))
    lcd.clear()
    lcd.message(('\x01' * 16) + '\n' + ('\x01' * 16))
    lcd.set_color(*BLACK)
    sys.exit(0)


def get_sighandler(lcd):
    def sighandler(signal, frame):
        exit_blank(lcd)
    return sighandler


def get_button_listener(lcd):
    def button_listener():
        colors = (RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE, BLACK)
        index = 0
        buttons = ( (LCD.SELECT, 'Select', (1,1,1)),
                    (LCD.LEFT,   'Left'  , (1,0,0)),
                    (LCD.UP,     'Up'    , (0,0,1)),
                    (LCD.DOWN,   'Down'  , (0,1,0)),
                    (LCD.RIGHT,  'Right' , (1,0,1)) )
        while not main_finished:
            # Loop through each button and check if it is pressed.
            for button in buttons:
                if lcd.is_pressed(button[0]):
                    lcd.set_color(*colors[index])
                    index += 1
                    if index == len(colors):
                        index = 0
                    time.sleep(0.25)
    return button_listener


def main():

    global main_finished

    # Initialize the LCD using the pins
    lcd = LCD.Adafruit_CharLCDPlate()
    lcd.set_color(*RED)
    signal.signal(signal.SIGINT, get_sighandler(lcd))

    threading.Thread(target=get_button_listener(lcd)).start()

    # create some custom characters
    lcd.create_char(1, DEGREE)
    lcd.create_char(2, FILL)

    lines = ['', '']
    lcd.clear()
    for line in sys.stdin:
        line = line.rstrip()
        line = line.replace('&deg;', '°')
        line = line.replace('°', '\x01')
        lcd.clear()
        lines = [lines[1], str(line[0:16])]
        lcd.message(lines[-2] + '\n' + lines[-1])

    main_finished = True


if __name__ =='__main__':
    main()
