import numpy as np
import matplotlib.pyplot as plt

# IQ 파일 경로
file_path = "dotdotdot.iq"

# 데이터 형식 (예: int16)
dtype = np.int16

# 데이터 읽기
with open(file_path, "rb") as f:
    raw_data = np.fromfile(f, dtype=dtype)

# I와 Q 데이터 분리 (인터리브된 경우)
I = raw_data[0::2]  # 짝수 인덱스
Q = raw_data[1::2]  # 홀수 인덱스

# 복소수 형태로 변환
iq_data = I + 1j * Q

# 시간 영역에서 신호 시각화
plt.figure()
plt.plot(I, label="I (In-phase)")
plt.plot(Q, label="Q (Quadrature)")
plt.title("Time-domain Signal")
plt.legend()
plt.show()

# 주파수 영역 분석 (FFT)
fft_data = np.fft.fftshift(np.fft.fft(iq_data))
freq = np.fft.fftshift(np.fft.fftfreq(len(iq_data)))

plt.figure()
plt.plot(freq, np.abs(fft_data))
plt.title("Frequency-domain Signal")
plt.xlabel("Frequency")
plt.ylabel("Magnitude")
plt.show()
