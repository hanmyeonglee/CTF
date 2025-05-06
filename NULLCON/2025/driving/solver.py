import cv2
import os

# 비디오 파일 경로
video_path = "./driving/driving.mp4"

# 비디오 파일 열기
cap = cv2.VideoCapture(video_path)

frame_count = 0
while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break  # 영상이 끝나면 종료

    # 원본 프레임 크기 가져오기
    height, width = frame.shape[:2]

    # 2배 확대 (INTER_CUBIC 보간법 사용)
    enlarged_frame = cv2.resize(frame, (width * 2, height * 2), interpolation=cv2.INTER_CUBIC)

    # 프레임 저장 (0001.jpg, 0002.jpg, ...)
    frame_filename = f'./driving/capture/{frame_count:03d}.jpg'
    cv2.imwrite(frame_filename, enlarged_frame)
    frame_count += 1

# 자원 해제
cap.release()
print(f"총 {frame_count}개의 확대된 프레임이 저장되었습니다.")
