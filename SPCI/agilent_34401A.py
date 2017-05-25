from SCPI import SCPI
import time


class Agilent34410ADriver(SCPI):

    def __init__(self):
        SCPI.__init__(self,'COM1','serial')
        #self.scpi_comm("SYST:REM")

        #self.scpi_comm("*RST")
        #self.scpi_comm("CLS")
        #self.scpi_comm("IDN?")
        self.ResetDevice()
        self.DeviceClear()
        self.scpi_comm("*CLS")
        self.ReadSoftwareVersion()



    def configCurrentMeasurement(self):
        self.scpi_comm("CONFIGURE:CURRENT:DC") #Take parameter to also be able to select AC
        return(True)

    def configResistanceMeasurement(self):
        self.scpi_comm("CONFIGURE:RESISTANCE") #Take parameter to also be able to select 4W
        return(True)

    def selectMeasurementFunction(self,function):
        values = ['CAPACITANCE','CONTINUITY','CURRENT','DIODE','FREQUENCY','RESISTANCE','TEMPERATURE','VOLTAGE']
        return_value = False
        if function in values:
            return_value = True
            function_string = "FUNCTION " + "\"" + function + "\""
            self.scpi_comm(function_string)

        return(return_value)

    def readConfiguration(self):
        response = self.scpi_comm("CONFIGURE?")
        response = response.replace(' ',',')
        conf = response.split(',')
        conf_string = "Measurement type: " + conf[0] + "\nRange: " + conf[1] + "\nResolution: " + conf[2]
        return(conf_string)

    def setAutoInputZ(self, auto=False):
        if auto:
            self.scpi_comm("VOLT:IMP:AUTO ON")
        else:
            self.scpi_comm("VOLT:IMP:AUTO OFF")

    # measure 5 times per second and return each measures
    def read(self):
        time.sleep(0.2)
        self.scpi_comm("SYST:REM")
        value = float(self.scpi_comm("MEAS:VOLT:DC?"))
       # value = float(self.scpi_comm("READ?"))

        return value

#--------------------------------------------------------------------------------------------------------------------------------
#stand alone test
##if  __name__ == "__main__":
##    voltmeter=Agilent34410ADriver()
##    volt=0.123456
##    #volt=voltmeter.read()
##    with open('Read_voltage.csv','w') as f:
##        f.write("%f" %(volt))
##    #entry keyboard  to avoid  to go out of the .py
##    raw_input()
#---------------------------------------------------------------------------------------------------------------------------------
