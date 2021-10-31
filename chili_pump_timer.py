#!/usr/bin/python3.7
'''
This script controlling pump and valves based on timer
'''

import troykahat
import time
import logging
import argparse,sys
from time import sleep
from threading import Thread

#Logger configuration
logger=logging.getLogger()
logger.setLevel(logging.INFO)
formatter=logging.Formatter('%(asctime)s %(name)s %(levelname)s: %(message)s')
#Logger to file
fh=logging.FileHandler('/home/pi/projects/results/logs/Chili_pump_timer.log')
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)
#Logger to console
ch=logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)

logger.info('Script started')

#format for --help
class CustomFormatter(argparse.RawDescriptionHelpFormatter, argparse.ArgumentDefaultsHelpFormatter):
    pass

#Parsing in user input positional arguments
parser=argparse.ArgumentParser(description=sys.modules[__name__].__doc__, formatter_class=CustomFormatter)
parser.add_argument(dest='pin_valve', type=int, choices=[1,2,3,4,5,6], help='Digital pin where connected valve.')
parser.add_argument(dest='working_time', type=int, help='Seconds for activate pump.')

try:
    args=parser.parse_args()
except AttributeError:
    logger.critical(f'Not enought attributes for work. Read --help')
    sys.exit(1)
    
pin_valve=args.pin_valve
working_time=args.working_time
logger.info(f'User input: valve pin = {pin_valve}, working time = {working_time}')

MAX_TIME=95 #Equil 2.5 liters
if working_time>MAX_TIME:
    logger.critical(f'User input too long working time={working_time}. Max time={MAX_TIME}')
    raise ValueError (f'You choose long time for working of pump. Please set time below {MAX_TIME} seconds.')    
    sys.exit(1)

#This is statement of pump and valve. Switch to false for disable.
work_signal=True
#Enable troykahat digital pins
wp = troykahat.wiringpi_io()

def activate_pump_timer(PIN_WP_MOSF,SECONDS_WORK):
    '''
    This module activate pump.
    '''
    #Digital pin for controlling pump. Its switched on via a mosfet N-type (normally disabled)
    wp.pinMode(PIN_WP_MOSF, wp.OUTPUT)
    global work_signal    
    try:
        #Changing mosfet statement
        wp.digitalWrite(PIN_WP_MOSF, True) #set True for enable
        logger.info(f'Digital pin {PIN_WP_MOSF} enabled, pump activated')
        for i in range(SECONDS_WORK):
            if work_signal is True:
                sleep(1)

    except Exception as e:
        logging.exception('Exception occured')  
    finally:
        #Changing mosfet statement
        wp.digitalWrite(PIN_WP_MOSF, False)
        logger.info(f'Digital pin {PIN_WP_MOSF} disabled, pump disabled')
        
def activate_valve_timer(PIN_WP_MOSF,SECONDS_WORK):
    '''
    This module open valve.
    '''
    #Digital pin for controlling pump. Its switched on via a mosfet N-type (normally disabled)
    wp.pinMode(PIN_WP_MOSF, wp.OUTPUT)
    global work_signal  
    try:        
        #Changing mosfet statement
        wp.digitalWrite(PIN_WP_MOSF, True) #set True for enable
        logger.info(f'Digital pin {PIN_WP_MOSF} enabled, valve opened')
        for i in range(SECONDS_WORK):
            if work_signal is True:
                sleep(1)

    except Exception as e:
        logging.exception('Exception occured')
    finally:
        #Changing mosfet statement
        wp.digitalWrite(PIN_WP_MOSF, False)
        logger.info(f'Digital pin {PIN_WP_MOSF} disabled, valve closed')

def irrigation_timer(VALVE, SECONDS_WORK):
    '''
    Combines the operation of the pump and valves.
    '''
    
    try:
        thread1=Thread(target=activate_valve_timer, args=(VALVE,SECONDS_WORK,))
        thread2=Thread(target=activate_pump_timer, args=(7,SECONDS_WORK,))
        
        thread1.start()
        thread2.start()
        thread1.join()
        thread2.join()
        
        logger.info('Script finished')
    except (KeyboardInterrupt, SystemExit):        
        global work_signal
        work_signal=False
        logging.exception('Exception occured')
        logger.info('Script interrupted')
    finally:
        wp.digitalWrite(VALVE, False)
        wp.digitalWrite(7, False)
def main():
    irrigation_timer(pin_valve,working_time)
    
if __name__=='__main__':
    main()

