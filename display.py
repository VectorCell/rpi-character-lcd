#!/usr/bin/python3

import signal
import sys
import os
import time
import threading
import Adafruit_CharLCD as LCD


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
        sys.exit(0)
    return sighandler


def reform_line(line):
    line = line.rstrip()
    line = line.replace('&deg;', '°')
    line = line.replace('°', '\x01')
    if len(line) < 16:
        line += ' ' * (16 - len(line))
    elif len(line) > 16:
        line = line[:16]
    return line


def process_cmd(lcd, line, lines):
    line = line.strip()
    if line.startswith('cmd.'):
        cmd = line[len('cmd.'):]
        if cmd.startswith('color.'):
            color = cmd[len('color.'):].upper()
            lcd.set_color(*globals()[color])
        elif cmd == 'clear':
            for i in range(len(lines)):
                lines[i] = ''
            lcd.clear()
        elif cmd == 'exit':
            sys.exit(0)
        return True
    return False


def main():

    # number of lines to read at a time (2 is faster)
    n_feed_lines = 1
    for arg in sys.argv:
        if arg == '-2':
            n_feed_lines = 2

    # Initialize the LCD using the pins
    lcd = LCD.Adafruit_CharLCDPlate()
    lcd.set_color(*RED)
    lcd.clear()

    signal.signal(signal.SIGINT, get_sighandler(lcd))

    # create some custom characters
    lcd.create_char(1, DEGREE)

    if n_feed_lines == 1:
        lines = ['', '']
        for line in sys.stdin:
            if not process_cmd(lcd, line, lines):
                line = reform_line(line)
                lines = [lines[1], line]
                lcd.clear()
                lcd.message(lines[-2] + '\n' + lines[-1])
    elif n_feed_lines == 2:
        buf = ['', '']
        buf_full = True
        for line in sys.stdin:
            if not process_cmd(lcd, line, lines):
                if buf_full:
                    buf[0] = reform_line(line)
                    buf_full = False
                else:
                    buf[1] = reform_line(line)
                    buf_full = True
                    lcd.clear()
                    lcd.message('\n'.join(buf))


if __name__ =='__main__':
    main()
