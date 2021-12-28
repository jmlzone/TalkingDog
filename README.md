# TalkingDog
A keyboard of arcade style buttons to teach a dog to talk with a raspberry PI and MCP23017 and ALSA
# Basic Concept:
* Buttons that are big enough and robust enough to have a dog press with a paw.
* When a button is pressed, an audio file is played through a USB speaker.
* Since the 'arcade' buttons also have LED's the hardware can also light them as a teaching aid.
  
# Future type of things easily added:
* Dog can text you (ie whatever the dog keyboards will be sent as an email or text)!
* Dog can get a treat from pushing a button or you can doit via the web
* Raspi camera to see your at the keyboard?
  
# Directories:
* doc/ -- Some drawings/docs in the doc directory.  Likly this will be hand built
* python/ -- the code
* sounds/ -- sound files for the buttons.
* bin/tout -- a simple beep generator I created for PiPtr

# Some of the python files
* TalkingDog.py -- the main code
* gpTImer.py    -- a wrapper class for a general puropse timer making threading.Timer more friendly
* buttonio.py   -- a class for the io on the mcp23107 i2c GPIO expander. Includes software timer button debounce, or includes detection for double click and long hold.
* recorder.py   -- a class and routines for integreated recoding on the target

# requirements
enable I2C on the rasberry pi, install alsaaudio and pydub
        sudo apt-get install -y python3-smbus python3-dev i2c-tools python3-alsaaudio
        sudo pip3 install pydub

# check to see the I2c peripherals work:
        sudo i2cdetect -y 1

# to record and edit the audio files
        sudo apt-get install -y audacity

# To record on the target hardware:
1. Plug a USB microphone into the pi.  Note: a mic only device is expected.  record.py could be modified to understand UDB sound cards.  I have a neat little UDB to XLR microphone adapter I used.
2. When talking dog starts it will recognize the microphone is connected and tell you so.  mic muist be connected before start-up to be detected.
3. double click a button.  You will hear beep.  You have 5 seconds to record a sound for the button.  The timeout can also be adjusted in the python.  The sound will be automatically trimmed to remove leading and trailing silence, Thanks pydub!  The new sound file will be saved in the sounds directory.  A new sound dictionary will be generated and saved in the python directory.

I hope you enjoy.
