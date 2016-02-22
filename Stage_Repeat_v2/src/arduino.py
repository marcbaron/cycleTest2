from System.IO.Ports import SerialPort
import time

class Arduino:
    # define constants
    valve1 = 12
    valve2 = 13
    en = "HIGH" # energize
    de = "LOW" # denergize
    
    def __init__(self, ser):
        "setup serial communication with arduino"
        ser.BaudRate = 9600
        self.ser = ser

    def stage(self, stage):
        self.valveOperation(stage)
    
    def valveOperation (self,stage):
        if stage == 1: # Energize valve1, valve2	
            #print ("Stage1: ")
            tx = str(self.valve1) + self.en + '\n' # transmit message
            self.ser.Write(tx) # send message to arduino
            tx = str(self.valve2) + self.en + '\n' # transmit message
            self.ser.Write(tx) # send message to arduino
            time.sleep(0.1) #give arduino time to write
            rx = self.ser.ReadExisting()#read from Arduino
          

        elif stage == 2: # Denergize valve1, valve2	
            #print ("Stage2: ")
            tx = str(self.valve1) + self.de + '\n' # transmit message
            self.ser.Write(tx) # send message to arduino
            tx = str(self.valve2) + self.de + '\n' # transmit message
            self.ser.Write(tx) # send message to arduino
            time.sleep(0.1) #give arduino time to write
            rx = self.ser.ReadExisting()#read from Arduino
            

        elif stage == 3: # Energize valve1, valve2
            #print ("Stage3: ")
            tx = str(self.valve1) + self.en + '\n' # transmit message
            self.ser.Write(tx) # send message to arduino
            tx = str(self.valve2) + self.de + '\n' # transmit message
            self.ser.Write(tx) # send message to arduino
            time.sleep(0.1) #give arduino time to write
            rx = self.ser.ReadExisting()#read from Arduino
            #print rx
            

        elif stage == 4: # Energize valve1, valve2
            #print ("Stage4: ")
            tx = str(self.valve1) + self.de + '\n' # transmit message
            self.ser.Write(tx) # send message to arduino
            tx = str(self.valve2) + self.en + '\n' # transmit message
            self.ser.Write(tx) # send message to arduino
            time.sleep(0.1) #give arduino time to write
            rx = self.ser.ReadExisting()#read from Arduino

        elif stage == 5:
            tx = str(self.valve1) + self.de + '\n' # transmit message
            self.ser.Write(tx) # send message to arduino
            tx = str(self.valve2) + self.de + '\n' # transmit message
            self.ser.Write(tx) # send message to arduino            