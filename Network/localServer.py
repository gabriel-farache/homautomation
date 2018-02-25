import socket
import sendData
import VC0706
import SDCard
import gc
from machine import SD

addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]

SDCard.mountSDCard()

s = socket.socket()
s.bind(addr)
s.listen(1)

while True:
    cl, addr = s.accept()
    try:
        f = open('/sd/' + VC0706.takePhotoAndSaveToFile(), 'r')
        response = f.readall()
        f.close()
        cl.send(response)
        cl.close()
        gc.collect()
    except Exception as e:
        print(e)
        gc.collect()
