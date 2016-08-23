from machine import Pin
from machine import SPI 
class MFRC522:
  RESET = 'GP22'
  CLK = 'GP14'
  MISO = 'GP15'
  MOSI = 'GP16'
  CS = 'GP17'

  MAX_LEN = 16
  
  PCD_IDLE       = 0x00
  PCD_AUTHENT    = 0x0E
  PCD_TRANSCEIVE = 0x0C
  PCD_RESETPHASE = 0x0F
  PCD_CALCCRC    = 0x03

  PICC_REQIDL    = 0x26
  PICC_REQALL    = 0x52
  PICC_ANTICOLL  = 0x93
  PICC_SElECTTAG = 0x93
  PICC_AUTHENT1A = 0x60
  PICC_READ      = 0x30
  PICC_WRITE     = 0xA0
  
  MI_OK       = 0
  MI_NOTAGERR = 1
  MI_ERR      = 2
  MI_AUTH_ERROR_STATUS2REG = 3

  CommandReg     = 0x01
  CommIEnReg     = 0x02
  CommIrqReg     = 0x04
  DivIrqReg      = 0x05
  ErrorReg       = 0x06
  Status2Reg     = 0x08
  FIFODataReg    = 0x09
  FIFOLevelReg   = 0x0A
  WaterLevelReg  = 0x0B
  ControlReg     = 0x0C
  BitFramingReg  = 0x0D
  
  ModeReg        = 0x11
  TxControlReg   = 0x14
  TxAutoReg      = 0x15
  
  CRCResultRegM     = 0x21
  CRCResultRegL     = 0x22
  TModeReg          = 0x2A
  TPrescalerReg     = 0x2B
  TReloadRegH       = 0x2C
  TReloadRegL       = 0x2D
    
  serNum = []

  def __init__(self, spd=1000000):
    # first assign CLK, MISO, MOSI, CS to the correct pins
    self.pin_clk = Pin(self.CLK, mode=Pin.OUT)    # CLK
    self.pin_miso = Pin(self.MISO)    # MISO
    self.pin_mosi = Pin(self.MOSI, mode=Pin.OUT)    # MOSI
    self.pin_cs = Pin(self.CS, mode=Pin.OUT)    # NSS/CS
    self.pin_reset = Pin(self.RESET, mode=Pin.OUT)

    self.pin_reset.value(0)
    self.pin_cs.value(1)

    self.spi = SPI(0)
    self.spi.init(mode=SPI.MASTER, baudrate=spd, pins=(self.CLK, self.MOSI, self.MISO))
    
    self.pin_reset.value(1)

    self.MFRC522_Init()
  
  def MFRC522_Reset(self):
    self.Write_MFRC522(self.CommandReg, self.PCD_RESETPHASE)
  
  def Write_MFRC522(self, addr, val):
    self.pin_cs.value(0)
    # 0(MSB = Write) ADDR1 ADDR2 ADDR3 ADDR4 ADDR5 ADDR6 0(LSB = 0) DATA
    spiBytes = bytearray(2)
    spiBytes[0] = ((addr<<1)&0x7E) 
    spiBytes[1] = val
    self.spi.write(spiBytes)
    self.pin_cs.value(1)
  
  def Read_MFRC522(self, addr):
    self.pin_cs.value(0)
    # 1(MSB = Read) ADDR1 ADDR2 ADDR3 ADDR4 ADDR5 ADDR6 0(LSB = 0)
    self.spi.write((addr<<1)&0x7E|0x80)
    data = self.spi.read(1)
    self.pin_cs.value(1)
    return data[0]
  
  def SetBitMask(self, reg, mask):
    tmp = self.Read_MFRC522(reg)
    self.Write_MFRC522(reg, tmp | mask)
    
  def ClearBitMask(self, reg, mask):
    tmp = self.Read_MFRC522(reg);
    self.Write_MFRC522(reg, tmp & (~mask))
  
  def AntennaOn(self):
    temp = self.Read_MFRC522(self.TxControlReg)
    if(~(temp & 0x03)):
      self.SetBitMask(self.TxControlReg, 0x03)

  
  def AntennaOff(self):
    self.ClearBitMask(self.TxControlReg, 0x03)
  
  def MFRC522_ToCard(self,command,sendData):
    backData = []
    backLen = 0
    status = self.MI_ERR
    irqEn = 0x00
    waitIRq = 0x00
    lastBits = None
    n = 0
    i = 0
    
    if command == self.PCD_AUTHENT:
      irqEn = 0x12
      waitIRq = 0x10
    if command == self.PCD_TRANSCEIVE:
      irqEn = 0x77
      waitIRq = 0x30

    self.Write_MFRC522(self.CommIEnReg, irqEn|0x80)
    self.ClearBitMask(self.CommIrqReg, 0x80)
    self.SetBitMask(self.FIFOLevelReg, 0x80)
    self.Write_MFRC522(self.CommandReg, self.PCD_IDLE);  

    while(i<len(sendData)):
      self.Write_MFRC522(self.FIFODataReg, sendData[i])
      i = i+1
    self.Write_MFRC522(self.CommandReg, command)

    if command == self.PCD_TRANSCEIVE:
      self.SetBitMask(self.BitFramingReg, 0x80)
    
    i = 2000
    while True:
      n = self.Read_MFRC522(self.CommIrqReg)
      i = i - 1
      if ~((i!=0) and ~(n&0x01) and ~(n&waitIRq)):
        break
    
    self.ClearBitMask(self.BitFramingReg, 0x80)
  
    if i != 0:
      st = self.Read_MFRC522(self.ErrorReg)
      if (st & 0x1B)==0x00:
        status = self.MI_OK

        if n & irqEn & 0x01:
          status = self.MI_NOTAGERR
        elif command == self.PCD_TRANSCEIVE:
          n = self.Read_MFRC522(self.FIFOLevelReg)
          lastBits = self.Read_MFRC522(self.ControlReg) & 0x07
          if lastBits != 0:
            backLen = (n-1)*8 + lastBits
          else:
            backLen = n*8
          
          if n == 0:
            n = 1
          if n > self.MAX_LEN:
            n = self.MAX_LEN
    
          i = 0
          while i<n:
            backData.append(self.Read_MFRC522(self.FIFODataReg))
            i = i + 1;
      else:
        status = self.MI_ERR
    return (status,backData,backLen)
  
  
  def MFRC522_Request(self, reqMode):
    status = None
    backBits = None
    TagType = [reqMode]

    self.Write_MFRC522(self.BitFramingReg, 0x07)

    (status,backData,backBits) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, TagType)
    if ((status != self.MI_OK) | (backBits != 0x10)):
      status = self.MI_ERR
      
    return (status,backBits)
  
  
  def MFRC522_Anticoll(self):
    backData = []
    serNumCheck = 0
    
    serNum = [self.PICC_ANTICOLL, 0x20]
  
    self.Write_MFRC522(self.BitFramingReg, 0x00)
    
    (status,backData,backBits) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE,serNum)
    
    if(status == self.MI_OK):
      i = 0
      if len(backData)==5:
        while i<4:
          serNumCheck = serNumCheck ^ backData[i]
          i = i + 1
        if serNumCheck != backData[i]:
          status = self.MI_ERR
      else:
        status = self.MI_ERR
  
    return (status,backData)
  
  def CalulateCRC(self, pIndata):
    self.ClearBitMask(self.DivIrqReg, 0x04)
    self.SetBitMask(self.FIFOLevelReg, 0x80);
    i = 0
    while i<len(pIndata):
      self.Write_MFRC522(self.FIFODataReg, pIndata[i])
      i = i + 1
    self.Write_MFRC522(self.CommandReg, self.PCD_CALCCRC)
    i = 0xFF
    while True:
      n = self.Read_MFRC522(self.DivIrqReg)
      i = i - 1
      if not ((i != 0) and not (n&0x04)):
        break
    pOutData = []
    pOutData.append(self.Read_MFRC522(self.CRCResultRegL))
    pOutData.append(self.Read_MFRC522(self.CRCResultRegM))
    return pOutData
  
  def MFRC522_SelectTag(self, serNum):
    backData = []
    buf = [self.PICC_SElECTTAG, 0x70] + serNum[:5]

    buf += self.CalulateCRC(buf)
    (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buf)
    
    if (status == self.MI_OK) and (backLen == 0x18):
      return self.MI_OK
    else:
      return self.MI_ERR
  
  def MFRC522_Auth(self, authMode, BlockAddr, Sectorkey, serNum):
    #First byte should be the authMode (A or B)
    #Second byte is the trailerBlock (usually 7)
    #Now we need to append the authKey which usually is 6 bytes of 0xFF
    #Next we append the first 4 bytes of the UID
    buff = [authMode, BlockAddr] + Sectorkey + serNum[:4]

    # Now we start the authentication itself
    (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_AUTHENT,buff)

    # Check if an error occurred


    # Return the status
    return status
  
  def MFRC522_StopCrypto1(self):
    self.ClearBitMask(self.Status2Reg, 0x08)

  def MFRC522_Read(self, blockAddr):
    recvData = [self.PICC_READ, blockAddr]
    recvData += self.CalulateCRC(recvData)

    (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, recvData)
    return (status, backData)
  
  def MFRC522_Write(self, blockAddr, writeData):
    buff = [self.PICC_WRITE, blockAddr]
    buff += self.CalulateCRC(buff)
    (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE, buff)
    if not(status == self.MI_OK) or not(backLen == 4) or not((backData[0] & 0x0F) == 0x0A):
        status = self.MI_ERR
    
    if status == self.MI_OK:
        i = 0
        buf = []
        while i < 16:
            buf.append(writeData[i])
            i = i + 1
        buf += self.CalulateCRC(buf)
        (status, backData, backLen) = self.MFRC522_ToCard(self.PCD_TRANSCEIVE,buf)
        if not(status == self.MI_OK) or not(backLen == 4) or not((backData[0] & 0x0F) == 0x0A):
            status = self.MI_ERR

    return status

  def MFRC522_Init(self):
    self.MFRC522_Reset();
    
    self.Write_MFRC522(self.TModeReg, 0x8D)
    print(hex(self.Read_MFRC522(self.TModeReg)))
    self.Write_MFRC522(self.TPrescalerReg, 0x3E)
    print(hex(self.Read_MFRC522(self.TPrescalerReg)))
    self.Write_MFRC522(self.TReloadRegL, 30)
    print(hex(self.Read_MFRC522(self.TReloadRegL)))
    self.Write_MFRC522(self.TReloadRegH, 0)
    print(hex(self.Read_MFRC522(self.TReloadRegH)))
    self.Write_MFRC522(self.TxAutoReg, 0x40)
    print(hex(self.Read_MFRC522(self.TxAutoReg)))
    self.Write_MFRC522(self.ModeReg, 0x3D)
    print(hex(self.Read_MFRC522(self.ModeReg)))
    self.AntennaOn()
