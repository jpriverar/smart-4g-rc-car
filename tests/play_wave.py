from playsound import playsound
import wave, struct, math, random


sampleRate = 44100.0 # hertz
duration = 1.0 # seconds
frequency = 440.0 # hertz

obj = wave.open('D:\OTROS\Smart-RC\Software Tests\sound.wav','w')
obj.setnchannels(1) # mono
obj.setsampwidth(2)
obj.setframerate(sampleRate)

for i in range(99999):
   value = random.randint(-32767, 32767)
   data = struct.pack('<h', value)
   obj.writeframesraw( data )

obj.close()

playsound('D:\OTROS\Smart-RC\Software Tests\sound.wav')