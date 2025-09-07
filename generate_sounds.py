"""
Script para gerar sons simples para o jogo Perfect Potion.
Gera os seguintes efeitos sonoros:
- collect.wav: Som de coleta de item (um tom curto e agradável)
- damage.wav: Som de dano (um tom mais grave e desagradável)
- explosion.wav: Som de explosão (ruído branco com envelope de decaimento)
- level_up.wav: Som de subida de nível (uma sequência ascendente de tons)
"""

import os
import numpy as np
from scipy.io import wavfile
from scipy import signal
import math

def generate_tone(frequency, duration, sample_rate=44100, volume=0.5):
    """Gera um tom senoidal simples."""
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = np.sin(2 * np.pi * frequency * t) * volume
    return tone

def generate_noise(duration, sample_rate=44100, volume=0.5):
    """Gera ruído branco."""
    noise = np.random.uniform(-1, 1, int(sample_rate * duration)) * volume
    return noise

def apply_envelope(sound, attack=0.05, decay=0.2, sustain=0.7, release=0.3, sample_rate=44100):
    """Aplica um envelope ADSR ao som."""
    total_samples = len(sound)
    envelope = np.ones(total_samples)
    
    # Converte tempos para amostras
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    
    # Aplica ataque
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Aplica decaimento para o nível de sustentação
    if decay_samples > 0:
        start = attack_samples
        end = attack_samples + decay_samples
        if end > total_samples:
            end = total_samples
        decay_env = np.linspace(1, sustain, end - start)
        envelope[start:end] = decay_env
    
    # Aplica release no final
    if release_samples > 0 and release_samples < total_samples:
        start = max(0, total_samples - release_samples)
        release_env = np.linspace(envelope[start], 0, total_samples - start)
        envelope[start:] = release_env
    
    return sound * envelope

def generate_collect_sound():
    """Gera um som de coleta de item."""
    # Um tom agradável e curto
    tone1 = generate_tone(880, 0.1, volume=0.3)  # Lá 5
    tone2 = generate_tone(1318.51, 0.1, volume=0.3)  # Mi 6
    
    # Combina os tons
    sound = np.concatenate([tone1, tone2])
    
    # Aplica um envelope suave
    sound = apply_envelope(sound, attack=0.01, decay=0.1, sustain=0.5, release=0.1)
    
    return sound

def generate_damage_sound():
    """Gera um som de dano."""
    # Um tom grave e desagradável
    tone = generate_tone(220, 0.3, volume=0.4)  # Lá 3
    
    # Adiciona um pouco de ruído para fazer soar mais áspero
    noise = generate_noise(0.3, volume=0.1)
    
    # Combina o tom com o ruído
    sound = tone * 0.7 + noise * 0.3
    
    # Aplica um envelope com ataque rápido e decaimento
    sound = apply_envelope(sound, attack=0.01, decay=0.2, sustain=0.0, release=0.1)
    
    return sound

def generate_explosion_sound():
    """Gera um som de explosão."""
    # Gera ruído branco
    noise = generate_noise(0.8, volume=0.7)
    
    # Aplica um filtro passa-baixa para soar mais como uma explosão
    b, a = signal.butter(4, 500/(44100/2), 'low')
    filtered_noise = signal.filtfilt(b, a, noise)
    
    # Aplica um envelope com ataque muito rápido e decaimento longo
    sound = apply_envelope(filtered_noise, attack=0.01, decay=0.3, sustain=0.1, release=0.4)
    
    return sound

def generate_level_up_sound():
    """Gera um som de subida de nível."""
    # Uma sequência ascendente de tons
    notes = [523.25, 587.33, 659.25, 698.46, 783.99, 880.00, 987.77, 1046.50]  # C5 até C6
    sound = np.array([])
    
    for i, freq in enumerate(notes):
        # Cada nota fica mais curta e mais suave
        duration = 0.08 * (1 - i * 0.05)
        volume = 0.3 * (1 - i * 0.05)
        note = generate_tone(freq, duration, volume=volume)
        sound = np.concatenate([sound, note])
    
    # Adiciona um final brilhante
    final_note = generate_tone(1318.51, 0.2, volume=0.4)  # Mi 6
    sound = np.concatenate([sound, final_note])
    
    # Aplica um envelope suave
    sound = apply_envelope(sound, attack=0.01, decay=0.3, sustain=0.5, release=0.2)
    
    return sound

def save_sound(sound, filename, sample_rate=44100):
    """Salva o som em um arquivo WAV."""
    # Normaliza para evitar clipping
    sound = sound / np.max(np.abs(sound)) * 0.9  # 0.9 para evitar distorção
    
    # Converte para o formato de 16 bits
    sound = (sound * 32767).astype(np.int16)
    
    # Cria o diretório se não existir
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    # Salva o arquivo WAV
    wavfile.write(filename, sample_rate, sound)
    print(f"Arquivo salvo: {filename}")

def main():
    # Cria a pasta de sons se não existir
    sounds_dir = os.path.join('assets', 'sounds')
    pew_dir = os.path.join(sounds_dir, 'pew')
    os.makedirs(pew_dir, exist_ok=True)
    
    # Gera e salva os sons
    print("Gerando sons para o jogo...")
    
    # Som de coleta
    collect_sound = generate_collect_sound()
    save_sound(collect_sound, os.path.join(pew_dir, 'collect.wav'))
    
    # Som de dano
    damage_sound = generate_damage_sound()
    save_sound(damage_sound, os.path.join(pew_dir, 'damage.wav'))
    
    # Som de explosão
    explosion_sound = generate_explosion_sound()
    save_sound(explosion_sound, os.path.join(pew_dir, 'explosion.wav'))
    
    # Som de level up
    level_up_sound = generate_level_up_sound()
    save_sound(level_up_sound, os.path.join(sounds_dir, 'level_up.wav'))
    
    print("\nTodos os sons foram gerados com sucesso!")

if __name__ == "__main__":
    main()
