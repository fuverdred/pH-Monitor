import time
from pyb import Pin, I2C, ADC
import dht

from pyb_i2c_lcd import I2cLcd
from PH_Monitor import PH_Monitor

LCD_ADDRESS = 0x27

pump_1 = Pin('Y9', mode=Pin.OUT_PP)
pump_2 = Pin('Y10', mode = Pin.OUT_PP)

button_pin = ADC('X11')
ph_pin = ADC('X7')

d_temp_humid = dht.DHT22(Pin('X6'))


i2c = I2C(1, I2C.MASTER)
lcd = I2cLcd(i2c, LCD_ADDRESS, 2, 16)

ph_monitor = PH_Monitor(ph_pin,
                        button_pin,
                        pump_1,
                        pump_2,
                        d_temp_humid,
                        lcd)

ph_monitor.loop()
