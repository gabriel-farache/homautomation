#!/usr/bin/python
# python code for interfacing to VC0706 cameras and grabbing a photo
# pretty basic stuff
# written by ladyada. MIT license
# revisions for Raspberrry Pi by Gordon Rush

from machine import SD, RTC, UART
import sendData
import time
import ubinascii
import gc

class VC0706():
    uart = None;
    sd = None;
    wlan = None;

    BAUD = 38400

    TIMEOUT = 0.5    # I needed a longer timeout than ladyada's 0.2 value
    SERIALNUM = 0    # start with 0, each camera should have a unique ID.

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

    VC0706_640x480 = 0x00
    VC0706_320x240 = 0x11
    VC0706_160x120 = 0x22

    VC0706_READ_DATA = 0x30
    VC0706_WRITE_DATA = 0x31

    getversioncommand = [COMMANDSEND, SERIALNUM, CMD_GETVERSION, COMMANDEND]
    resetcommand = [COMMANDSEND, SERIALNUM, CMD_RESET, COMMANDEND]
    takephotocommand = [COMMANDSEND, SERIALNUM,
                        CMD_TAKEPHOTO, 0x01, FBUF_STOPCURRENTFRAME]
    getbufflencommand = [COMMANDSEND, SERIALNUM,
                         CMD_GETBUFFLEN, 0x01, FBUF_CURRENTFRAME]
    readphotocommand = [COMMANDSEND, SERIALNUM,
                        CMD_READBUFF, 0x0c, FBUF_CURRENTFRAME, 0x0a]


    def checkreply(r, b):
        r = list(r)
        #print(r)
        string = ''.join(list(map(chr,r)))
        try:
            if(len(r)<100):
                print(string[3:])
        except Exception as e:
            print(e)

        if(r[0] == COMMANDREPLY and r[1] == SERIALNUM and r[2] == b and r[3] == 0x00):
            return True
        return False


    def reset():
        cmd = ''.join(map(chr, resetcommand))
        VC0706.uart.write(cmd)
        time.sleep(0.01)
        reply = VC0706.uart.read(100)
        r = list(reply)
        if checkreply(r, CMD_RESET):
            return True
        return False


    def getversion():
        cmd = ''.join(map(chr, getversioncommand))
        VC0706.uart.write(cmd)
        time.sleep(0.01)
        reply = VC0706.uart.read(16)
        r = list(reply)
        # print r
        if checkreply(r, CMD_GETVERSION):
            # print r
            return True
        return False


    def takephoto():
        #cmd = ''.join(map(chr, takephotocommand))
        cmd = ''.join( list(map( chr, takephotocommand )))
        VC0706.uart.write(cmd)
        time.sleep(0.01)
        reply = VC0706.uart.read(5)
        r = list(reply)
        if(checkreply(r, CMD_TAKEPHOTO) and r[3] == int(0x0)):
            return True
        return False


    def getbufferlength():
        cmd = ''.join(map(chr, getbufflencommand))
        VC0706.uart.write(cmd)
        time.sleep(0.01)
        reply = VC0706.uart.read(9)
        r = list(reply)
        print("bufer")
        print(r[4] == int(0x4))
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


    def readbuffer(bytes):
        addr = 0   # the initial offset into the frame buffer
        photo = []

        # bytes to read each time (must be a mutiple of 4)
        inc = 512

        while(addr < bytes):
            # on the last read, we may need to read fewer byteVC0706.uart.
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
            print ("Reading", chunk, "bytes at", addr)
            # print map(hex, command)

            # make a string out of the command byteVC0706.uart.
            cmd = ''.join(map(chr, command))
            VC0706.uart.write(cmd)
            time.sleep(0.5)
            # the reply is a 5-byte header, followed by the image data
            #   followed by the 5-byte header again.
            reply = VC0706.uart.read(5 + chunk + 5)

            # convert the tuple reply into a list
            r = list(reply)
            if(len(r) != 5 + chunk + 5):
                # retry the read if we didn't get enough bytes back.
                print("Read %VC0706.uart. Retrying" % (len(r)))
                continue

            if(not checkreply(r, CMD_READBUFF)):
                print("ERROR READING PHOTO")
                return

            # append the data between the header data to photo
            f.write(bytearray(r[5:chunk + 5]))
            gc.collect()
            # advance the offset into the frame buffer
            addr += chunk

        print("%s Bytes written" % (addr))
        #return photo


    def setsize(size):
        setsizecommand = [COMMANDSEND, COMMANDEND,
                          VC0706_WRITE_DATA, 0x05, 0x04, 0x01, 0x00, 0x19, size]

        cmd = ''.join(map(chr, setsizecommand))
        print(ubinascii.hexlify(cmd))
        VC0706.uart.write(cmd)
        time.sleep(0.01)
        reply = VC0706.uart.read(17)
        print(reply)
        return True

    def mountSDCard():
        #MOSI G11 P4 CMD
        #MISO G15 P8 DATA
        #SCK G10 P23 CLOCK
        try:
            oVC0706.uart.stat('/sd')
        except OSError:
            print('Mounting SD Card\n')
            sd = SD()
            sd.init()
            oVC0706.uart.mount(sd, '/sd')
            VC0706.sd = sd
            print('SD Card mounted')
            print('%s\n' % oVC0706.uart.listdir('/sd'))

        print('SD Card mounted')
        print('%s\n' % oVC0706.uart.listdir('/sd'))

    def takePhotoAndSaveToFile():
        try:
            if(not VC0706.getversion()):
                print("Camera not found")
                exit(0)

            print("VC0706 Camera found")

            if takephoto():
                print("Snap!")

            filename = ''.join(map(str,rtc.now()))+'.jpg';
            f = open('/sd/'+filename, 'wb');
            try:
                bytes = getbufferlength()
                print("%s bytes to read" % (bytes))
                readbuffer(bytes)
                f.close()
            except Exception as e:
                f.close()
                print(e)
            #sendData.send(host='http://192.168.1.15', port=1337, data=photo)
        except Exception as e:
            print(e)

    def __init__():
        if(VC0706.wlan == None):
            VC0706.wlan = sendData.connectLocalBox()
            rtc = RTC()
            rtc.ntp_sync('fr.pool.ntp.org')

        if(VC0706.sd == None):
            mountSDCard()


        if(VC0706.uart == None):
            VC0706.uart = UART(2, baudrate=38400, pins=('G8','G7'), timeout_chars=5, bits=8, parity=None, stop=1)
            VC0706.uart.readall()
            setsize(VC0706_160x120)
            reset()
        gc.enable()
