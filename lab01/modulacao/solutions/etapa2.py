import soundfile as sf
import numpy as np

SAMPLE_RATE = 44100  # Hz
BIT_DURATION = 1.0   # 1 segundo por bit
FREQ_LOW = 440       # Frequência para '0' (Lá)
FREQ_HIGH = 880      # Frequência para '1' (Lá oitava)
DURATION = 0

def show(data:str,debug):
    if debug==True:
        print(data)

def detect_frequency(audio_segment, sample_rate=SAMPLE_RATE):
    """
    Detecta a frequência dominante em um segmento de áudio

    Args:
        audio_segment: Segmento de áudio
        sample_rate: Taxa de amostragem

    Returns:
        float: Frequência detectada
    """
    # FFT para análise espectral
    fft = np.fft.fft(audio_segment)
    freqs = np.fft.fftfreq(len(fft), 1/sample_rate)

    # Considera apenas frequências positivas
    magnitude = np.abs(fft[:len(fft)//2])
    freqs_positive = freqs[:len(freqs)//2]

    # Encontra o pico de frequência
    peak_idx = np.argmax(magnitude)
    detected_freq = abs(freqs_positive[peak_idx])

    return detected_freq

def frequency_to_bit(frequency, threshold=660):
    """
    Converte frequência detectada em bit

    Args:
        frequency: Frequência detectada
        threshold: Limiar para decisão (média entre FREQ_LOW e FREQ_HIGH)

    Returns:
        str: '0' ou '1'
    """
    return '1' if frequency > threshold else '0'

def decode_nrz(audio_signal, num_bits, sample_rate=SAMPLE_RATE,debug=False):
    """
    Decodifica sinal NRZ

    Args:
        audio_signal: Sinal de áudio
        num_bits: Número esperado de bits
        sample_rate: Taxa de amostragem

    Returns:
        str: Bits decodificados
    """
    samples_per_bit = int(sample_rate * BIT_DURATION)
    decoded_bits = ""

    show("Decodificando NRZ:",debug)

    for i in range(num_bits):
        start_idx = i * samples_per_bit
        end_idx = start_idx + samples_per_bit

        if end_idx > len(audio_signal):
            show(f"Aviso: Áudio muito curto para {num_bits} bits",debug)
            break

        # Analisa o meio do bit para evitar transições
        mid_start = start_idx + samples_per_bit // 4
        mid_end = end_idx - samples_per_bit // 4
        segment = audio_signal[mid_start:mid_end]

        freq = detect_frequency(segment, sample_rate)
        bit = frequency_to_bit(freq)
        decoded_bits += bit

        show(f"Bit {i}: freq={freq:.1f}Hz -> '{bit}'",debug)

    return decoded_bits

def decode_manchester(audio_signal, num_bits, sample_rate=SAMPLE_RATE,debug=False):
    """
    Decodifica sinal Manchester
    """
    samples_per_bit = int(sample_rate * BIT_DURATION)
    decoded_bits = ""

    show("Decodificando Manchester:",debug)

    for i in range(num_bits):
        start_idx = i * samples_per_bit
        end_idx = start_idx + samples_per_bit

        if end_idx > len(audio_signal):
            break

        # Analisa primeira e segunda metade do bit
        mid_point = start_idx + samples_per_bit // 2

        # Primeira metade
        first_half = audio_signal[start_idx + samples_per_bit//8 : mid_point - samples_per_bit//8]
        freq1 = detect_frequency(first_half, sample_rate)
        state1 = frequency_to_bit(freq1)

        # Segunda metade
        second_half = audio_signal[mid_point + samples_per_bit//8 : end_idx - samples_per_bit//8]
        freq2 = detect_frequency(second_half, sample_rate)
        state2 = frequency_to_bit(freq2)

        # Determina o bit baseado na transição
        if state1 == '1' and state2 == '0': # Alto -> Baixo
            bit = '1'
            show(f"Bit {i}: {freq1:.1f}Hz -> {freq2:.1f}Hz = alto->baixo = '1'",debug)
        elif state1 == '0' and state2 == '1': # Baixo -> Alto
            bit = '0'
            show(f"Bit {i}: {freq1:.1f}Hz -> {freq2:.1f}Hz = baixo->alto = '0'",debug)
        else: # Erro de decodificação
            bit = '?'
            show(f"Bit {i}: {freq1:.1f}Hz -> {freq2:.1f}Hz = ERRO na transição",debug)

        decoded_bits += bit

    return decoded_bits


if __name__ == '__main__':
    matricula = input("Insira sua matrícula: ")
    DURATION = int(input("Insira a duração do áudio em segundos: "))
    
    path = "audios/dados_" + matricula + "_44100hz.wav"
    print("\n1. Decodificando NRZ:")
    nrz_audio, _ = sf.read(path)
    decoded_nrz = decode_nrz(nrz_audio, DURATION)
    
    print(f"Decodificado: {decoded_nrz}")
    print(f"Número de bits é: {len(decoded_nrz)}")
    
    print("\n3. Decodificando Manchester:")
    manchester_audio, _ = sf.read(path)
    decoded_manchester = decode_manchester(manchester_audio, DURATION)
    print(f"Decodificado: {decoded_manchester}")
    print(f"Número de bits é: {len(decoded_manchester)}")

