"""
🎵 Procedural Audio Generator (100% Royalty-Free, Zero External Dependencies)
NASA Space Apps 2026 - Team RIP

Uses Python's standard library `wave` and `math` to synthesize custom sound effects:
1. thruster.wav: Low-frequency modulated spacecraft thruster hum
2. target_lock.wav: Dual-tone resonant sonar chime for locking onto moving objects
"""

import math
import os
import struct
import wave

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "frontend", "audio")
os.makedirs(OUTPUT_DIR, exist_ok=True)

SAMPLE_RATE = 44100

def create_wave_file(filename, samples):
    filepath = os.path.join(OUTPUT_DIR, filename)
    with wave.open(filepath, 'w') as wav:
        wav.setnchannels(1)      # Mono
        wav.setsampwidth(2)      # 16-bit
        wav.setframerate(SAMPLE_RATE)

        for sample in samples:
            clamped = max(-1.0, min(1.0, sample))
            val = int(clamped * 32767.0)
            wav.writeframesraw(struct.pack('<h', val))
    print(f"✅ Generated: {filepath} ({len(samples)} samples)")

def generate_thruster_sound(duration_sec=0.8):
    total_samples = int(SAMPLE_RATE * duration_sec)
    samples = []

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Envelope: fast attack, smooth decay
        envelope = math.sin(math.pi * (i / total_samples))

        # Dual modulated low frequencies: 75Hz and 110Hz + subtle pink noise rumble
        f1 = math.sin(2 * math.pi * 75 * t)
        f2 = math.sin(2 * math.pi * 110 * t) * 0.5
        f3 = math.sin(2 * math.pi * 42 * t) * 0.3

        # Pseudo-noise
        pseudo_noise = ((math.sin(i * 12.9898) * 43758.5453) % 1.0 - 0.5) * 0.15

        sample = (f1 + f2 + f3 + pseudo_noise) * envelope * 0.45
        samples.append(sample)

    create_wave_file("thruster.wav", samples)

def generate_target_lock_sound(duration_sec=0.45):
    total_samples = int(SAMPLE_RATE * duration_sec)
    samples = []

    for i in range(total_samples):
        t = i / SAMPLE_RATE
        # Envelope: exponential decay
        envelope = math.exp(-6.0 * (i / total_samples))

        # Chime: 880 Hz (A5) + 1320 Hz (E6) harmonic
        tone1 = math.sin(2 * math.pi * 880 * t)
        tone2 = math.sin(2 * math.pi * 1320 * t) * 0.6
        tone3 = math.sin(2 * math.pi * 1760 * t) * 0.25

        sample = (tone1 + tone2 + tone3) * envelope * 0.4
        samples.append(sample)

    create_wave_file("target_lock.wav", samples)

if __name__ == "__main__":
    print("Generating procedural sound effects...")
    generate_thruster_sound()
    generate_target_lock_sound()
    print("All audio generated successfully.")
