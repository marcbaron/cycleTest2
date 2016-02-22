from System.IO.Ports import SerialPort
import time, sys, syringe
import driver
from gui import NanoAssemblrTesting
from System.Windows.Forms import Application, Form
import thread

form = NanoAssemblrTesting()
Application.Run(form)
