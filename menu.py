#!/usr/bin/python3

import signal
import sys
import os
import time
import datetime
import string
import urllib.request
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

buttons = ( (LCD.SELECT, 'Select', RED),
            (LCD.LEFT,   'Left',   GREEN),
            (LCD.UP,     'Up',     BLUE),
            (LCD.DOWN,   'Down',   YELLOW),
            (LCD.RIGHT,  'Right',  CYAN))

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


def printlog(*t, **d):
    print('[{}]'.format(time.strftime('%Y-%m-%d_%H:%M:%S')), end=' ')
    def str_to_bytearray(s):
        if not isinstance(s, str):
            return s
        for c in s:
            if c not in string.printable:
                return bytearray(s, 'utf-8')
        return s
    def reform_bytearray(ba):
        if not isinstance(ba, bytearray):
            return ba
        return str(ba)[len('bytearray('):][:-1]
    tcopy = tuple(reform_bytearray(str_to_bytearray(e)) for e in t)
    print(*tcopy, **d)


class Module:

    def __init__(self, lcd):
        raise NotImplementerError('this is an abstract constructor')

    def update(self, force = False):
        raise NotImplementerError('update is an abstract method')

    def show(self):
        raise NotImplementerError('update is an abstract method')

    def hide(self):
        raise NotImplementerError('update is an abstract method')



class ModuleTime(Module):

    def __init__(self, lcd):
        self.lcd = lcd
        self.cache = None
        self.last_update = 0
        self.visible = False

    def __need_update(self):
        # always
        return True
        # every second
        #return self.visible and (not self.cache or (int(time.time()) > (self.last_update)))

    def update(self, force = False):
        if self.__need_update() or force:
            new = time.strftime('%Y %b %d, %a\n%-I:%M:%S %p')
            if new == self.cache:
                return False
            self.cache = new
            self.last_update = int(time.time())
            return True
        return False

    def show(self):
        if not self.visible:
            printlog('show time')
            self.lcd.clear()
            self.visible = True
        self.update()
        self.lcd.home()
        #self.lcd.set_color(*WHITE)
        self.lcd.message(self.cache)

    def hide(self):
        self.visible = False


class ModuleTimeNoSeconds(Module):

    def __init__(self, lcd):
        self.lcd = lcd
        self.cache = None
        self.last_update = 0
        self.visible = False

    def __need_update(self):
        # every minute
        return self.visible and (not self.cache or (int(time.time()) > (self.last_update + 60)))

    def update(self, force = False):
        if self.__need_update() or force:
            new = time.strftime('%Y %b %d, %a\n%-I:%M %p')
            if new == self.cache:
                return False
            self.cache = new
            self.last_update = int(time.time())
            return True
        return False

    def show(self):
        if not self.visible:
            printlog('show time (no seconds)')
            self.lcd.clear()
            self.visible = True
        self.update()
        self.lcd.home()
        #self.lcd.set_color(*WHITE)
        self.lcd.message(self.cache)

    def hide(self):
        self.visible = False


class ModuleWeather(Module):

    def __init__(self, lcd):
        self.lcd = lcd
        self.url = "http://forecast.weather.gov/MapClick.php?lon=-97.74928981475828&lat=30.35843540042552#.WC_tULWVsTs"
        self.cache = None
        self.last_update = 0
        self.visible = False

    def __need_update(self):
        # every 15 minutes
        return self.visible and (not self.cache or (int(time.time()) > (self.last_update + 15 * 60)))

    def update(self, force = False):
        if self.__need_update() or force:
            self.lcd.clear()
            #self.lcd.set_color(*YELLOW)
            self.lcd.message('LOADING WEATHER')
            temperatures = []
            conditions = []
            def isolate_text(line):
                line = line[line.index('>') + 1:]
                line = line[:line.index('<')]
                return line
            f = urllib.request.urlopen(self.url)
            for line in f.read().decode('utf-8').splitlines():
                if 'myforecast-current-lrg' in line:
                    temperatures += [isolate_text(line)]
                elif 'myforecast-current-sm' in line:
                    temperatures += [isolate_text(line)]
                elif 'myforecast-current' in line:
                    conditions += [isolate_text(line)]
            output = '\n'.join((' '.join(temperatures).strip(), ' '.join(conditions).strip()))
            output = ''.join(c for c in output if c in string.printable)
            output = output.replace('&deg;', '°').replace('°', '\x01')
            printlog(output)
            self.cache = output
            self.last_update = int(time.time())
            return True
        return False

    def show(self):
        if not self.visible:
            printlog('show weather')
            self.lcd.clear()
            self.visible = True
        self.update()
        #self.lcd.set_color(*CYAN)
        self.lcd.clear()
        self.lcd.message(self.cache)

    def hide(self):
        self.visible = False


def main():

    # Initialize the LCD using the pins
    lcd = LCD.Adafruit_CharLCDPlate()
    lcd.set_color(*RED)
    signal.signal(signal.SIGINT, get_sighandler(lcd))

    # create some custom characters
    lcd.create_char(1, DEGREE)
    lcd.create_char(2, FILL)

    colors = (RED, GREEN, BLUE, YELLOW, CYAN, MAGENTA, WHITE, BLACK)
    color_idx = 0

    modules = (ModuleTime(lcd), ModuleTimeNoSeconds(lcd), ModuleWeather(lcd))
    mod_idx = 1
    stopped = False
    force_update = False
    delay = 0.1
    modules[mod_idx].show()
    while not stopped:
        if lcd.is_pressed(LCD.DOWN) or lcd.is_pressed(LCD.UP):
            modules[mod_idx].hide()
            if lcd.is_pressed(LCD.DOWN):
                mod_idx += 1
                if mod_idx == len(modules):
                    mod_idx = 0
            elif lcd.is_pressed(LCD.UP):
                mod_idx -= 1
                if mod_idx < 0:
                    mod_idx = len(modules) - 1
            modules[mod_idx].show()
        elif lcd.is_pressed(LCD.LEFT) and lcd.is_pressed(LCD.RIGHT):
            printlog('stop')
            stopped = True
            continue
        elif lcd.is_pressed(LCD.LEFT) or lcd.is_pressed(LCD.RIGHT):
            if lcd.is_pressed(LCD.LEFT):
                color_idx -= 1
                if color_idx < 0:
                    color_idx = len(colors) - 1
            elif lcd.is_pressed(LCD.RIGHT):
                color_idx += 1
                if color_idx == len(colors):
                    color_idx = 0
            printlog('set color:', ''.join(e for e in globals() if globals()[e] == colors[color_idx]))
            lcd.set_color(*colors[color_idx])
            time.sleep(0.25)
            continue
        elif lcd.is_pressed(LCD.SELECT):
            printlog('force update to current module')
            force_update = True
        time.sleep(delay)

        # request module update every iteration
        if modules[mod_idx].update(force = force_update):
            modules[mod_idx].show()

        force_update = False

    exit_blank(lcd)


if __name__ =='__main__':
    main()
