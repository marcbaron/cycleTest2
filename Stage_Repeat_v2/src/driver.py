from System.IO.Ports import SerialPort
from System import Console
from System import TimeoutException
from System.Threading import AutoResetEvent 
import time
import pyevent
import syringe

# driver code to send and recieve things through the serial port.
# uses System.IO.Ports.SerialPort to communicate with the serial
# port. see
#
# http://msdn.microsoft.com/en-us/library/system.io.ports.serialport.aspx
#
# Compared with pyserial, it has nice a nice function for finding 
# the available serial ports (SerialPort.GetPortNames) which uses
# the familiar COM# labeling scheme, and is included with windows
# so less extra files need to be distributed.

ERROR_CODES = {
    0: "No Error",
    1: "Init Error",
    2: "Bad Command",
    3: "Bad Operand",
    9: "Overload Error",
}

def get_checksum(message):
    return reduce( lambda a,b: a ^ b, [ord(i) for i in message])

STX = chr(2)
ETX = chr(3)
all = 'A'

# Parses a response string and gives it a nice data structure
class Response:
    def __init__(self, response):
        #print "r: " + response
        status = ord(response[0])

        self.ok = status & 0x60 > 0
        self.ready = status & 0x40 > 0

        self.error_code = status & 0xf
        
        self.data = response[1:]

        if not(hasattr(self, 'data')):
            self.data = 0

    def __repr__(self):
        if not self.ok:
            return "bad response."

        r = "response found. "

        if self.error_code != 0:
            if self.error_code in ERROR_CODES:
                r += ERROR_CODES[self.error_code]+". "
            else:
                r += "unknown error (%d). " % self.error_code

        if len(self.data) > 0:
            r += "data is %s. " % self.data

        if self.ready:
            r += "stepper is ready."

        return r
        
# uses pyevent.py to implement a nice callback mechanism.
# It waits for incoming data on the serial port on a seperate
# thread and calls any functions attached to on_response
# with with the response object.

# eg.
#
# def my_callback(response):
#     print response.status
#
# d = EZStepper( <serial port> )
# d.on_response += my_callback
#  -> now will print the status code of any response recieved.
# 
# d.on_response -= my_callback
#  -> disable the callback

class EZStepper:
    def __init__(self, ser,sy,vol,flow,chq):
        """ser should be an open SerialPort"""
        ser.ReadTimeout = 100
        self.ser = ser

        self.ser.DataReceived += self.got_data_oem

        self.on_response, self._response_caller = pyevent.make_event()
        #self.on_response += self.print_response

        #for send_safe
        self.retries = 5

        #queue to store incoming data
        self.incoming = ""

        #motors specs
        self.homeSpeed = 200000
        self.homeStep = 3000000
        self.step_tot = 2400000

        #set checkbox status
        self.chq = chq
        self.factor = 1.2 #speed increase factor

        #convert input
        self.step_vol = syringe.volume_to_step(vol,sy) # steps to dispense volume
        self.step_sec = syringe.flow_to_step(flow,sy) # flow rate to dispense volume
        self.step_offset = self.step_tot - self.step_vol


    def print_response(self, resp):
        print("recv: %s" % resp)
        
    # s is a System.IO.Ports.SerialPort object
    # for OEM protocol.. 
    #
    # **************************************************************
    # NOTE: SerialPort.ReadTo crashes here when compiled with pyc.py
    # **************************************************************
    def got_data_oem(self, s, args):
        while s.BytesToRead > 0:
            self.incoming = self.incoming + s.ReadExisting()

        self.read_incoming()

    # parse the incoming  queue for response messages from device
    def read_incoming(self):
        #find start of message in queue and discard any junk data before that
        start = self.incoming.find(STX+"0")
        if start > -1:
            self.incoming = self.incoming[start:]
        else:
            return False #no message

        #find end of message
        end = self.incoming.find(ETX)+1
        if end < 1 or end >= len(self.incoming):
            return False #haven't received end of message yet

        #otherwise we have a message
        message = self.incoming[:end]
        if get_checksum(message) == ord(self.incoming[end]):
            self._response_caller( Response(message[2:-1]) )

        self.incoming = self.incoming[end+1:]
        self.read_incoming()

    # DT protocol. like
    # /<address><data.... ><carriage return>
    def send_dt(self, address, data): 
        message = "/" + str(address) + data + "\r"
        self.ser.Write( message )

    #OEM protocol. like
    # <STX><address><sequence><data.... ><ETX><checksum>
    def send_oem(self, address, data, tries=1):
        #sequence always has 0x30 set. makes it into a readable char.
        sequence = 0x30 | tries
        if tries > 1: #set repeat bit..
            sequence = sequence | 8

        message = STX + str(address) + chr(sequence) + str(data) + ETX
        checksum = get_checksum(message)
        self.ser.Write(message + chr(checksum))

    def send(self, addr, data):
        self.send_oem(addr, data)
        #print("sent " + str(addr) + data)

    def sendrecv(self, addr, data):
        receiver = AutoResetEvent(False)

        self.r = None

        def on_response(resp):
            self.r = resp
            if resp.ok and resp.error_code == 0:
                receiver.Set()

        self.on_response += on_response

        #print data
        self.send(addr, data)

        receiver.WaitOne(100)

        #Version 1 had the following line commented out
        self.on_response -= on_response
        
        #print self.r.data
        return self.r
            

    def send_safe(self, addr, data):
        for i in range(self.retries):
            r = self.sendrecv(addr, data)
            if r != None and r.ok:
                return r

    def disconnect(self):
        self.ser.DataReceived -= self.got_data_oem

    def operation (self,stage):
        if stage == 1:
            self.send_safe(all,"V%dP%dR" % (self.step_sec, self.step_vol)) # dispens volume
            self.secUp_vol = self.step_vol/self.step_sec + 2 # calculate time in secs for motors to move up
            time.sleep(self.secUp_vol)
        elif stage == 3:
            self.send_safe(all,"V%dZ%dR" % (self.homeSpeed, self.step_vol))
            self.secDown = self.step_vol/self.homeSpeed + 2 # calculate time in secs for motors to home
            time.sleep(self.secDown)
        elif stage == 5:
            self.send_safe(all,"V%dZ%dR" % (self.homeSpeed, self.homeStep))
        elif stage == 6: #for stop 
            self.send_safe("Q", "T")
        elif stage == 7: #for home
            #turn on sensors
            self.send_safe(1,"n2R")
            self.send(all,"V%dZ%dR" % (self.homeSpeed, self.homeStep))
        
    #def stage (self, cycle, stage):
    def stage (self,stage):
        #self.operation(cycle,stage)
        self.operation(stage)
        if self.chq and stage == 3:    #only change speed when its checked and the end of the cycle
            self.step_sec = int(self.step_sec * self.factor)
            #print(self.step_sec)
            if self.step_sec > 300000:
                self.step_sec = 100000
        
if __name__ == "__main__":
    import sys

    ser = SerialPort("COM9")
    ser.Open()

    d = EZStepper(ser,1,1,1,1)
    print ("Initiated")  
    d.stage(7)
    print "Home"
    
#import code
#code.interact(local=locals())