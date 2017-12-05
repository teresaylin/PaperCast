import os
from gtts import gTTS

tts = gTTS(text="hello world", lang="en")
tts.save("good.mp3")
os.system("espeak 'hello world'")

