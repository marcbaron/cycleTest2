import clr
clr.AddReference("System.Drawing")
clr.AddReference("System.Windows.Forms")
from System.Windows.Forms import Application, Form

from System.Drawing import *
from System.Windows.Forms import *
from System.IO.Ports import SerialPort
from System import Threading

from arduino import Arduino
from driver import EZStepper
from System import Array

import time

class NanoAssemblrTesting(Form):

    def __init__(self):
        self.Text = 'NanoAssmblr Testing'
        self.FormBorderStyle = FormBorderStyle.FixedDialog

        screenSize = Screen.GetWorkingArea(self)
        self.Height = 700
        self.Width = 400
        self.panelHeight = self.ClientRectangle.Height / 2

        self.setupPanel1()
        self.setupPanel2()

        self.Controls.Add(self.panel1)
        self.Controls.Add(self.panel2)

        self.cmbArd.Items.AddRange(SerialPort.GetPortNames()) 
        self.cmbEz.Items.AddRange(SerialPort.GetPortNames()) 

        self.drivingThread = Threading.Thread(Threading.ThreadStart(self.driving))

    def setupPanel1(self):
        self.panel1 = Panel()
        image = Image.FromFile("precision.png")
        self.panel1.BackgroundImage = image
        self.panel1.ForeColor = Color.Blue
        self.panel1.Width = self.Width
        self.panel1.Height = 250
        self.panel1.Location = Point(0, 0)
        self.panel1.BorderStyle = BorderStyle.None

    def setupPanel2(self):
        #set up panel 2
        self.panel2 = Panel()
        self.panel2.Width = self.Width
        self.panel2.Height = self.Height - 250
        self.panel2.Location = Point(0, self.Height/2)
        self.panel2.BorderStyle = BorderStyle.None


        # Labels
        self.lbl2 = Label()
        self.lbl2.Text = "Volume:"
        self.lbl2.Location = Point(162, 304)
        self.lbl2.Height = 17
        self.lbl2.Width = 59

        self.lbl1 = Label()
        self.lbl1.Text = "Syringe Size:"
        self.lbl1.Location = Point(20, 304)
        self.lbl1.Height = 17
        self.lbl1.Width = 91

        self.lbl3 = Label()
        self.lbl3.Text = "Flow Rate:"
        self.lbl3.Location = Point(274, 304)
        self.lbl3.Height = 17
        self.lbl3.Width = 74

        self.lbl4 = Label()
        self.lbl4.Text = "Cycles:"
        self.lbl4.Location = Point(20, 344)
        self.lbl4.Height = 17
        self.lbl4.Width = 74

        self.Controls.Add(self.lbl1)
        self.Controls.Add(self.lbl2)
        self.Controls.Add(self.lbl3)
        self.Controls.Add(self.lbl4)

        # textboxes
        self.txtSy = ComboBox();
        self.txtSy.Location = Point(14, 323);
        self.txtSy.Size = Size(100, 20);
        self.txtSy.Items.AddRange(Array[object]((1, 3, 5, 10, 20, 30)))
        self.txtSy.SelectedIndex = 3 #initial values

        self.txtVol = TextBox();
        self.txtVol.Location = Point(143, 323);
        self.txtVol.Size = Size(100, 20);
        self.txtVol.Text = '5' #initial values

        self.txtFlow = TextBox();
        self.txtFlow.Location = Point(265, 323);
        self.txtFlow.Size = Size(100, 20);
        self.txtFlow.Text = '18' #initial values

        self.txtCycles = TextBox();
        self.txtCycles.Location = Point(14, 364);
        self.txtCycles.Size = Size(100, 20);
        self.txtCycles.Text = '20' #initial values

        self.Controls.Add(self.txtSy)
        self.Controls.Add(self.txtVol)
        self.Controls.Add(self.txtFlow)  
        self.Controls.Add(self.txtCycles)  

        # combobox
        self.cmbArd = ComboBox()
        self.cmbArd.Location = Point(12, 263)
        self.cmbArd.Size = Size(121, 21)
        self.cmbArd.Click += self.updateArd

        self.cmbEz = ComboBox()
        self.cmbEz.Location = Point(244, 263)
        self.cmbEz.Size = Size(121, 21)
        self.cmbEz.Click += self.updateEz

        self.lblArd = Label()
        self.lblArd.Text = "Arduino:"
        self.lblArd.Location = Point(53, 238);
        self.lblArd.Size = Size(50, 13);

        self.lblEz = Label()
        self.lblEz.Text = "NanoAssemblr:"
        self.lblEz.Location = Point(250, 238);
        self.lblEz.Size = Size(150, 13);

        self.Controls.Add(self.cmbArd)
        self.Controls.Add(self.cmbEz)
        self.Controls.Add(self.lblArd)
        self.Controls.Add(self.lblEz)

        # buttons
        self.btnStart = Button()
        self.btnStart.Location = Point(50, 400);
        self.btnStart.Size = Size(50, 23);
        self.btnStart.Text = "Start";
        self.btnStart.Click += self.btnStart_Click;
        
        self.btnStop = Button()
        self.btnStop.Location = Point(280, 400);
        self.btnStop.Size = Size(50, 23);
        self.btnStop.Text = "Stop";
        self.btnStop.Click += self.btnStop_Click;

        self.btnHome = Button()
        self.btnHome.Location = Point(160, 400);
        self.btnHome.Size = Size(50, 23);
        self.btnHome.Text = "Home";
        self.btnHome.Click += self.btnHome_Click;

        self.Controls.Add(self.btnStart)
        self.Controls.Add(self.btnStop)
        self.Controls.Add(self.btnHome)


        # list box
        self.lst = ListBox()
        self.lst.Location = Point(10, 430);
        self.lst.Size = Size(self.Width-20,self.Height-420-40)

        self.Controls.Add(self.lst)

        # timer
        self.timer = Timer()
        self.timer.Interval = 50
        self.timer.Enabled = True
        self.timer.Tick += self.timer_tick;

        #check box
        self.chq = CheckBox();
        self.chq.Text = "Enable Variable Speed"
        self.chq.Location = Point(143,364)
        self.chq.Size = Size(150,20)

        self.Controls.Add(self.chq)
         
    def btnStart_Click(self, sender, event):
        self.flag = True     # if anything is wrong, program wont run and flag = flase   

        self.input() #convert input
                
        if self.flag:
            # set com port
            self.ardport = self.cmbArd.SelectedItem
            self.ezport = self.cmbEz.SelectedItem
            # set up serial
            self.setupSerial();
     
        if self.flag:
            self.btnStart.Enabled = False
            self.btnHome.Enabled = False
            self.chq.Enabled = False
            self.ez.stage(7)
            self.lst.Items.Add("Program Starts.")
            if self.chq.Checked:
                self.lst.Items.Add("Varibale speed enabled")
            #self.lst.Items.Add("Home Motor, wait for 5s")
            if not self.drivingThread.IsAlive:
                self.drivingThread = Threading.Thread(Threading.ThreadStart(self.driving))
                self.drivingThread.Start()

    def updateArd(self, sender, event):
        self.cmbArd.Items.Clear();
        self.cmbArd.Items.AddRange(SerialPort.GetPortNames()) 

    def updateEz(self, sender, event):
        self.cmbEz.Items.Clear();
        self.cmbEz.Items.AddRange(SerialPort.GetPortNames()) 

    def timer_tick(self, sender, event):
        self.lst.SelectedIndex = self.lst.Items.Count - 1;

    def input(self):
        # convert str to numbers
        try:
            self.sy = int(self.txtSy.Text)
        except:
            self.flag = False
            self.lst.Items.Add("Please enter syringe size")
        # check if there is input and if vol < sy
        try:
            self.vol = float(self.txtVol.Text)
            if self.vol > self.sy or self.vol<0:
                self.lst.Items.Add("Invalid volume, please check if volume to dispense is smaller than syringe size")
                self.flag = False
        except:
            self.flag = False
            self.lst.Items.Add("Please enter volume")
        # check if there is input
        try:
            self.flow = float(self.txtFlow.Text)
        except:
            self.flag = False
            self.lst.Items.Add("Please enter flow rate")
        
        # check if there is input
        try:
            self.cycle = int(self.txtCycles.Text)
        except:
            self.flag = False
            self.lst.Items.Add("Please enter cycle")

    def setupSerial(self):
        try: # check if port can be connected
            self.ardser = SerialPort(self.ardport)
            self.ardser.Open()
            self.ard = Arduino(self.ardser)
        except:
            self.lst.Items.Add("Please select COM Port for Arduino")
            self.flag = False
        try:
            self.ezser = SerialPort(self.ezport)
            self.ezser.Open()
            self.ez = EZStepper(self.ezser,self.sy,self.vol,self.flow, self.chq.Checked)
        except: 
            self.lst.Items.Add("Please select COM Port for NanoAssemblr")
            self.flag = False

    def driving(self):
        #time.sleep(5)
        time.sleep(1)
        for cycle in range (1,self.cycle+1):
            self.lst.Items.Add("This is cycle %d" %cycle)
            #print '\n' + "This is cycle %d" %cycle + '\n'

            # stage zero: move syringe up
            self.lst.Items.Add("Stage 1: High Pressure, Moving Up")
            self.ard.stage(1) # tell arduino this is stage 1
            time.sleep(1)
            #self.ez.stage(cycle,1) # tell driver this is stage 1
            self.ez.stage(1) # tell driver this is stage 1

            # stage one: vent air
            self.lst.Items.Add("Stage 2: Vent Air")
            self.ard.stage(2) # tell arduino this is stage 2
            time.sleep(3) # temprorary wait until operation is done

            # stage two: move syringe down
            self.lst.Items.Add("Stage 3: Low Pressure, Moving Down")
            self.ard.stage(3) # tell arduino this is stage 3
            time.sleep(1)
            #self.ez.stage(cycle,3)    # tell driver this is stage 3
            self.ez.stage(3) # tell driver this is stage 1

            # stage three: ready for next loop
            self.lst.Items.Add("Stage 4: Vent Air")
            self.ard.stage(4) # tell arduino this is stage 4
            time.sleep(5) # temprorary wait until operation is done

        # finish up, turn off two valves, close serial so that can restart
        self.ard.stage(5)
        #self.ez.stage(cycle,5)
        self.ez.stage(5)
        self.ardser.Close()
        self.ezser.Close()
        self.lst.Items.Add("Cycles finished")
        self.btnStart.Enabled = True

    def btnStop_Click(self, sender, event):
        self.drivingThread.Abort()
        try:
            #self.ez.stage(1,6)
            self.ez.stage(6)
            self.ard.stage(5)
        except:
            trashvalue = 0
        try:
            if self.ardser.IsOpen:
                self.ardser.Close()
            if self.ezser.IsOpen:
                self.ezser.Close()
        except:
            trashvalue = 0

        self.lst.Items.Add("Program Stopped")
        self.btnStart.Enabled = True
        self.btnHome.Enabled = True
        self.chq.Enabled = True

    def btnHome_Click(self, sender, event):
        try:
            self.ezport = self.cmbEz.SelectedItem
            self.ezser = SerialPort(self.ezport)
            if self.ezser.IsOpen:
                self.ez.stage(7)
                self.lst.Items.Add("Home Motor")
                self.ezser.Close()
            else:
                self.ezser.Open()
                self.ez = self.ez = EZStepper(self.ezser,1,1,1,1)
                self.ez.stage(7)
                time.sleep(0.5) #for some reason the ez stepper needs time to process stage 7
                self.lst.Items.Add("Home Motor")
                self.ezser.Close()
        except:
            self.lst.Items.Add("NanoAssemblr cannot be found")
            


if __name__ == "__main__" :
    form = NanoAssemblrTesting()
    Application.Run(form) 