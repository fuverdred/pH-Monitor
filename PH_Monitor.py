'''
====================================
    pH Monitor
====================================
This device reads the pH of a water bath at a given frequency, and uses two
peristaltic pumps to supply an acid/base mixture to maintain the pH of the bath.

The button arrangement is:
#########(3)####
##(1)##(2)#(5)##
#########(4)####
where:
1. START:     Begin monitoring the process. The first adjustment won't be made
              until ADJUSTMENT_INTERVAL has elapsed.
2. STOP:      Stop monitoring and adjusting the pH.
3. PRIME 1:   Run pump 1 to allow it to be primed with fluid.
4. PRIME 2:   Run pump 2 to allow it to be primed with fluid.
5. CALIBRATE: Calibrate the pH meter to a known value

Note that pressing multiple buttons at the same time is not supported and will
default to the higher button number.

-----------------------------------
    Operation
-----------------------------------
Connect pump 1 to the acidic reservoid, pump 2 to the basic reservoir.

The device will read all of the input values every 10 seconds, and display the
values on the LCD. However, changes to the pH will only be made over a longer
period of time, set by ADJUSTMENT_INTERVAL.

The pH meter itself has a tendency to drift, and will therefore need calibration
every so often. This uses a one step calibration, where the probe is placed in
a solution of known pH and the value PH_OFFSET is adjusted to that value,
assuming the gradient of the response curve does not change.

Code by Fred Cook, 2020
'''

import time
from collections import namedtuple

limits = namedtuple('limit', 'lower upper')

class PH_Monitor:
    DRIP_TIME = 150 # (ms), time it takes to deliver one drip
    ADJUSTMENT_INTERVAL = 1000 * 60 * 60 * 12# (ms) time between pH measurements
    SLEEP = 200 # ms, time between checking for button presses
    DEBOUNCE = 2 # (ms) button debounce time

    PH_GRADIENT = 1 # CHANGE THIS, NEED TO MAKE SOME MEASUREMENTS
    PH_OFFSET = 1 # CHANGE THIS TOO
    PH_TARGET = 7 # Keep things neutral
    PH_ERROR = 0.2 # allow the pH to move 0.2 around the target value

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
        self.pump_1 = pump_1 # ACIDIC
        self.pump_2 = pump_2 # BASIC
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

    def calibrate_ph_meter(self):
        '''Record the analogue read value for a known pH'''
        pH = self.read_ph_meter()
        # Use this value to adjust self.PH_OFFSET

    def analogue_to_ph(self, value):
        return (value * self.PH_GRADIENT) + self.PH_OFFSET

    def read_ph_meter(self, repeats=20):
        '''Average the analogue read value over N repeats'''
        total = 0
        for _ in range(repeats):
            total += self.ph_pin.read()
            time.sleep_ms(2)
        value = total / repeats

        return self.analogue_to_ph(value)

    def lcd_write(self, string, row=0):
        '''Print the string on the row. Everything gets centred for ease'''
        self.lcd.move_to(0, row)
        self.lcd.putstr('{:^16}'.format(string))

    def ms_to_hhmmss(self, ms):
        ms //=1000 # seconds
        hh, ms = divmod(ms, 3600)
        mm, ss = divmod(ms, 60)
        return '{:02d}:{:02d}:{:02d}'.format(hh, mm, ss)

    def loop(self):
        '''Where everything happens'''
        t = 0
        running_flag = False
        while 1:
            button = self.button_pin.read()
            time.sleep_ms(self.DEBOUNCE)
            if button > self.BUTTON_THRESHOLD:
                pass # nothing pressed, crack on
            else:
                button = self.button_pin.read() # update val after debounce time
                #START
                if self.BUTTON_1.lower < button <= self.BUTTON_THRESHOLD:
                    while self.BUTTON_1.lower < button <= self.BUTTON_THRESHOLD:
                        button = self.button_pin.read()
                    else:
                        self.lcd.clear()
                        self.lcd_write('STARTING')
                        running_flag = True # Start making adjustments
                #STOP
                elif self.BUTTON_2.lower < button <= self.BUTTON_2.upper:
                    while self.BUTTON_2.lower < button <= self.BUTTON_2.upper:
                        button = self.button_pin.read()
                    else:
                        running_flag = False # Stop making adjustments
                #PRIME PUMP 1
                elif self.BUTTON_3.lower < button <= self.BUTTON_3.upper:
                    while self.BUTTON_3.lower < button <= self.BUTTON_3.upper:
                        self.pump_1.high()
                        button = self.button_pin.read()
                    else:
                        self.pump_1.low()
                #PRIME PUMP 2
                elif self.BUTTON_4.lower < button <= self.BUTTON_4.upper:
                    while self.BUTTON_4.lower < button <= self.BUTTON_4.upper:
                        self.pump_2.high()
                        button = self.button_pin.read()
                    else:
                        self.pump_2.low()
                #CALIBRATE PH METER
                elif button < self.BUTTON_5.upper:
                    while button <= self.BUTTON_5.upper:
                        button = self.button_pin.read()
                    else:
                        self.calibrate_ph_meter()

            # Adjust pH as necessary
            if t > self.ADJUSTMENT_INTERVAL: # Time to adjust the pH
                pH = self.read_ph_meter()
                if pH < (self.PH_TARGET - self.PH_ERROR): # Too acidic
                    self.drip(self.pump_2) # Drip from basic reservoir
                elif pH > (self.PH_TARGET + self.PH_ERROR): #Too basic
                    self.drip(self.pump_1) # Drip from acidic reservoir
                t = 0 # reset the timer

            # Update LED
            if not t % 10000: # update the screen every 10 seconds
                if not running_flag:
                    self.lcd_write('HELLO BARNEY')
                    self.lcd_write('NOT RUNNING', 1)
                else:
                    temperature, humidity = 21.1, 76 # self.read_dht()
                    pH = self.read_ph_meter()
                    self.lcd_write(u'{:.1f}\xdfC {:d}% pH {:.1f}'.format(temperature, humidity, pH))
                    self.lcd_write('{} to next'.format(self.ms_to_hhmmss(self.ADJUSTMENT_INTERVAL-t)), 1)


            t += self.SLEEP
            time.sleep_ms(self.SLEEP)

