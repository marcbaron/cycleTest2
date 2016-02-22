#Look up the syringe diameter
diams = {1: 4.78, 3: 8.66, 5: 12.06, 10: 14.5, 20: 19.13, 30: 21.70}

def syringe_to_dia(sy):
    return float(diams [sy])

def volume_to_step(vol, sy):
    #Calculate the number of steps to dispense a volume
    #Assume step resolution of 256 microsteps
    sy_dia = syringe_to_dia(sy)
    
    step_size = 0.00003086 # in mm
    sy_area = 0.25*3.14*sy_dia*sy_dia # mm^2
    step_length = 1000*vol / sy_area #1000 mm^3/ml * ml / mm^2 = mm
    steps = step_length / step_size # mm/mm
    
    steps = int(steps) #convert the steps to an integer to remove any decimal places
    return steps

def flow_to_step(flow, sy):
    #Converts the desired ml/min flow to steps/sec
    sy_dia = syringe_to_dia(sy)
    
    steps = volume_to_step(1, sy) #number of steps in 1 ml, steps/ml
    
    step_sec = int(flow*steps/60.0) #ml/min * steps/ml * 1 min/60 sec = steps/sec, convert to an integer to remove decimal places
    
    return step_sec