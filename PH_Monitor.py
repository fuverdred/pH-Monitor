########(3)###
#(1)##(2)#(5)#
########(4)###

#1. 1480
#2. 700
#3. 370
#4. 140
#5. 0

import time

class PH_Monitor:
    DRIP_TIME = 150 # (ms), time it takes to deliver one drip
    READ_INTERVAL = 60 * 60 * 12 # (s)

    BUTTON_THRESHOLD = 2000
    
    def __init__(self,
                 ph_pin, # ADC pin
                 button_pin, # ADC pin
                 pump_1, # GPIO
                 pump_2, # GPIO
                 dht, # DHT11 class
                 lcd): # I2cLcd class

        self.ph_pin = ph_pin
        self.button_pin = button_pin
        self.pump_1 = pump_1
        self.pump_2 = pump_2
        self.dht = dht # digital humidity and temperature
        self.lcd = lcd

    def drip(self, pump):
        '''Turn a pump on for a specific amount of time'''
        pump.high()
        time.sleep_ms(self.DRIP_TIME)
        pump.low()

    def read_dht(self):
        '''Return (temperature, humidity) tuple'''
        self.dht.measure()
        return dht.temperature(), dht.humidity()

    def loop(self):
        '''Where everything happens'''
        time = 0
        while 1:
            button = self.button_pin.read()
            if button > self.BUTTON_THRESHOLD:
                pass
            else:
                print('BUTTON PRESS')
            time.sleep_ms(100)
            
        
