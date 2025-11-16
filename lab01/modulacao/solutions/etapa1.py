import os
import sounddevice as sd

from ..encoders import *
from ..decoders import * 

print(sd.query_devices()[7])

input_device = 5
output_device = 7
sd.default.device = (input_device, output_device)


SAMPLE_RATE = 44100  # Taxa de amostragem do audio
BIT_DURATION = 1.0   # 1 segundo por bit
FREQ_LOW = 440       # bit '0' (Lá)
FREQ_HIGH = 880      # bit '1' (Lá oitava)

test_bits = "0000000"
print(f"Dados originais: {test_bits}\n")
# Testa cada modulação
print("1. NRZ:")
nrz_signal = encode_nrz(test_bits,debug=True)

print("\n3. Manchester:")
manchester_signal = encode_manchester(test_bits,debug=True)


sd.play(manchester_signal, SAMPLE_RATE)
sd.wait()
sd.play(nrz_signal, SAMPLE_RATE)
sd.wait()

plot_signal(nrz_signal,'NRZ',len(test_bits))


# Quantos tons diferentes vocês conseguem distinguir? 2
# É possível identificar qual tom representa 0 e qual representa 1? Sim
# O que acontece quando há muitos bits iguais consecutivos? É gerado uma sequência de sons iguais, mas ainda é possível distinguir os tons

