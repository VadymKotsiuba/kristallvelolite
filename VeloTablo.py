import sys
import datetime
import serial
import time
from PIL import *
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import SDL_DS3231
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from os import system

serial_port = '/dev/ttyS0'
serial_speed = 9600

font_name = "/home/pi/kristallvelolite/MyFont.ttf"
font_size = 40
medium_font_size = 30
small_font_size = 15
color1 = "#ff0000"
color2 = "#00ff00"

last_count = 0
new_count = 0
count = {"today 1": 0, "all 1": 0, "today 2": 0, "all 2": 0}
error = [0, 0]
temperature = -25
rtc_str = "  15:15\n 01.01.19"

isFirstTemp = True

restartCommand = 'sudo python3 /home/pi/kristallvelolite/VeloTablo.py'


def print_matrix(block, text, color, varFont):
    global toolDraw

    text_w, text_h = toolDraw.multiline_textsize(text, font=varFont)
    if block in {0, 1, 6, 7}:
        x_center = (63 - text_w)/2
        toolDraw.rectangle([block * 64, 0, block * 64 + 63, 31], fill='black')
        y_center = (31 - text_h) / 2
    else:
        x_center = (127 - text_w)/2
        toolDraw.rectangle([block * 64, 0, block * 64 + 127, 31], fill='black')
        y_center = (31 - text_h) / 2 - 2
    #for i in range(12):
    #    if i == 0 or i == 6 or i % 2 != 0:
    #        toolDraw.line([i*64+63, 0, i*64+63, 31], fill='white')
    toolDraw.multiline_text((block*64+x_center, y_center), text, font=varFont, fill=color)


def init():
    global toolDraw
    global myFont, myFontSmall, myFontMedium
    global rtcString
    global sec
    global matrix
    global ds3231
    global COMport
    global buffer
    global rtc_str

    time.sleep(5)

    dataFile = open("/home/pi/kristallvelolite/count.txt", "r")
    data = dataFile.readlines()
    for i, temp in enumerate(data):
        record = list(map(int, temp.split()))
        key1 = "today "+str(i+1)
        key2 = "all " + str(i + 1)
        count[key1] = record[0]
        count[key2] = record[1]
    dataFile.close()
    
# Vlad 11.06.2020
    try:
      COMport = serial.Serial(serial_port, serial_speed, timeout=None)
      print(serial_port)
    except:
      COMport = serial.Serial("/dev/ttyUSB1", serial_speed, timeout=None)
      print('ComPort ttyUSB1')
############################## 
    COMport.close()
    COMport.open() #Vlad 11.06.2020
    COMport.reset_input_buffer()

    myFont = ImageFont.truetype(font_name, font_size)
    myFontSmall = ImageFont.truetype(font_name, small_font_size)
    myFontMedium = ImageFont.truetype(font_name, medium_font_size)

    buffer = Image.new("RGB", (768, 32), "black")
    toolDraw = ImageDraw.Draw(buffer)
    print_matrix(0, "   15:19\n 06.06.19", color1, myFontSmall)
    print_matrix(1, str(temperature)+"°C", color1, myFontMedium)
    print_matrix(2, str(count["today 1"]), color1, myFont)
    print_matrix(4, str(count["all 1"]), color2, myFont)
    print_matrix(6, "   15:19\n 06.06.19", color1, myFontSmall)
    print_matrix(7, str(temperature)+"°C", color1, myFontMedium)
    print_matrix(8, str(count["today 2"]), color1, myFont)
    print_matrix(10, str(count["all 2"]), color2, myFont)

    sec = 0

    ds3231 = SDL_DS3231.SDL_DS3231(1, 0x68)
    rtc_str = ds3231.read_str()

    matrix_options = RGBMatrixOptions()
    matrix_options.rows = 32
    matrix_options.cols = 64
    matrix_options.chain_length = 12
    matrix_options.parallel = 1
    matrix_options.multiplexing = 1
    matrix_options.hardware_mapping = 'adafruit-hat'
    matrix_options.gpio_slowdown = 2
    matrix_options.pwm_bits = 1
    #matrix_options.pwm_dither_bits = 1
    matrix_options.brightness = 100
    matrix_options.pwm_lsb_nanoseconds = 350
    matrix = RGBMatrix(options = matrix_options)
    matrix.SetImage(buffer, 0, 0)


def updateImage():
    print_matrix(0, rtc_str, color1, myFontSmall)
    print_matrix(1, str(temperature)+"°C", color1, myFontMedium)
    print_matrix(2, str(count["today 1"]+count["today 2"]), color1, myFont)
    print_matrix(4, str(count["all 1"]+count["all 2"]), color2, myFont)
    print_matrix(6, rtc_str, color1, myFontSmall)
    print_matrix(7, str(temperature)+"°C", color1, myFontMedium)
    print_matrix(8, str(count["today 2"]+count["today 1"]), color1, myFont)
    print_matrix(10, str(count["all 2"]+count["all 1"]), color2, myFont)

    matrix.SetImage(buffer, 0, 0)
    
    system("clear")
    print(rtc_str)
    print(str(temperature)+"°C")
    print(str(count["today 1"]+count["today 2"]))
    print(str(count["all 1"]+count["all 2"]))


def readData():
    global dataSerial
    global rtc_str
    global temperature
    global new_count
    global isFirstTemp

    rtc_str = ds3231.read_str()
#    try:
    if COMport.is_open:
        if COMport.in_waiting >= 2:
            dataSerial = COMport.read(2)
    #           COMport.close()
            print(dataSerial)
            if dataSerial[0] == 0x00:
                key1 = "today " + str(dataSerial[1])
                key2 = "all " + str(dataSerial[1])
                count[key1] += 1
                count[key2] += 1
                error[0] = 0
                error[1] = 0
                new_count += 1
            if dataSerial[0] == 1 or dataSerial[0] == 2:
                sign = 1 #13:54 16.11.2020 Vadym Kotsiuba
                if dataSerial[0] == 2: #13:54 16.11.2020 Vadym Kotsiuba
                    sign = -1
                dT = abs(temperature - (dataSerial[1]*sign)) #13:54 16.11.2020 Vadym Kotsiuba
                if dataSerial[1] != 0 and -20<dataSerial[1]<40 and isFirstTemp == True:
                    temperature = dataSerial[1]
                    isFirstTemp = False
                if dT <= 3:
                    temperature = dataSerial[1]
                temperature *= sign #13:54 16.11.2020 Vadym Kotsiuba
#    except:
#    print('ComPort error')
#     COMport.close()
#     subprocess.call(['open', '-W', '-a', 'lxterminal', 'python3', '--args', '/home/pi/kristallvelolite/VeloTablo.py'])
#     exit()
#     init()


def timeUpdate():
    global sec
    time.sleep(0.1)
    sec += 1


def checkUpdateFiles():
    global last_count
    if new_count-last_count >= 10:
        dataFile = open("/home/pi/kristallvelolite/count.txt", "w")
        dataFile.write(str(count["today 1"]) + " " + str(count["all 1"]) + "\n")
        dataFile.write(str(count["today 2"]) + " " + str(count["all 2"]))
        dataFile.close()
        last_count = new_count
    hours = ds3231.read_hours()
    if hours in (8, 12, 16, 20, 23):
        dataFile = open("/home/pi/kristallvelolite/count.txt", "w")
        dataFile.write(str(count["today 1"]) + " " + str(count["all 1"]) + "\n")
        dataFile.write(str(count["today 2"]) + " " + str(count["all 2"]))
        dataFile.close()
        last_count = new_count



def checkResetCounterFromDate():
    DMY = ds3231.read_DMY()
    dataFile = open("/home/pi/kristallvelolite/last_date.txt", "r")
    data = dataFile.readlines()
    dataFile.close()
    date_bytes = list(map(int, data[0].split(' ')))
    if date_bytes[0] != DMY["DAY"] or date_bytes[1] != DMY["MONTH"] or date_bytes[2] != DMY["YEAR"]:
        count["today 1"] = 0
        count["today 2"] = 0
        dataFile = open("/home/pi/kristallvelolite/count.txt", "w")
        dataFile.write(str(count["today 1"]) + " " + str(count["all 1"]) + "\n")
        dataFile.write(str(count["today 2"]) + " " + str(count["all 2"]))
        dataFile.close()
        dataFile = open("/home/pi/kristallvelolite/last_date.txt", "w")
        dataFile.write(str(DMY["DAY"]) + " " + str(DMY["MONTH"]) + " " + str(DMY["YEAR"]))
        dataFile.close()

init()

while 1:
    timeUpdate()
    readData()
    if sec >= 5:
        updateImage()
        sec = 0
    checkUpdateFiles()
    checkResetCounterFromDate()
