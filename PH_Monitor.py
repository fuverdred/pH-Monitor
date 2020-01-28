'''
====================================
pH Monitor
====================================
This device reads the pH of a water bath at a given frequency, and uses two
peristaltic pumps to supply an acid/base mixture to maintain the pH of the bath

The button pin out is:
########(3)###
#(1)##(2)#(5)#
########(4)###
where:
1. START:   Begin monitoring the process. The first adjustment won't be made until
            frequency has elapsed.
2. STOP:    Stop monitoring and adjusting the pH.
3. PRIME 1: Run pump 1 to allow it to be primed with fluid.
4. PRIME 2: Run pump 2 to allow it to be primed with fluid.
5. undefined

Note that pressing multiple buttons at the same time is not supported and will
default to the higher button number.
'''

import time
from collections import namedtuple

limits = namedtuple('limit', 'lower upper')

class PH_Monitor:
    DRIP_TIME = 150 # (ms), time it takes to deliver one drip
    READ_INTERVAL = 60 * 60 * 12 # (s) time between pH measurements
    DEBOUNCE = 2 # (ms) button debounce time

    # These values are the analogue reads of the button pin
    BUTTON_THRESHOLD = 2000
    BUTTON_1 = limits(1000, BUTTON_THRESHOLD)   # Button 1 ~ 1480
    BUTTON_2 = limits(500, 1000)                # Button 2 ~ 700
    BUTTON_3 = limits(250, 500)                 # Button 3 ~ 370
    BUTTON_4 = limits(80, 250)                  # Button 4 ~ 140
    BUTTON_5 = limits(0, 80)                    # Button 5 ~ 0
    
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
        t = 0
        while 1:
            button = self.button_pin.read()
            time.sleep_ms(self.DEBOUNCE)
            if button > self.BUTTON_THRESHOLD:
                pass # nothing pressed, crack on
                self.lcd.clear()
            else:
                button = self.button_pin.read() # update val after debounce time
                if self.BUTTON_1.lower < button <= self.BUTTON_THRESHOLD:
                    while self.BUTTON_1.lower < button <= self.BUTTON_THRESHOLD:
                        button = self.button_pin.read()
                    else:
                        print('finished button 1')
                        self.lcd.clear()
                        self.lcd.move_to(0,0)
                        self.lcd.putstr('{:^16}'.format('started'))
                elif self.BUTTON_2.lower < button <= self.BUTTON_2.upper:
                    while self.BUTTON_2.lower < button <= self.BUTTON_2.upper:
                        button = self.button_pin.read()
                    else:
                        print('finished button 2')
                        self.lcd.clear()
                        self.lcd.move_to(0,0)
                        self.lcd.putstr('{:^16}'.format('stopped'))
                elif self.BUTTON_3.lower < button <= self.BUTTON_3.upper:
                    while self.BUTTON_3.lower < button <= self.BUTTON_3.upper:
                        button = self.button_pin.read()
                        self.lcd.move_to(0,0)
                        self.lcd.putstr('{:^16}'.format('PUMPING 1'))
                    else:
                        print('finished button 3')
                        self.lcd.clear()
                elif self.BUTTON_4.lower < button <= self.BUTTON_4.upper:
                    while self.BUTTON_4.lower < button <= self.BUTTON_4.upper:
                        button = self.button_pin.read()
                        self.lcd.move_to(0,0)
                        self.lcd.putstr('{:^16}'.format('PUMPING 2'))
                    else:
                        print('finished button 4')
                        self.lcd.clear()
                elif button < self.BUTTON_5.upper:
                    while button <= self.BUTTON_5.upper:
                        button = self.button_pin.read()
                    else:
                        print('finished button 5')
                        self.lcd.clear()
                        self.lcd.move_to(0,0)
                        self.lcd.putstr('{:^16}'.format('UNASSIGNED'))            
        

