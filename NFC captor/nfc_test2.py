#!/usr/bin/env python
# -*- coding: utf8 -*-

import nfc2

continue_reading = True

# Capture SIGINT for cleanup when the script is aborted
def end_read():
    global continue_reading
    print("Ctrl+C captured, ending read.")
    continue_reading = False


# Create an object of the class MFRC522
MIFAREReader = nfc2.MFRC522()

# Welcome message
print("Welcome to the MFRC522 data read example")
print("Press Ctrl-C to stop.")

# This loop keeps checking for chips. If one is near it will get the UID and authenticate
while continue_reading:
    
    # Scan for cards    
    (status,TagType) = MIFAREReader.MFRC522_Request(MIFAREReader.PICC_REQIDL)
    # If a card is found
    if status == MIFAREReader.MI_OK:
        print("Card detected")
    
        # Get the UID of the card
        (status,uid) = MIFAREReader.MFRC522_Anticoll()

        # If we have the UID, continue
        if status == MIFAREReader.MI_OK:

            # Print UID
            print("Card read UID: {}, {}, {}, {}".format(uid[0],uid[1],uid[2],uid[3]))
        
            # This is the default key for authentication
            key = [0xFF,0xFF,0xFF,0xFF,0xFF,0xFF]
            
            # Select the scanned tag
            if MIFAREReader.MFRC522_SelectTag(uid) != MIFAREReader.MI_ERR:
                print("Tag selected")
                # Authenticate
                status = MIFAREReader.MFRC522_Auth(MIFAREReader.PICC_AUTHENT1A, 8, key, uid)

                # Check if authenticated
                if status == MIFAREReader.MI_OK:
                    print("Data read: {}".format(MIFAREReader.MFRC522_Read(8)))
                    status = MIFAREReader.MFRC522_Write(8, b"\x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0a\x0b\x0c\x0d\x0e\x0f")
                    MIFAREReader.MFRC522_StopCrypto1()
                    if status == MIFAREReader.MI_OK:
                        print("Data written to card")
                    else:
                        print("Failed to write data to card")
                else:
                    print ("Authentication error")