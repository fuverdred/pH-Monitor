'''
================================================================================                                                                   
           ,--.  ,--.    ,--.   ,--.               ,--.  ,--.                 
     ,---. |  '--'  |    |   `.'   | ,---. ,--,--, `--',-'  '-. ,---. ,--.--. 
    | .-. ||  .--.  |    |  |'.'|  || .-. ||      \,--.'-.  .-'| .-. ||  .--' 
    | '-' '|  |  |  |    |  |   |  |' '-' '|  ||  ||  |  |  |  ' '-' '|  |    
    |  |-' `--'  `--'    `--'   `--' `---' `--''--'`--'  `--'   `---' `--'    
    `--'
================================================================================
--------------------------------------------------------------------------------
This device reads the pH of a water bath at a given frequency, and uses two
peristaltic pumps to supply an acid/base mixture to maintain the pH of the bath.
--------------------------------------------------------------------------------

The button pin out is:
########(3)###
#(1)##(2)#(5)#
########(4)###
where:
1. START:     Begin monitoring the process. The first adjustment won't be made
              until frequency has elapsed.
2. STOP:      Stop monitoring and adjusting the pH.
3. PRIME 1:   Run pump 1 to allow it to be primed with fluid.
4. PRIME 2:   Run pump 2 to allow it to be primed with fluid.
5. CALIBRATE: Calibrate the pH meter to a known value

Note that pressing multiple buttons at the same time is not supported and will
default to the higher button number.

PUMP 1: Green/Red
Place in the acidic reservoir to lower the pH when needed

PUMP 2: Black/Red
Place in the basic reservoir to raise the pH when needed

================================================================================
Instructions
================================================================================
1.  Attach crocodile clips to peristaltic pumps. The green and red pair need to
    to the pump in the acidic reservoir. Make sure the red wire comes from the
    terminal adjacent to the green wire. The other pair come from the other
    side of the box. The pumps have freewheeling diodes soldered on. Attach the
    red crocodile clip to the electrode which the grey end of the diode is
    soldered to. The same for the basic reservoir.

2.  Plug in the power supply, the unit will turn on. The pumps will run briefly.

3.  Prime the pumps. For each pump insert both tubes into the reservoir and hold
    the prime pump button (3 or 4). Air bubbles will come out of one end. Keep
    running until there are no more bubbles, then place that end of tube above
    the water bath so that it can drip into it when needed.

4.  Press the start button, the screen will change from 'Hello' to displaying
    the current status (temperature, humidity, pH and time to next adjustment).

5.  Calibration. I don't know how often it should be done, perhaps on comparison
    to a reading from your own pH meter. Remove the pH meter from the water bath
    and give it a rinse, then place in the known buffer, which should be 6.8.
    Let the pH settle, then press the calibrate button (button 5). The screen
    will display 'calibrated' when completed.

notes:
 -  Because of the shitty way I have written the program it only checks for
    button presses every 200ms, so you might have to hold the button for a short
    while.
 -  As of writing this each drip from the pump is approximately 0.05 ml
    (corresponding to 20ms pulse of the pumps). This can be increased if needed,
    I haven't worked out how much you will need to dilute the solutions. At the
    moment I have it making a change every 2 hours.
'''

import time
from collections import namedtuple

limits = namedtuple('limit', 'lower upper')

class PH_Monitor:
    DRIP_TIME = 20 # (ms), time it takes to deliver one drip
    ADJUSTMENT_INTERVAL = 1000 * 60 * 60 * 2# (ms) time between pH measurements
    SLEEP = 200 # (ms), time between checking for button presses
    DEBOUNCE = 2 # (ms) button debounce time

    PH_GRADIENT = 6.17E-3 # From measurements
    PH_OFFSET = -7.7 # From measurements
    PH_TARGET = 5.8 # Hold bath at PH_TARGET
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
                 dht, # DHT22 class
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
        return self.dht.temperature(), self.dht.humidity()

    def calibrate_ph_meter(self, calibration=6.86):
        '''Record the analogue read value for a known pH'''
        measured_pH = self.read_ph_meter()
        print('Error = ', calibration - measured_pH)
        self.PH_OFFSET += calibration - measured_pH

    def analogue_to_ph(self, value):
        return (value * self.PH_GRADIENT) + self.PH_OFFSET

    def read_ph_meter(self, repeats=500):
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
                        self.lcd_write('CALIBRATED')
                        time.sleep(1)

            #Update LED
            if not t % 10000: # update the screen every 10 seconds
                if not running_flag:
                    self.lcd_write('HELLO BARNEY')
                    self.lcd_write('NOT RUNNING', 1)
                else:
                    temperature, humidity = self.read_dht()
                    pH = self.read_ph_meter()
                    self.lcd_write(u'{:.1f}\xdfC   {:d}%'.format(temperature, int(humidity)))
                    self.lcd_write('pH {:.1f}  {}'.format(pH, self.ms_to_hhmmss(self.ADJUSTMENT_INTERVAL-t)),1)

            if t > self.ADJUSTMENT_INTERVAL:
                pH = self.read_ph_meter()
                if pH > self.PH_TARGET + self.PH_ERROR: # Need to pump from the acidic reservoir
                    self.drip(self.pump_1)
                elif pH < self.PH_TARGET - self.PH_ERROR: # Need to pump from the basic reservoir
                    self.drip(self.pump_2)
                t = 0 # Reset the timer
            t += self.SLEEP
            time.sleep_ms(self.SLEEP)

