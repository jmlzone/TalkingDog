# Import all the libraries we need to run
import RPi.GPIO as GPIO
import smbus
import gpTimer
import threading
import time
""" User IO pin naames
"""
GPA0 = 0
GPA1 = 1
GPA2 = 2
GPA3 = 3
GPA4 = 4
GPA5 = 5
GPA6 = 6
GPA7 = 7
GPB0 = 8
GPB1 = 9
GPB2 = 10
GPB3 = 11
GPB4 = 12
GPB5 = 13
GPB6 = 14
GPB7 = 15
# HWIO directions
INPUT = 1
OUTPUT = 0
# interupt directions same as GPIO
RISING = 31
FALLING = 32
BOTH = 33
PUD_UP = 22
PUD_OFF = 20
# the MCP23017 does not have a pull down
""" MCP23008 Register names
"""
IODIR    = 0
IPOL     = 1
GPINTEN  = 2
DEFVAL   = 3
INTCON   = 4
IOCON    = 5
GPPU     = 6
INTF     = 7
INTCAP   = 8
GPIOR    = 9
OLAT     = 10
""" MCP23017 Register names
"""
IODIRA   =  0  # 1 = input, 0 = output
IODIRB   =  1
IPOLA    =  2  # 1 = Interrupt inverted from IO state
IPOLB    =  3
GPINTENA =  4  # Interupt on change
GPINTENB =  5
DEFVALA  =  6  # Default value for interupt on change compare
DEFVALB  =  7
INTCONA  =  8  # 1 = compare aginst def val, 0= compare against previous value
INTCONB  =  9
IOCONA   = 10
IOCONB   = 11
GPPUA    = 12 # Enables Pullups
GPPUB    = 13
INTFA    = 14 # Interrupt flags
INTFB    = 15
INTCAPA =  16 # Captured values when an interup occurs
INTCAPB =  17
GPIOA   =  18 # IO Values
GPIOB   =  19
OLATA   =  20 # read back written value
OLATB   =  21
""" The MCP23017 and MCP23008 base address is the same as the max7314 default used in the kenwoods instead of PROMs
"""
MCP23017BASE = 32
GPIOEX0 = MCP23017BASE
GPIOEX1 = MCP23017BASE +1
GPIOEX2 = MCP23017BASE +2
GPIOEX3 = MCP23017BASE +3
GPIOEX4 = MCP23017BASE +4
INTPOL = 1<<1 # Interupt polarity, 1 = active high
ODR    = 1<<2 # Open drain for the interupt pins, 1= open drain active low
HAEN   = 1<<3 # used in spi only to ignore the address pins
DISSLW = 1<<4 # disables slew rate control when 1
SEQOP  = 1<<5 # automatic address incementing disabled when 1
MIRROR = 1<<6 # both interpt pins do the same thing
BANK   = 1<<7 # Keep as zero or address map is different
""" user IO related pins
"""
UINTA = 12

class buttonio :
    def __init__ (self,multiClick=True) :
        self.buttonQueue=[]
        self.multiClick = multiClick
        self.intf = 0
        self.val = 0
        self.waitCB = False
        if(self.multiClick) :
            self.buttons = []
            for b in range(16) :
                self.buttons.append(button(b,self))
            self.CBTimer = gpTimer.gpTimer(0.025, userHandler = self.timerCB)
        else:
            self.debounce = 0
            self.debounceTimer = gpTimer.gpTimer(0.5, userHandler = self.debounceCB)
        self.event = threading.Event()
        self.event.clear()
        GPIO.setmode(GPIO.BOARD)
        self.haveIO = {GPIOEX0:True, GPIOEX1:True}
        try:
            self.i2cBus = smbus.SMBus(1)
        except:
            print("I2C is not enabled on the pi, please enmable it")
            # IOEX0 is the button inputs 
        try:
            self.i2cBus.write_byte_data(GPIOEX0, IODIRA,0xff) # port as input
            self.i2cBus.write_byte_data(GPIOEX0, IODIRB,0xff) # port as input
            self.i2cBus.write_byte_data(GPIOEX0, GPPUA,0xff) # turn on pullups
            self.i2cBus.write_byte_data(GPIOEX0, GPPUB,0xff) # turn on pullups
            self.i2cBus.write_byte_data(GPIOEX0, DEFVALA,0xff) # default all 1
            self.i2cBus.write_byte_data(GPIOEX0, DEFVALB,0xff) # default all 1
            self.i2cBus.write_byte_data(GPIOEX0, IOCONA,(MIRROR|INTPOL)) # both int pins same (only one used)
            self.i2cBus.write_byte_data(GPIOEX0, GPINTENA,0xff) # enable all interupts
            self.i2cBus.write_byte_data(GPIOEX0, GPINTENB,0xff) # enable all interupts
        except:
            self.haveIO[GPIOEX0] = False
        # IOEX1 is the leds in the buttons
        try:
            self.i2cBus.write_byte_data(GPIOEX1, IODIRA,0) # port as output
            self.i2cBus.write_byte_data(GPIOEX1, IODIRB,0) # port as output
            self.i2cBus.write_byte_data(GPIOEX1, GPIOA,0xff) # Turn off all leds
            self.i2cBus.write_byte_data(GPIOEX1, GPIOB,0xff) # turn off all leds

        except:
            self.haveIO[GPIOEX1] = False
        if(self.haveIO[GPIOEX0]) :
            GPIO.setup(UINTA, GPIO.IN)
            self.intclr()
            GPIO.add_event_detect(UINTA, GPIO.RISING, callback=self.uinta)
            print("Have GPIOEX0 OK")
        else :
            print("Check I2C connections no GPIOEX0 so this won't work")

        if(self.haveIO[GPIOEX1]) :
            print("Have GPIOEX1 OK")
        else :
            print("Check I2C connections no GPIOEX1 so no leds")
    def i2cSafeWrite(self,busaddr,regaddr,val) :
        if (self.haveIO[busaddr]) :
            try: 
                self.i2cBus.write_byte_data(busaddr, regaddr, val)
            except:
                pass
    def i2cSafeRead(self,busaddr,regaddr) :
        val = 0xff
        if (self.haveIO[busaddr]) :
            try: 
                val = self.i2cBus.read_byte_data(busaddr, regaddr)
            except:
                pass
        return(val)

    def uinta(self,pin) :
        vala = self.i2cSafeRead(GPIOEX0,INTFA)
        #print("val A %d " %vala)
        valb = self.i2cSafeRead(GPIOEX0,INTFB)
        #print("val B %d " %valb)
        self.intf = self.intf | vala  | (valb <<8)
        print("intf = %x" % self.intf)
        vala = self.i2cSafeRead(GPIOEX0,GPIOA)
        #print("val A %d " %vala)
        valb = self.i2cSafeRead(GPIOEX0,GPIOB)
        #print("val B %d " %valb)
        self.val =  vala  | (valb <<8)
        print("val = %x" % self.val)
        self.intclr()
        if(self.multiClick) :
            self.waitCB = False
            # call all the multi clickers
            for n in range(16) :
                self.buttons[n].update((self.val>>n) & 1)
            if(self.waitCB) :
                self.CBTimer.reset()
        else:
            # next add the low pin(s) to the queue
            for n in range(16) :
                if((self.intf & 1<<n) and not (self.debounce & 1<<n)) :
                    self.buttonQueue = self.buttonQueue + ([n],'click')
            self.debounce = self.debounce | self.intf
            self.debounceTimer.reset()
        self.intf = 0
        if(len(self.buttonQueue)) :
            self.event.set()

    def intclr(self) :
        # reading incap and gpio clear the interupt condition.
        intcapA = self.i2cSafeRead(GPIOEX0,INTCAPA) 
        intcapB = self.i2cSafeRead(GPIOEX0,INTCAPB)
        # read above
        #inctrlA = self.i2cSafeRead(GPIOEX0,GPIOA)
        #inctrlB = self.i2cSafeRead(GPIOEX0,GPIOB)

    def debounceCB(self):
        self.debounce = 0
        self.debounceTimer.stop()

    def timerCB(self):
        self.CBTimer.stop()
        self.uinta(0)

    def ledon(self,led) :
        if(led <8) :
            v=1<<led
            p=GPIOA
        else :
            v=1<<(led-8)
            p=GPIOB
        v = ~v & 0xff
        self.i2cSafeWrite(GPIOEX1,port,v)
    def ledoff(self,led) :
        if(led <8) :
            v=1<<led
            p=GPIOA
        else :
            v=1<<(led-8)
            p=GPIOB
        v = ~v & 0xff
        self.i2cSafeWrite(GPIOEX1,port,0xff)

LOW = 0
HIGH = 1
debounce = 20
DCgap = 250
holdTime = 1000
longHoldTime = 3000
class button:
    def __init__(self,id,parent):
        self.id = id;
        self.parent=parent
        self.val = HIGH
        self.last = HIGH
        self.DCwaiting = False
        self.DConUp = False
        self.singleOK = True
        self.downTime = 0
        self.upTime = 0
        self.ignoreUp = False
        self.waitForUp = False
        self.holdEventPast = False
        self.longHoldEventPast = False
        self.clicktype = None
    def mils(self):
        return(round(time.time() * 1000))
    def update(self,val) :
        #if(val == self.val) : # no change
        #    return()
        self.val=val
        # Button pressed down
        if (self.val == LOW and self.last == HIGH and (self.mils() - self.upTime) > debounce):
            self.downTime = self.mils()
            self.ignoreUp = False
            self.waitForUp = False
            self.singleOK = True
            self.holdEventPast = False
            self.longHoldEventPast = False
            if ((self.mils()-self.upTime) < DCgap and self.DConUp == False and self.DCwaiting == True):
                self.DConUp = True
            else :
                self.DConUp = False
            self.DCwaiting = False
        # Button released
        elif (self.val == HIGH and self.last == LOW and (self.mils() - self.downTime) > debounce) :
            if (not self.ignoreUp) :
                self.upTime = self.mils()
                if (self.DConUp == False):
                    self.DCwaiting = True
                else:
                    self.clicktype = 'doubleClick'
                    self.DConUp = False
                    self.DCwaiting = False
                    self.singleOK = False
        # Test for normal click event: DCgap expired
        if ( self.val == HIGH and (self.mils()-self.upTime) >= DCgap and self.DCwaiting == True
             and self.DConUp == False and self.singleOK == True and self.clicktype != 'doubleClick'):
            self.clicktype = 'click'
            self.DCwaiting = False
        # Test for hold
        if (self.val == LOW and (self.mils() - self.downTime) >= holdTime) :
           # Trigger "normal" hold
           if (not self.holdEventPast) :
               self.clicktype = 'hold'
               self.waitForUp = True
               self.ignoreUp = True
               self.DConUp = False
               self.DCwaiting = False
               self.holdEventPast = True
           # Trigger "long" hold
        if ((self.mils() - self.downTime) >= longHoldTime):
           if (not self.longHoldEventPast):
               self.clicktype = 'longHold'
               self.longHoldEventPast = True
        self.last = self.val
        if(self.DCwaiting or self.waitForUp) :
            self.parent.waitCB = True
        if(self.clicktype != None) :
            self.parent.buttonQueue.append((self.id,self.clicktype))
            self.clicktype = None
