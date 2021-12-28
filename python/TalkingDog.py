#!/usr/bin/python3
import buttonio
import alsaaudio
import subprocess
import time
import os
import recorder
r=recorder.recorder()
r.detect()
root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..' ))
print("running from %s" % root)
sounddir = os.path.join(root,"sounds")
dictf =  os.path.join(root,'python/buttonDict.py')
if(os.path.isfile(dictf) and os.access(dictf,os.R_OK)) :
   from buttonDict import sounddict
else:
   sounddict = {0:'zero.wav', 1:'one.wav',2:'two.wav',3:'three.wav',4:'four.wav', 5:'busybone.wav'}
tout = os.path.join(root,'bin/tout')
#p=subprocess.Popen(['/usr/bin/aplay', '-D', 'sysdefault:CARD=Device', '../sounds/audiocheck.net_dtmf_1.wav'])
## audio setup now in recorder.py
##cards = len(alsaaudio.cards()) -1
##m=alsaaudio.mixers(cards)
##mix =  alsaaudio.Mixer(control='PCM', cardindex=cards)
##mix.setvolume(75,0,alsaaudio.PCM_PLAYBACK)
##v = mix.getvolume()
##print("volume set to %s" % str(v))
buttons = buttonio.buttonio()
soundf = os.path.join(sounddir, 'ready.wav')
#p=subprocess.Popen(['/usr/bin/aplay', '-D', 'sysdefault:CARD=Device', soundf])
p=subprocess.Popen(['/usr/bin/aplay', '-D', r.speakerLong, soundf])
p.wait()
if(r.have_mic())  :
    soundf = os.path.join(sounddir, 'record.wav')
    p=subprocess.Popen(['/usr/bin/aplay', '-D', r.speakerLong, soundf])
    p.wait()
print("startup done")
while True:
    #time.sleep(1)
    buttons.event.wait()
    while (len(buttons.buttonQueue) > 0) :
        (b,c) = buttons.buttonQueue.pop(0)
        print("got button %d, clock type %s" % (b,c))
        if(r.have_mic() and c== 'doubleClick'):
            soundf = os.path.join(sounddir, 'b%d.wav' %b)
            r.recordingSequence(soundf,tout)
            sounddict[b] = 'b%d.wav' % b
            f = open(dictf,'w')
            f.write("sounddict =  %s" % str(sounddict))
            f.close()
        if( b in sounddict and not 'longHold' in c) :
            soundf = os.path.join(sounddir, sounddict[b])
            if(os.path.isfile(soundf) ) :
                p=subprocess.Popen(['/usr/bin/aplay', '-D', r.speakerLong, soundf])
                p.wait()
            else :
                print("could not play %s" % soundf)
        else :
            print("%s was not found in the sound dictionary" % str(b))
    buttons.event.clear()            
