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
