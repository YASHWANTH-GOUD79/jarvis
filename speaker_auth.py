import sounddevice as sd
import soundfile as sf
import numpy as np
import os

def record_voice(file):
    audio = sd.rec(int(3 * 16000), samplerate=16000, channels=1)
    sd.wait()
    sf.write(file, audio, 16000)

def extract(audio):
    audio = audio.flatten()
    return np.array([audio.mean(), audio.std()])

def register_user():
    features = []
    for i in range(5):
        record_voice(f"s{i}.wav")
        a,_ = sf.read(f"s{i}.wav")
        features.append(extract(a))
    np.save("voice.npy", features)

def verify_user():
    if not os.path.exists("voice.npy"):
        return True

    record_voice("test.wav")
    t,_ = sf.read("test.wav")
    t_feat = extract(t)

    data = np.load("voice.npy")
    scores = [np.linalg.norm(f - t_feat) for f in data]

    return min(scores) < 0.2