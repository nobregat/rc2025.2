import matplotlib.pyplot as plt
import soundfile as sf
import sounddevice as sd

from scipy.signal import spectrogram
import numpy as np

import sys
from pathlib import Path

# Obtém o diretório raiz (modulacao)
root = Path(__file__).resolve().parents[1]
sys.path.append(str(root))

from encoders import *
from decoders import *
from ruido import *
from utils import *

output_device = 4
input_device = 1
sd.default.device = (input_device, output_device)


def plot_grafico(x, y):
    plt.figure()              
    plt.plot(x, y)            
    plt.xlabel("SNR (db)")      
    plt.ylabel("Quantidade de bits errados")      
    plt.title("Quantidade de bits errados por SNR")
    plt.grid(True)            
    plt.show()        

def plot_multiple_signals(signals, num_bits, titles=None):
    """
    signals: lista de arrays de áudio
    num_bits: quantidade de bits (para marcar divisões)
    titles: lista opcional de títulos
    """

    num_signals = len(signals)

    fig, axs = plt.subplots(num_signals, 1, figsize=(12, 3.5 * num_signals), sharex=True)

    if num_signals == 1:
        axs = [axs]

    for i, signal in enumerate(signals):
        time_axis = np.linspace(0, len(signal) / SAMPLE_RATE, len(signal))

        axs[i].plot(time_axis, signal, color="black")

        if titles and i < len(titles):
            axs[i].set_title(titles[i])
        else:
            axs[i].set_title(f"Sinal {i+1}")

        axs[i].set_ylabel("Amplitude")
        axs[i].grid(True, alpha=0.3)

        for b in range(1, num_bits):
            axs[i].axvline(x=b * BIT_DURATION, color='red', linestyle='--', alpha=0.5)

    axs[-1].set_xlabel("Tempo (s)")

    plt.tight_layout()
    plt.show()

def plot_multiple_signals_frequency(signals, num_bits, titles=None):
    """
    signals: lista de arrays de áudio
    num_bits: quantidade de bits (para marcar as divisões no tempo)
    titles: lista de títulos (opcional)
    """

    num_signals = len(signals)

    fig, axs = plt.subplots(num_signals, 1, figsize=(12, 4 * num_signals), sharex=True)

    if num_signals == 1:
        axs = [axs]

    for i, signal in enumerate(signals):
        # ---- Cálculo do espectrograma ----
        f, t, Sxx = spectrogram(signal, fs=SAMPLE_RATE, nperseg=512)
        # ---- Plot ----
        im = axs[i].pcolormesh(t, f, 10 * np.log10(Sxx + 1e-10),
                               shading='gouraud')
        # Título
        if titles and i < len(titles):
            axs[i].set_title(titles[i])
        else:
            axs[i].set_title(f"Sinal {i+1}")

        axs[i].set_ylabel("Frequência (Hz)")

        # 🔥 Limitar escala de frequências até 1000 Hz
        axs[i].set_ylim(0, 1000)

        # Marcas de bit
        for b in range(1, num_bits):
            axs[i].axvline(x=b * BIT_DURATION, color='red', linestyle='--', alpha=0.8)

        fig.colorbar(im, ax=axs[i], label="Intensidade (dB)")

    axs[-1].set_xlabel("Tempo (s)")
    plt.tight_layout()
    plt.show()
   

MATRICULA = '123110479'
FILENAME = root / 'dados_codificados' / f'dados_{MATRICULA}_44100hz.wav'
BITS_LENGTH = 22
audio, _ = sf.read(FILENAME)
decoded_nrz = decode_nrz(audio, BITS_LENGTH)

RUIDO = -2
noisy_signal_example = adicionar_ruido(audio, RUIDO)
noisy_msg_example = decode_nrz(noisy_signal_example, BITS_LENGTH)

# grafico amplitude x tempo
# plot_multiple_signals([audio, noisy_signal_example], BITS_LENGTH, ['sinal limpo', F'sinal com ruido de {RUIDO}'])
# grafico frequencia x tempo
# plot_multiple_signals_frequency([audio, noisy_signal_example], BITS_LENGTH, ['sinal limpo', F'sinal com ruido de {RUIDO}'])

# print('ESCUTANDO SOM ORIGINAL')
# sd.play(audio, SAMPLE_RATE)
# sd.wait()

# print(F'ESCUTANDO SOM COM RUIDO DE {RUIDO}')
# sd.play(noisy_signal_example, SAMPLE_RATE)
# sd.wait()


snrs = list(range(0, -100, -1)) # niveis de ruidos
x = []
y = []
for snr in snrs:
    N = 10 # quantidade de testes
    cnt = 0
    errors = []
    for t in range(N):
        clean_signal = audio
        original_msg = decoded_nrz

        noisy_signal = adicionar_ruido(clean_signal, snr)
        noisy_msg = decode_nrz(noisy_signal, BITS_LENGTH)

        if(original_msg != noisy_msg):
            # print(f"  Teste: {t}")
            # print(f"  {"Original:":25} {original_msg}")
            # print(f"  {f'Com ruido de {snr} db:':25} {noisy_msg}")
            cnt+=1

        errors.append(len([i for i in range(BITS_LENGTH) if(original_msg[i] != noisy_msg[i])]))

    errors_bit = sum(errors)/len(errors)
    print(f'snr = {snr}db, de {N} testes, {cnt} falharam tendo proporção de {cnt/N:.2f}, e media de {errors_bit:.1f} bits errados')
    x.append(-snr)
    y.append(errors_bit)

plot_grafico(x,y)

# plot_multiple_signals([adicionar_ruido(clean_signal, snr) for snr in snrs], BITS_LENGTH, [f'noisy with {snr}db' for snr in snrs])
