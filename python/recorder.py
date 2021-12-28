#!/usr/bin/python3
#sudo apt-get install -y python3-alsaaudio
#pip3 install pydub

import alsaaudio
import pydub
import subprocess

class recorder :
    def __init__(self) :
        self.mic = None
        self.speaker = None
        
    def detect(self):
        c=[]
        c=alsaaudio.cards()
        print("There are %d cards" % len(c) )
        cardList = []
        i=0
        for i in range(len(c)) :
            m = alsaaudio.mixers(i)
            if ('Mic' in m and 'Speaker' in m) :
                print("Card %d: %s has both" % (i,c[i]))
                cardList.append(c[i])
            elif('Mic' in m) :
                print("Card %d: %s is Mic only" % (i,c[i]))
                self.mic = c[i]
                self.micIndex = i
                self.micLong = "sysdefault:CARD=" + self.mic
                mix = alsaaudio.Mixer(control='Mic', cardindex=i)
                mix.setvolume(100,0, alsaaudio.PCM_CAPTURE)
            elif(('Speaker' in m) or ('PCM' in m)) :
                print("Card %d: %s is Speaker only" % (i,c[i]))
                self.speaker = c[i]
                self.speakerIndex = i
                self.speakerLong = "sysdefault:CARD=" + self.speaker
                mix = alsaaudio.Mixer(control=m[0], cardindex=i)
                mix.setvolume(75,0, alsaaudio.PCM_PLAYBACK)
                #mix.setvolume(75,1, alsaaudio.PCM_PLAYBACK)
            else:
                print("Card %d: %s has controls %s" % (i,c[i],str(m)))

    def have_mic(self):
        if(self.mic != None):
            return(True)
        else:
            return(False)

    def record(self,fn,card,duration=5):
        # arecord -D sysdefault:CARD=Device -d 10 -t wav -f S16_LE -r 16000 test.wav
        subprocess.call(['/usr/bin/arecord','-D',card, '-d', str(duration), '-t', 'wav', '-f', 'S16_LE', '-r', '16000', fn ], shell=False)
        pass
    
    def trim(self,soundfile,threshold=-50):
        sound = pydub.AudioSegment.from_file(soundfile , format="wav")
        start_trim = self.detect_leading_silence(sound,threshold)
        end_trim = self.detect_leading_silence(sound.reverse(),threshold)
        duration = len(sound)    
        trimmed_sound = sound[start_trim:duration-end_trim]
        trimmed_sound.export(soundfile , format="wav")

    def detect_leading_silence(self,sound, silence_threshold=-50.0, chunk_size=10):
        '''
        sound is a pydub.AudioSegment
        silence_threshold in dB
        chunk_size in ms
        
        iterate over chunks until you find the first one with sound
        '''
        trim_ms = 0 # ms
        assert chunk_size > 0 # to avoid infinite loop
        while sound[trim_ms:trim_ms+chunk_size].dBFS < silence_threshold and trim_ms < len(sound):
            trim_ms += chunk_size
        return trim_ms

    def recordingSequence(self,soundf,tout):
        p=subprocess.Popen([tout, self.speakerLong, '660', '1500', '300'])
        p.wait()
        self.record(soundf,self.micLong)
        p=subprocess.Popen([tout, self.speakerLong, '660','1500','200', '660','0','100', '660','1500','200'])
        p.wait()
        self.trim(soundf)


