#!/usr/bin/python3
import buttonio
import alsaaudio
import subprocess
import time
import os
sounddict = {1:'one.wav',2:'two.wav',3:'three.wav',4:'four.wav'}
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..' ))
print("running from %s" % root)
sounddir = os.path.join(root,"sounds")
#p=subprocess.Popen(['/usr/bin/aplay', '-D', 'sysdefault:CARD=Device', '../sounds/audiocheck.net_dtmf_1.wav'])
cards = len(alsaaudio.cards()) -1
m=alsaaudio.mixers(cards)
mix =  alsaaudio.Mixer(control='PCM', cardindex=cards)
mix.setvolume(75,0,alsaaudio.PCM_PLAYBACK)
v = mix.getvolume()
print("volume set to %s" % str(v))
soundf = os.path.join(sounddir, 'ready.wav')
p=subprocess.Popen(['/usr/bin/aplay', '-D', 'sysdefault:CARD=Device', soundf])
p.wait()
print("startup done")
buttons = buttonio.buttonio()
while True:
    #time.sleep(1)
    buttons.event.wait()
    while (len(buttons.buttonQueue) > 0) :
        p = buttons.buttonQueue.pop(0)
        print("got button %d" % p)
        if( p in sounddict) :
            soundf = os.path.join(sounddir, sounddict[p])
            if(os.path.isfile(soundf) ) :
                p=subprocess.Popen(['/usr/bin/aplay', '-D', 'sysdefault:CARD=Device', soundf])
                p.wait()
            else :
                print("could not play %s" % soundf)
        else :
            print("%s was not found in the sound dictionary" % str(p))
    buttons.event.clear()            
