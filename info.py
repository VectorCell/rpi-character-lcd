#!/usr/bin/python3


import sys
import time
import urllib.request


WEATHER_URL_AUSTIN = "http://forecast.weather.gov/MapClick.php?lat=30.349290869878814&lon=-97.77015612070767#.WC7jTbWVsTs"


def emit_weather():
    temperatures = []
    conditions = []
    def isolate_text(line):
        line = line[line.index('>') + 1:]
        line = line[:line.index('<')]
        return line
    f = urllib.request.urlopen(WEATHER_URL_AUSTIN)
    for line in f.read().decode('utf-8').splitlines():
        if 'myforecast-current-lrg' in line:
            temperatures += [isolate_text(line)]
        elif 'myforecast-current-sm' in line:
            temperatures += [isolate_text(line)]
        elif 'myforecast-current' in line:
            conditions += [isolate_text(line)]
    for t in temperatures:
        print(t, end=' ')
    print()
    for c in conditions:
        print(c, end=' ')
    print(flush=True)


def main():
    while True:
        emit_weather()
        time.sleep(60.0)


if __name__ =='__main__':
    main()
