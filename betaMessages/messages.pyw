import os
import cv2
import sys
import numpy as np
import time
from PIL import Image, ImageChops
import base64
import re
from subprocess import check_output
import psutil
import threading
import locale
locale.setlocale(locale.LC_ALL, 'C')
import tesserocr
from tesserocr import OEM, PSM
import datetime


Heko = cv2.imread('Heko.png',0)
guild = cv2.imread('guild.png',0)

def get_pid(name):
    for proc in psutil.process_iter():
        if name in proc.name():
           pid = proc.pid
           return pid

#get connection to emulator
if os.path.exists('settings.txt'):
    file = open('settings.txt')
    path = file.read()
    path = path.strip()
    file.close()
else:
    id = get_pid('nox_adb.exe')
    p = psutil.Process(id)
    path = p.exe()
    path = os.path.dirname(path)
    with open("settings.txt", "w") as myfile:
        myfile.write(path)
os.chdir(path)
device = os.popen("adb devices").read().strip()
if re.search(r'device\s.', device):
    print('Choose device:')
    i = 0
    while(i < len(device)):
        if device[i] == '\n':
            device = device[:i] + '\n[{}]'.format(getnum()) + device[i+1:]
        i = i+1
    print(device)
    method = input()
    num = device.find('[{}]'.format(method))
    num = num+1+len(method)+1
    device = device[num:]
    match = re.search(r'[\d\.:]+?\s', device)
    device = match[0].strip()
    print("Waiting for connection ...")
    connect = os.popen("adb connect " + device ).read()
    print(connect)
    if int(method)-1 == 0: hwnd = win32gui.FindWindow(None, 'NoxPlayer')
else:
    device = os.popen("adb devices").read().split('\n', 1)[1].split("device")[0].strip()
    print("Waiting for connection ...")
    connect = os.popen("adb connect " + device ).read()
    print(connect)
adbstr = 'adb -s {}'.format(device) + ' shell '
###########################

#variables
i = 0
error = ''
players = []
players.append(Heko)
os.system(adbstr + "ime set com.android.adbkeyboard/.AdbIME")
api = tesserocr.PyTessBaseAPI(lang='rus' ,psm=PSM.SINGLE_LINE)
##########

def devscreen():
    command = adbstr + "\"screencap -p | busybox base64\""
    pcommand = os.popen(command)
    png_screenshot_data = pcommand.read()
    png_screenshot_data = base64.b64decode(png_screenshot_data)
    pcommand.close()
    images = cv2.imdecode(np.frombuffer(png_screenshot_data, np.uint8), cv2.IMREAD_COLOR)
    return images

def click(x,y):
    os.system(adbstr + "input tap {} {}".format(x,y))
    time.sleep(0.5)

def search(screen):
    x = 0
    y = 0
    width, height = screen.shape[::-1]
    while y < height:
        x = 0
        while x < width:
            if screen[y,x] != 0:
                if y == 0: return -2, -2
                elif y >= 682: return -3, -3
                return x,y
            x += 1
        y += 1
    return -1,-1

def AddPlayer(screen, x, y):
    global players
    x = 0
    finalx,_  = screen.shape[::-1]
    finaly = y+45
    player = screen[y:finaly, x:finalx]
    roi = cv2.boundingRect(player)
    x,y,w,h = roi
    player = player[y:y+h, x:x+w]
    players.append(player)

def main(text):
    global players,error,api,i,adbstr,Heko,guild
    while True:
        try:
            screen = devscreen()
            date = screen[268:990, 1010:1150]
            screen = screen[268:990, 165:375] #90
            image = screen
            screen = cv2.inRange(screen, (41, 0, 68), (100,85,220))
            for player in players:
                res = cv2.matchTemplate(screen,player,cv2.TM_CCOEFF_NORMED)
                threshold = 0.7
                loc = np.where( res >= threshold)
                w,h = player.shape[::-1]
                if len(list(zip(*loc[::-1]))) > 0:
                    for pt in zip(*loc[::-1]):
                        y=pt[1]
                        while y <= pt[1]+h+10:
                            x=0
                            while x <= 209:
                                screen[y,x] = 0
                                x += 1
                            y += 1
                        break
            x,y = search(screen)
            if (x == -1) and (y == -1):
                os.system(adbstr + "input swipe 650 900 650 700")
                time.sleep(3)
                continue
            elif (x == -2) and (y == -2):
                os.system(adbstr + "input swipe 650 770 650 790")
                time.sleep(2)
                continue
            elif (x == -3) and (y == -3):
                os.system(adbstr + "input swipe 650 790 650 770")
                time.sleep(2)
                continue
            if (y <= 332) and (y >= 252):
                os.system(adbstr + "input swipe 650 790 650 740")
                time.sleep(2)
                continue
            thread = threading.Thread(target=AddPlayer(screen, x,y))
            thread.start()
            date = date[(y-20):(y+50), 0:140]
            date = cv2.inRange(date, (41, 0, 68), (100,85,220))
            date=255-date
            api.SetImage(Image.fromarray(date))
            datetext = api.GetUTF8Text()
            datetext = datetext.strip()
            i = 0
            if datetext[len(datetext)-2] == 'д':

                for char in datetext:
                    if char == 'З': datetext = datetext[:i] + '3' + datetext[i+1:]
                    elif char == 'О': datetext = datetext[:i] + '0' + datetext[i+1:]
                    elif char == 'В': datetext = datetext[:i] + '8' + datetext[i+1:]
                    i += 1
                offline = datetext[:len(datetext)-2]
                offline = int(offline)
                if offline >= 8:
                    thread.join()
                    break
            x = x+20+165
            y = y+10+268
            click(x,y)
            click(750,420)
            os.system(adbstr + "input tap 1100 930 && " + adbstr + "am broadcast -a ADB_INPUT_TEXT --es msg '"+text+"' && " + adbstr + "input tap 400 1900 && " + adbstr + "input tap 1530 930")
            click(1830,50)
            image = devscreen()
            image = image[900:1000, 1800:1900]
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            res = cv2.matchTemplate(image,guild,cv2.TM_CCOEFF_NORMED)
            threshold = 0.9
            loc = np.where( res >= threshold)
            if len(list(zip(*loc[::-1]))) <= 0:
                click(1860,300)
            click(1860,965)
            thread.join()
        except Exception as e:
            with open("logs.log", "a") as myfile:
                if error != repr(e):
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    myfile.write("[%s] - [line %s]: %s\n" % (str(datetime.datetime.now()), exc_tb.tb_lineno, repr(e)))
                    error = repr(e)

if __name__ == '__main__':
    text = sys.argv[1]
    text = text.strip()
    if len(text) >= 80: text = '[ ' + datetext + ' ]'
    main(text)
