# written by ladyada. MIT license
# revisions for Raspberrry Pi by Gordon Rush
from machine import SD, RTC, UART
import sendData
import time
import gc
import SDCard

TX='G8'
RX='G7'

BAUD = 38400

COMMANDSEND = 0x56
COMMANDREPLY = 0x76
COMMANDEND = 0x00

CMD_GETVERSION = 0x11
CMD_RESET = 0x26
CMD_TAKEPHOTO = 0x36
CMD_READBUFF = 0x32
CMD_GETBUFFLEN = 0x34

FBUF_CURRENTFRAME = 0x00
FBUF_NEXTFRAME = 0x01

FBUF_STOPCURRENTFRAME = 0x00

VC0706_160x120 = 0x22

getversioncommand = [COMMANDSEND, 0x00, CMD_GETVERSION, COMMANDEND]
resetcommand = [COMMANDSEND, 0x00, CMD_RESET, COMMANDEND]
takephotocommand = [COMMANDSEND, 0x00,
                    CMD_TAKEPHOTO, 0x01, FBUF_STOPCURRENTFRAME]
getbufflencommand = [COMMANDSEND, 0x00,
                     CMD_GETBUFFLEN, 0x01, FBUF_CURRENTFRAME]
readphotocommand = [COMMANDSEND, 0x00,
                    CMD_READBUFF, 0x0c, FBUF_CURRENTFRAME, 0x0a]


def checkreply(r, b):
    r = list(r)

    if(r[0] == COMMANDREPLY and r[1] == 0x00 and r[2] == b and r[3] == 0x00):
        return True
    return False


def reset():
    uart.readall()
    cmd = ''.join(map(chr, resetcommand))
    uart.write(cmd)
    time.sleep(1)
    reply = uart.read(100)
    r = list(reply)

    if checkreply(r, CMD_RESET):
        return True
    else:
        reset()

def getversion():
    uart.readall()
    cmd = ''.join(map(chr, getversioncommand))
    uart.write(cmd)
    time.sleep(0.01)
    reply = uart.read(16)
    r = list(reply)
    if checkreply(r, CMD_GETVERSION):
        return True
    return False


def takephoto():
    uart.readall()
    cmd = ''.join(list(map( chr, takephotocommand )))
    uart.write(cmd)
    time.sleep(0.01)
    reply = uart.read(5)
    r = list(reply)
    if(checkreply(r, CMD_TAKEPHOTO) and r[3] == int(0x0)):
        return True
    return False

def getbufferlength():
    uart.readall()
    cmd = ''.join(map(chr, getbufflencommand))
    uart.write(cmd)
    time.sleep(1)
    reply = uart.read(9)
    r = list(reply)

    if(checkreply(r, CMD_GETBUFFLEN) and r[4] == int(0x4)):
        l = (r[5])
        l <<= 8
        l += (r[6])
        l <<= 8
        l += (r[7])
        l <<= 8
        l += (r[8])
        return l
    return 0

def readbuffer(bytes, f):
    addr = 0

    # must be a mutiple of 4
    inc = 512
    uart.readall()
    retry = 0
    while(addr < bytes):
        gc.collect()
        time.sleep(0.1)
        # on the last read, we may need to read fewer byteuart.
        chunk = min(bytes - addr, inc)

        # append 4 bytes that specify the offset into the frame buffer
        command = readphotocommand + [(addr >> 24) & 0xff, (addr >> 16) & 0xff, (addr >> 8) & 0xff,
                                      addr & 0xff]

        # append 4 bytes that specify the data length to read
        command += [(chunk >> 24) & 0xff,
                    (chunk >> 16) & 0xff,
                    (chunk >> 8) & 0xff,
                    chunk & 0xff]

        # append the delay
        command += [1, 0]

        uart.write(''.join(map(chr, command)))
        time.sleep(1)
        # the reply is a 5-byte header, followed by the image data
        #   followed by the 5-byte header again.
        r = list(uart.read(5 + chunk + 5))
        if(len(r) != 5 + chunk + 5):
            print("Read %s. Retrying" % (len(r)))
            if(retry <= 5):
                retry+=1
                continue

        if(not checkreply(r, CMD_READBUFF)):
            print("ERROR READING PHOTO")
            return(0)

        f.write(bytearray(r[5:chunk + 5]))
        gc.collect()
        time.sleep(0.1)

        addr += chunk
        retry = 0

def setsize(size):
    uart.readall()

    cmd = ''.join(map(chr, [COMMANDSEND, COMMANDEND,
                      0x31, 0x05, 0x04, 0x01, 0x00, 0x19, size]))
    uart.write(cmd)
    time.sleep(0.01)
    uart.readall()

def takePhotoAndSaveToFile(filename=None, retry=True):
    global uart

    SDCard.mountSDCard()
    uart = UART(2, baudrate=BAUD, pins=(TX,RX), timeout_chars=5)
    uart.readall()
    setsize(VC0706_160x120)
    reset()
    uart.readall()
    if(not getversion()):
        print("Camera not found")
        return(0)

    if takephoto():
        if(filename == None):
            filename = ''.join(map(str,RTC().now()))+'.jpg';

        f = open('/sd/'+filename, 'wb');

        try:
            gc.collect()
            readbuffer(getbufferlength(), f)
            return filename
        except Exception as e:
            print(e)
            if(retry):
                try:
                    time.sleep(2)
                    f.close()
                    gc.collect()
                    return takePhotoAndSaveToFile(filename, False)
                except Exception as ee:
                    print(ee)
        finally:
            f.close()
            uart.deinit()
            gc.collect()
