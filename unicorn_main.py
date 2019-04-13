#!/usr/bin/env python

#  _    _       _                      _           _     _    _ _____   
# | |  | |     (_)                    | |         | |   | |  | |  __ \  
# | |  | |_ __  _  ___ ___  _ __ _ __ | |__   __ _| |_  | |__| | |  | | 
# | |  | | '_ \| |/ __/ _ \| '__| '_ \| '_ \ / _` | __| |  __  | |  | | 
# | |__| | | | | | (_| (_) | |  | | | | | | | (_| | |_  | |  | | |__| | 
#  \____/|_| |_|_|\___\___/|_|  |_| |_|_| |_|\__,_|\__| |_|  |_|_____/  
#                                                                       
#  _____                 _                         _                 _ _          _   _             
# |  __ \               | |                       (_)               | (_)        | | (_)            
# | |__) |__ _ _ __   __| | ___  _ __ ___   __   ___ ___ _   _  __ _| |_ ______ _| |_ _  ___  _ __  
# |  _  // _` | '_ \ / _` |/ _ \| '_ ` _ \  \ \ / / / __| | | |/ _` | | |_  / _` | __| |/ _ \| '_ \ 
# | | \ \ (_| | | | | (_| | (_) | | | | | |  \ V /| \__ \ |_| | (_| | | |/ / (_| | |_| | (_) | | | |
# |_|  \_\__,_|_| |_|\__,_|\___/|_| |_| |_|   \_/ |_|___/\__,_|\__,_|_|_/___\__,_|\__|_|\___/|_| |_|
#                                                                                                   
# Uses pip install unicorn-hat-sim                                                                                                 

"""Main script for running random visualizations on Unicornhat HD"""

import unicorn_config as conf
import random
import time
import datetime as dt
import colorsys
from datetime import datetime
from sys import exit
import math
from random import randint

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    exit('This script requires the pillow module\nInstall with: sudo pip install pillow')

try:
    import unicornhathd as unicorn
    print("Unicorn hat hd detected")
except ImportError:
    from unicorn_hat_sim import unicornhathd as unicorn

#*********************************
# Brigthness
#*********************************
def SetUnicornBrightness():

    unicorn.brightness(0.6)

    return 0

#*********************************
# Random numbers
#*********************************
def RandomNum (stop):

    num = random.randrange(0, stop)

    return num

#*********************************
# 
#*********************************
def set_pixel(b, x, y, v):
    b[y * 16 + x] = int(v)

#*********************************
# 
#*********************************
def get_pixel(b, x, y):
    # out of range sample lookup
    if x < 0 or y < 0 or x >= 16 or y >= 16:
        return 0

    # subpixel sample lookup
    if isinstance(x, float) and x < 15:
        f = x - int(x)
        return (b[int(y) * 16 + int(x)] * (1.0 - f)) + (b[int(y) * 16 + int(x) + 1] * (f))

    # fixed pixel sample lookup
    return b[int(y) * 16 + int(x)]

#*********************************
# Candle
#*********************************
def UnicornCandle():
    print("Showing candle")

    unicorn.rotation(270)
    width, height = unicorn.get_shape()
    # buffer to contain candle "heat" data
    candle = [0] * 256

    # create a palette for mapping heat values onto colours
    palette = [0] * 256
    for i in range(0, 256):
        h = i / 5.0
        h /= 360.0
        s = (1.0 / (math.sqrt(i / 50.0) + 0.01))
        s = min(1.0, s)
        s = max(0.0, s)

        v = i / 200.0
        if i < 60:
            v = v / 2
        v = min(1.0, v)
        v = max(0.0, v)

        r, g, b = colorsys.hsv_to_rgb(h, s, v)
        palette[i] = (int(r * 255.0), int(g * 255.0), int(b * 255.0))

    step = 0
    currentPos = 1
    try:
        while currentPos <= conf.CANDLE_LENGHT:
            # step for waving animation, adds some randomness
            step += randint(0, 15)

            # clone the current candle
            temp = candle[:]

            # seed new heat
            v = 500

            set_pixel(candle, 6, 15, v)
            set_pixel(candle, 7, 15, v)
            set_pixel(candle, 8, 15, v)
            set_pixel(candle, 9, 15, v)
            set_pixel(candle, 6, 14, v)
            set_pixel(candle, 7, 14, v)
            set_pixel(candle, 8, 14, v)
            set_pixel(candle, 9, 14, v)

            # blur, wave, and shift up one step
            for x in range(0, 16):
                for y in range(0, 16):
                    s = math.sin((y / 30.0) + (step / 10.0)) * ((16 - y) / 20.0)
                    v = 0
                    for i in range(0, 3):
                        for j in range(0, 3):
                            # r = randint(0, 2) - 1
                            v += get_pixel(candle, x + i + s - 1, y + j)

                    v /= 10
                    set_pixel(temp, x, y, v)

            candle = temp

            # copy candle into UHHD with palette
            for x in range(0, 16):
                for y in range(0, 16):
                    o = (i * 3) + 1
                    r, g, b = palette[max(0, min(255, get_pixel(candle, x, y)))]
                    unicorn.set_pixel(x, y, r, g, b)

            unicorn.show()
            currentPos=currentPos+1
        unicorn.off()
    finally:
        unicorn.off()
    return 0
#*********************************
# Show date and time
#*********************************
def UnicornTimeShow():

    print ("Scrolling time and date")
    
    unicorn.rotation(270)
    lines =[dt.datetime.now().strftime('%H : %M'), dt.datetime.now().strftime('%a %e %B %Y')]

    colours = [tuple([int(n * 255) for n in colorsys.hsv_to_rgb(x / float(len(lines)), 1.0, 1.0)]) for x in range(len(lines))]

    FONT = ('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 12)

    width, height = unicorn.get_shape()

    text_x = width
    text_y = 2

    font_file, font_size = FONT

    font = ImageFont.truetype(font_file, font_size)

    text_width, text_height = width, 0

    lines =[dt.datetime.now().strftime('%H : %M'), dt.datetime.now().strftime('%a %e %B %Y')]

    colours = [tuple([int(n * 255) for n in colorsys.hsv_to_rgb(x / float(len(lines)), 1.0, 1.0)]) for x in range(len(lines))]
    try:
        for line in lines:
            w, h = font.getsize(line)
            text_width += w + width
            text_height = max(text_height, h)

        text_width += width + text_x + 1

        image = Image.new('RGB', (text_width, max(16, text_height)), (0, 0, 0))
        draw = ImageDraw.Draw(image)

        offset_left = 0

        for index, line in enumerate(lines):
            draw.text((text_x + offset_left, text_y), line, colours[index], font=font)

            offset_left += font.getsize(line)[0] + width

        for scroll in range(text_width - width):
            for x in range(width):
                for y in range(height):
                    pixel = image.getpixel((x + scroll, y))
                    r, g, b = [int(n) for n in pixel]
                    unicorn.set_pixel(width - 1 - x, y, r, g, b)

            unicorn.show()
            time.sleep(0.01)

    finally:
        unicorn.off()
    return 0
    
#*********************************
# Scroll text
#*********************************
def UnicornTextScroll():

    TEXT_FULL = conf.SCROLL_TEXT_RND
    TEXT_LEN = RandomNum(len(TEXT_FULL))
    TEXT = TEXT_FULL[TEXT_LEN]
    print ("Scrolling text: " + TEXT)

    #TEXT = conf.SCROLL_TEXT
    FONT = ('/usr/share/fonts/truetype/freefont/FreeSansBold.ttf', 12)

    width, height = unicorn.get_shape()

    unicorn.rotation(270)

    text_x = 1
    text_y = 2

    font_file, font_size = FONT
    font = ImageFont.truetype(font_file, font_size)
    text_width, text_height = font.getsize(TEXT)
    text_width += width + text_x
    image = Image.new('RGB', (text_width, max(height, text_height)), (0, 0, 0))
    draw = ImageDraw.Draw(image)
    draw.text((text_x, text_y), TEXT, fill=(255, 255, 255), font=font)

    for scroll in range(text_width - width):
        for x in range(width):
            hue = (x + scroll) / float(text_width)

            br, bg, bb = [int(n * 255) for n in colorsys.hsv_to_rgb(hue, 1.0, 1.0)]

            for y in range(height):

                pixel = image.getpixel((x + scroll, y))

                r, g, b = [float(n / 255.0) for n in pixel]

                r = int(br * r)
                g = int(bg * g)
                b = int(bb * b)
                unicorn.set_pixel(width - 1 - x, y, r, g, b)

        unicorn.show()

        # And sleep for a little bit, so it doesn't scroll too quickly!
        time.sleep(0.02)

    unicorn.off()

    return 0

# *****************************
# Starfield
# *****************************
def UnicornStarfield():

    print ("Running starfield")

    unicorn.rotation(270)
    
    lenght = conf.STARFIELD_LENGHT
    current_pos = 1
    star_count = 25
    star_speed = 0.05
    stars = []

    for i in range(0, star_count):
        stars.append((random.uniform(4, 11), random.uniform(4, 11), 0))

    while current_pos <= lenght:
        unicorn.clear()
        for i in range(0, star_count):
            stars[i] = (
                stars[i][0] + ((stars[i][0] - 8.1) * star_speed),
                stars[i][1] + ((stars[i][1] - 8.1) * star_speed),
                stars[i][2] + star_speed * 50)
            if stars[i][0] < 0 or stars[i][1] < 0 or stars[i][0] > 16 or stars[i][1] > 16:
                stars[i] = (random.uniform(4, 11), random.uniform(4, 11), 0)
            v = stars[i][2]
            unicorn.set_pixel(stars[i][0], stars[i][1], v, v, v)
        unicorn.show()
        current_pos=current_pos+1
        #print(current_pos)
    unicorn.clear()
    unicorn.off()
    return 0
#*********************************
# Matrix
#*********************************
def UnicornMatrix():

    print ("Running matrix")
    
    unicorn.rotation(90)
    lenght = conf.MATRIX_LENGHT
    current_pos = 1
    
    wrd_rgb = [
        [154, 173, 154], [0, 255, 0], [0, 235, 0], [0, 220, 0],
        [0, 185, 0], [0, 165, 0], [0, 128, 0], [0, 0, 0],
        [154, 173, 154], [0, 145, 0], [0, 125, 0], [0, 100, 0],
        [0, 80, 0], [0, 60, 0], [0, 40, 0], [0, 0, 0]
    ]

    clock = 0

    blue_pilled_population = [[randint(0, 15), 15]]

    while (current_pos<=lenght):
        for person in blue_pilled_population:
            y = person[1]
            for rgb in wrd_rgb:
                if (y <= 15) and (y >= 0):
                    unicorn.set_pixel(person[0], y, rgb[0], rgb[1], rgb[2])
                y += 1
            person[1] -= 1
        unicorn.show()
        time.sleep(0.1)
        clock += 1

        if clock % 5 == 0:
            blue_pilled_population.append([randint(0, 15), 15])
        if clock % 7 == 0:
            blue_pilled_population.append([randint(0, 15), 15])

        while len(blue_pilled_population) > 100:
            blue_pilled_population.pop(0)
        current_pos=current_pos+1
    unicorn.off()
    return 0

#*********************************
# Image
#*********************************
def UnicornImage():
    print ("Showing image "+conf.IMAGE_NAME)

    unicorn.rotation(0)

    lenght = conf.IMAGE_LENGHT
    current_pos = 1
    
    width, height = unicorn.get_shape()

    img = Image.open(conf.IMAGE_NAME)


    while current_pos<=lenght:
        for o_x in range(int(img.size[0] / width)):
            for o_y in range(int(img.size[1] / height)):

                valid = False
                for x in range(width):
                    for y in range(height):
                        pixel = img.getpixel(((o_x * width) + y, (o_y * height) + x))
                        r, g, b = int(pixel[0]), int(pixel[1]), int(pixel[2])
                        if r or g or b:
                            valid = True
                        unicorn.set_pixel(x, y, r, g, b)

                if valid:
                    unicorn.show()
                    time.sleep(0.5)
        current_pos=current_pos+1

    unicorn.off()

    return 0

# ****************************************************************
# ***************************** MAIN *****************************
# ****************************************************************
visualizations = {0:UnicornTimeShow,
                  1:UnicornTextScroll,
                  2:UnicornStarfield,
                  3:UnicornMatrix,
                  4:UnicornImage,
                  5:UnicornCandle}


print("********* START *********")
print ("Visualizations: " + str(visualizations))
print ("Wait seconds: " + str(conf.WAIT_BETWEEN_SEC))

random.seed()

try:
    while True:
        runVis = RandomNum(len(visualizations))
        print (runVis)

        print(visualizations[runVis])
        SetUnicornBrightness()
        visualizations[runVis]()
        print (str(dt.datetime.now()) + ' - Waiting for ' + str(conf.WAIT_BETWEEN_SEC) + ' second(s)')
        time.sleep (conf.WAIT_BETWEEN_SEC)
except KeyboardInterrupt:
    unicorn.off()


