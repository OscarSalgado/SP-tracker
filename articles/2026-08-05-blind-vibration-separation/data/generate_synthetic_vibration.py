"""Generador de datos sintéticos de vibración para validación del método.

Crea señales realistas de vibración de engranaje y rodamiento con función
de transferencia del sistema simulada.
"""

import numpy as np
from scipy import signal as sp_signal


def generate_synthetic_vibration(
    sampling_rate: int = 10000,
    duration: float = 2.0,
    freq_gear: float = 100.0,
    freq_bearing: float = 60.0,
    gear_amplitude: float = 1.0,
    bearing_amplitude: float = 0.1,
    snr_db: float = 20.0,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """Genera datos sintéticos de vibración con función de transferencia.

    Args:
        sampling_rate: Frecuencia de muestreo (Hz).
        duration: Duración de la señal (segundos).
        freq_gear: Frecuencia fundamental de engranaje (Hz).
        freq_bearing: Frecuencia de paso de bola de rodamiento (Hz).
        gear_amplitude: Amplitud de vibración de engranaje (V).
        bearing_amplitude: Amplitud de vibración de rodamiento (V).
        snr_db: Relación señal a ruido objetivo (dB).

    Returns:
        Tupla (tiempo, vibración_engranaje, vibración_rodamiento, señal_mezclada, función_transferencia)
    """
    num_samples = int(sampling_rate * duration)
    time = np.arange(num_samples) / sampling_rate

    gear_vib = gear_amplitude * np.sin(2 * np.pi * freq_gear * time)
    gear_vib += 0.3 * gear_amplitude * np.sin(2 * np.pi * 2 * freq_gear * time)
    gear_vib += 0.1 * gear_amplitude * np.sin(2 * np.pi * 3 * freq_gear * time)

    bearing_vib = bearing_amplitude * np.sin(2 * np.pi * freq_bearing * time)
    bearing_vib += 0.2 * bearing_amplitude * np.sin(2 * np.pi * (freq_bearing + freq_gear) * time)

    mixed_signal = gear_vib + bearing_vib

    sos = sp_signal.butter(2, 0.3, "low", output="sos")
    mixed_signal = sp_signal.sosfilt(sos, mixed_signal)

    signal_power = np.mean(mixed_signal**2)
    noise_power = signal_power / (10 ** (snr_db / 10))
    noise = np.sqrt(noise_power) * np.random.randn(num_samples)
    mixed_signal_noisy = mixed_signal + noise

    transfer_func_coeffs = sp_signal.butter(2, 0.3, "low")
    transfer_func = np.array(transfer_func_coeffs[0]) / np.array(transfer_func_coeffs[1])

    return time, gear_vib, bearing_vib, mixed_signal_noisy, transfer_func


def save_data(output_dir: str = ".") -> None:
    """Genera y guarda datos sintéticos en archivos .npy.

    Args:
        output_dir: Directorio donde guardar los archivos.
    """
    import os

    os.makedirs(output_dir, exist_ok=True)

    time, gear, bearing, mixed, transfer = generate_synthetic_vibration()

    np.save(os.path.join(output_dir, "time.npy"), time)
    np.save(os.path.join(output_dir, "gear_vibration.npy"), gear)
    np.save(os.path.join(output_dir, "bearing_vibration.npy"), bearing)
    np.save(os.path.join(output_dir, "mixed_signal.npy"), mixed)
    np.save(os.path.join(output_dir, "transfer_function.npy"), transfer)

    print(f"Datos sintéticos guardados en {output_dir}/")
    print(f"  - time.npy: {time.shape}")
    print(f"  - gear_vibration.npy: {gear.shape}")
    print(f"  - bearing_vibration.npy: {bearing.shape}")
    print(f"  - mixed_signal.npy: {mixed.shape}")
    print(f"  - transfer_function.npy: {transfer.shape}")


if __name__ == "__main__":
    save_data()
