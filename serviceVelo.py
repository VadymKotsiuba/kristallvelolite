#!/usr/bin/env python
#
# Test SDL_DS3231
# John C. Shovic, SwitchDoc Labs
# 08/03/2014
#
#

# imports

import sys
import time
import datetime
import random
import SDL_DS3231

# Main Program

ds3231 = SDL_DS3231.SDL_DS3231(1, 0x68)
#comment out the next line after the clock has been initialized
#ds3231.write_all(date=12, month=12, year=19, hours=16, minutes=15, seconds=0)

work = True

def setTime():
    temp_str = input("Inpute RTC date, DD MM YY HH MM: ")
    rtcBytes = list(map(int, temp_str.split(' ')))
    ds3231.write_all(date = rtcBytes[0], month=rtcBytes[1], year=rtcBytes[2], hours=rtcBytes[3], minutes=rtcBytes[4], seconds=0)
    print("The time has been set")
    
def resetCounter():
    accept = input("Do you want reset counter file?(y/n)")
    if accept == "y":
        dataFile = open("/home/pi/kristallvelolite/count.txt", "w")
        dataFile.write(str(0) + " " + str(0) + "\n")
        dataFile.write(str(0) + " " + str(0))
        dataFile.close()
        print("The counter file has been reset.")
    else:
        print("You canceled the decision.")

while work:
    print("1-Print RTC data | 2 - Set RTC Data | 3 - Reset Counter File | 4 - Exit")
    choose = int(input("Select action: "));
    if choose == 1:
        print(ds3231.read_str())
    if choose == 2:
        setTime()
    if choose == 3:
        resetCounter()
    if choose == 4:
        work = False

exit()