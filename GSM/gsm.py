from machine import UART, Pin, Time
class SIM800L:
    TERMINATION_CHAR = '\x1a'

    TXD_PIN = 'GP16'
    RXD_PIN = 'GP17'
    RST_PIN = 'GP22'

    SMS_PDU_MODE = 0
    SMS_TEXT_MODE = 1

    smsMode = SMS_PDU_MODE #default mode

    #return a tuple (cmd, gsm version, status)
    def __init__(self, spd=115200):
        RST = Pin(RST_PIN, mode=Pin.OUT)
        RST.value(0)
        uart = UART(1, baudrate=spd, pins=(TXD_PIN, RXD_PIN))
        RST.value(1)

    def initGSM(self):
        uart.write('ATI\r\n')
        time.sleep(1)
        uart.any()
        cmd = uart.readline()
        gsm_version = uart.readline()
        if (gsm_version == b'ERROR\r\n'):
            return (cmd, None, gsm_version)
        else:
            #this should be \r\n
            uart.readline()
            status = uart.readline()
            return(cmd, gsm_version, status)

    def setSMSType(self, mode):
        self.smsMode = mode
        uart.write('AT+CMGF='+self.smsMode+'\n'+self.TERMINATION_CHAR)
        time.sleep(1)
        cmd = uart.readline()
        status = uart.readline()
        return(cmd, status)

    def sendSMS(self, phoneNumber, message):
        if(self.smsMode == self.SMS_PDU_MODE):

        elif (self.smsMode == self.SMS_TEXT_MODE):
            uart.write('AT+CMGS="'+phoneNumber+'\n'+message+self.TERMINATION_CHAR)
            time.sleep(1)
            cmd = uart.readline()
            uart.readline()
            response = uart.readline()
            uart.readline()
            status = uart.readline()
        else:
            return(None, None, None)
        return (cmd, response, status)
        
    def readUnreadSMS(self):

