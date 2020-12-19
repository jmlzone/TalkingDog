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

# Some of the python files
* TalkingDog.py -- the main code
* gpTImer.py    -- a wrapper class for a general puropse timer making threading.Timer more friendly
* buttonio.py   -- a class for the io on the mcp23107 i2c GPIO expander. Includes software timer button debounce.

# requirments
enable I2C on the rasberry pi
sudo apt-get install -y python3-smbus python3-dev i2c-tools
sudo pip3 install pyalsaaudio

# check to see the I2c peripherals work:
sudo i2cdetect -y 1

# to record and edit the audio files
sudo apt-get install -y audacity
