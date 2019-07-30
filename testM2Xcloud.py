#!/usr/bin/env python
#
#
# Test All for Pi  SGS
#
# SwitchDoc Labs, September 2018 
#

#imports 

import sys
import RPi.GPIO as GPIO
import time
import threading
from m2x.client import M2XClient


#appends
sys.path.append('./SDL_Pi_HDC1000')
sys.path.append('./SDL_Pi_SSD1306')
sys.path.append('./Adafruit_Python_SSD1306')
sys.path.append('./SDL_Pi_SI1145')
sys.path.append('./SDL_Pi_Grove4Ch16BitADC/SDL_Adafruit_ADS1x15')
sys.path.append('./SDL_Pi_GroveDigitalExtender')


import SDL_Pi_HDC1000

import Adafruit_SSD1306

import Scroll_SSD1306

import ultrasonicRanger

from SDL_Adafruit_ADS1x15 import ADS1x15

import AirQualitySensorLibrary 

import SDL_Pi_SI1145
import SI1145Lux

import state
import extendedPlants

# Check for user imports
try:
            import conflocal as config
except ImportError:
            import config


###############
#initialization
###############


###############
# Sunlight SI1145 Sensor Setup
################


try:
        Sunlight_Sensor = SDL_Pi_SI1145.SDL_Pi_SI1145()
        time.sleep(1)
        state.Sunlight_Visible = SI1145Lux.SI1145_VIS_to_Lux(Sunlight_Sensor.readVisible())

        config.Sunlight_Present = True
except:
        config.Sunlight_Present = False


###############
# Ultrasonic Level Sensor
###############
GPIO.setup(config.UltrasonicLevel, GPIO.IN)  
	 


################
#4 Channel ADC ADS1115 Ext1 setup
################
# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
ADS1115 = 0x01  # 16-bit ADC

ads1115_ext1 = ADS1x15(ic=ADS1115, address=0x49)

# Select the gain
gain = 6144  # +/- 6.144V
#gain = 4096  # +/- 4.096V

# Select the sample rate
sps = 250  # 250 samples per second
# determine if device present
try:
       value = ads1115_ext1.readRaw(0, gain, sps) # AIN0 wired to AirQuality Sensor
       time.sleep(1.0)
       value = ads1115_ext1.readRaw(0, gain, sps) # AIN0 wired to AirQuality Sensor

       config.ADS1115_Ext1_Present = True

except TypeError as e:
       config.ADS1115_Ext1_Present = False


################
#4 Channel ADC ADS1115 Ext2 setup
################
# requries I2C Mux - wait for later

ads1115_ext2 = None
config.ADS1115_Ext2_Present = False



################
#Set all LEDs to Green
################



################
#SSD 1306 setup
################

# OLED SSD_1306 Detection

try:
        RST =27
        display = Adafruit_SSD1306.SSD1306_128_64(rst=RST, i2c_address=0x3C)
        # Initialize library.
        display.begin()
        display.clear()
        display.display()
        config.OLED_Present = True
except:
        config.OLED_Present = False

################
#4 Channel ADC ADS1115 setup
################
# Set this to ADS1015 or ADS1115 depending on the ADC you are using!
ADS1115 = 0x01  # 16-bit ADC

ads1115 = ADS1x15(ic=ADS1115, address=0x48)

# Select the gain
gain = 6144  # +/- 6.144V
#gain = 4096  # +/- 4.096V

# Select the sample rate
sps = 250  # 250 samples per second
# determine if device present
try:
       value = ads1115.readRaw(0, gain, sps) # AIN0 wired to AirQuality Sensor
       time.sleep(1.0)
       value = ads1115.readRaw(0, gain, sps) # AIN0 wired to AirQuality Sensor

       config.ADS1115_Present = True

except TypeError as e:
       config.ADS1115_Present = False


################
# HDC1000 Setup
################
config.HDC1000_Present = False
try:

    hdc1000 = SDL_Pi_HDC1000.SDL_Pi_HDC1000()
    config.hdc1000_Present = True

except:
    config.hdc1000_Present = False


def returnStatusLine(device, state):

        returnString = device
        if (state == True):
                returnString = returnString + ":   \t\tPresent"
        else:
                returnString = returnString + ":   \t\tNot Present"
        return returnString

if (config.OLED_Present):
      Scroll_SSD1306.addLineOLED(display,  ("    Welcome to "))
      Scroll_SSD1306.addLineOLED(display,  ("   Smart Garden "))


############
# Setup Moisture Pin for GrovePowerSave
############
GPIO.setup(config.moisturePower,GPIO.OUT)
GPIO.output(config.moisturePower, GPIO.LOW)

#


try:  

        
        # Creating M2X Client and device

        client = M2XClient(key='3e296370312002710e5019d6b4a4b512')
        device = client.device('cb3eed668dcb1cdf4e3b42df2c4fa00e')
        temperature_stream=device.streams()[0]
        humidity_stream = device.streams()[1]
        visible_light_strean = device.streams()[2]
        ir_light_strean = device.streams()[3]
        uv_light_stream = device.streams()[4]
        soil_moisture_stream = device.streams[5]
        water_tank_stream = device.streams[6]

        # read temp humidity

        degrees= hdc1000.readTemperature()
        humidity = hdc1000.readHumidity()

        print 'Temp             = {0:0.3f} deg C'.format(degrees)
        print 'Humidity         = {0:0.2f} %'.format(humidity)

        if (config.OLED_Present):
                Scroll_SSD1306.addLineOLED(display,  ("Temp = \t%0.2f C")%(degrees))
                Scroll_SSD1306.addLineOLED(display,  ("Humidity =\t%0.2f %%")%(humidity))

        print "----------------- "
        if (config.Sunlight_Present == True):
                            print " Sunlight Vi/IR/UV Sensor"
        else:
                            print " Sunlight Vi/IR/UV Sensor Not Present"
        print "----------------- "

        #Read sun light

        if (config.Sunlight_Present == True):
                ################
                SunlightVisible = Sunlight_Sensor.readVisible()
                SunlightIR = Sunlight_Sensor.readIR()
                SunlightUV = Sunlight_Sensor.readUV()
                SunlightUVIndex = SunlightUV / 100.0
                print 'Sunlight Visible:  ' + str(SunlightVisible)
                print 'Sunlight IR:       ' + str(SunlightIR)
                print 'Sunlight UV Index: ' + str(SunlightUVIndex)
                ################

        	if (config.OLED_Present):
                	Scroll_SSD1306.addLineOLED(display,  ("Sunlight = \t%0.2f Lum")%(SunlightVisible))

        
        #moisture humidity and air quality
        if (config.ADS1115_Present):
            GPIO.output(config.moisturePower, GPIO.HIGH)
            Moisture_Humidity   = ads1115.readADCSingleEnded(config.moistureADPin, gain, sps)/7 # AIN0 wired to AirQuality Sensor
            GPIO.output(config.moisturePower, GPIO.LOW)

            print Moisture_Humidity
	    Moisture_Humidity = Moisture_Humidity / 7.0
            if (Moisture_Humidity >100): 
                Moisture_Humidity = 100;
            print "Moisture Humidity = %0.2f" % (Moisture_Humidity)
            print"------------------------------"

            sensor_value =  AirQualitySensorLibrary.readAirQualitySensor(ads1115)

            sensorList = AirQualitySensorLibrary.interpretAirQualitySensor(sensor_value)
            print "Sensor Value=%i --> %s  | %i"% (sensor_value, sensorList[0], sensorList[1])
        
        else:
                            print " Humidity and air quality Not Present"
        print "----------------- "
                 
	if (config.UltrasonicLevel_Present):
                water_tanklevel=ultrasonicRanger.measurementInCM()
		print "Ultrasonic Level " + str(water_tanklevel) + " cm"
		



        # Adding value to streams.

        temperature_stream.add_value(degrees)
        humidity_stream.add_value(humidity)
        visible_light_strean.add_value(SunlightVisible)
        ir_light_strean.add_value(SunlightIR)
        uv_light_stream.add_value(SunlightUVIndex)
        soil_moisture_stream.add_value(Moisture_Humidity)
        water_tank_stream.add_value(water_tanklevel)

except KeyboardInterrupt:  
    	# here you put any code you want to run before the program   
    	# exits when you press CTRL+C  
        print "exiting program" 
