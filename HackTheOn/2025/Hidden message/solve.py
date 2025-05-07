import subprocess, os
import itertools

# 분석할 파일 경로
image_file = "Hidden message.png"  # 또는 BMP 파일

# 가능한 옵션들
planes = ['b1', 'b2', 'b4', 'r1', 'r2', 'r4', 'g1', 'g2', 'g4', 'a1', 'a2', 'a4']
orders = ['lsb', 'msb']
encodings = ['ascii', 'utf-8', 'utf-16le', 'utf-16be', 'utf-32le', 'utf-32be']

# 결과 저장
results = []

for plane, order, encoding in itertools.product(planes, orders, encodings):
    cmd = f"zsteg -E {plane} {order} {encoding} "
    cmd = [
        "zsteg",
        "-E", f"{plane} {order} {encoding}",
        image_file
    ]
    os.system(' '.join(cmd))
    """ try:
        output = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        result = output.decode(errors='ignore').strip()
        if result:
            print(f"[{plane} {order} {encoding}]\n{result}\n{'-'*40}")
            results.append((plane, order, encoding, result))
    except subprocess.CalledProcessError:
        continue  # 무시하고 다음으로 """

print(f"총 발견된 결과 수: {len(results)}")
