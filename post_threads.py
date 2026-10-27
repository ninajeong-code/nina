import os
import time
import json
import requests
from google import genai
from google.genai import types

THREADS_USER_ID = os.environ.get("THREADS_USER_ID")
ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BASE_URL = "https://graph.threads.net/v1.0"

def generate_thread_contents():
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = """
당신은 스레드(Threads)에서 바이럴되는 20대 타깃 넋두리 썰을 작성하는 마케터입니다.
상대방을 짝사랑하며 혼자 속앓이하다가 사주를 통해 상대의 음습한 집착 속마음을 알고 통쾌해하는 4편 연속 타래(Thread)를 작성하세요.

[필수 설정 및 톤앤매너]
- 소재: 학원, 동아리, 회사 사수, 스터디, 운동 모임 등 일상적인 상황 중 무작위 1개 선정.
- 스토리 구조: 
  1편: 남들 앞이나 공적인 자리에선 철벽 치고 차갑게 굴던 상대방. 내가 다른 이성과 웃는 모습을 본 뒤 표정 굳고 싸늘해진 태도.
  2편: 밤에 인스타 부계 스토리를 올리자마자 1빠로 읽고 질투 섞인 갠톡을 보냈다가 빛의 속도로 삭튀하는 음습한 행동.
  3편: '월영도령'으로 걔 속마음을 까봤더니, 자존심 때문에 겉으로만 선 긋고 뒤에선 나한테 미쳐서 혼자 집착에 피말라하던 명식(홍염사주)이었음.
  4편: 걔의 진짜 밑바닥을 알고 나서 자책을 멈추고 주도권을 잡음. 너네도 혼자 앓지 말고 속마음 까보라는 조언.
- 첫 댓글용 CTA: 지 혼자 쿨한 척하며 피말리게 하는 걔 속마음 까보라는 내용 + 링크 (https://foxbunny.io/r/UH0F2SRP).
- 말투: 현실적인 20대 여성의 독백체 (~했음, ~하더라, ㅋㅋㅋ 사용, 리얼하고 생생한 묘사).
- 각 편당 분량: 공백 포함 250~300자 내외.

[출력 형식]
반드시 부가 설명 없이 유효한 JSON 배열 포맷으로만 응답하세요:
[
  "1편 내용",
  "2편 내용",
  "3편 내용",
  "4편 내용",
  "첫 댓글 CTA 내용"
]
"""
    # 503 서버 과부하 발생 시 최대 5회 자동 재시도
    max_retries = 5
    delay = 10
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model='gemini-3.8-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"[{attempt + 1}/{max_retries}] 구글 AI 서버 혼잡 (503 등): {e}")
            if attempt < max_retries - 1:
                print(f"{delay}초 대기 후 자동으로 재시도합니다...")
                time.sleep(delay)
                delay += 10
            else:
                raise e

def create_container(text, reply_to_id=None):
    url = f"{BASE_URL}/{THREADS_USER_ID}/threads"
    payload = {
        "media_type": "TEXT",
        "text": text,
        "access_token": ACCESS_TOKEN
    }
    if reply_to_id:
        payload["reply_to_id"] = reply_to_id
        
    res = requests.post(url, data=payload)
    res.raise_for_status()
    return res.json().get("id")

def publish_container(creation_id):
    url = f"{BASE_URL}/{THREADS_USER_ID}/threads_publish"
    payload = {
        "creation_id": creation_id,
        "access_token": ACCESS_TOKEN
    }
    res = requests.post(url, data=payload)
    res.raise_for_status()
    return res.json().get("id")

def main():
    print("1. AI 원고 자동 생성 시작...")
    posts = generate_thread_contents()
    print(f"타래 생성 완료 (총 {len(posts)}개 항목)")

    previous_post_id = None
    for idx, text in enumerate(posts):
        step_name = f"{idx + 1}편 타래" if idx < len(posts) - 1 else "첫 댓글(CTA)"
        print(f"[{step_name}] 컨테이너 생성 중...")
        
        container_id = create_container(text, reply_to_id=previous_post_id)
        time.sleep(3)
        
        print(f"[{step_name}] 발행 중...")
        published_id = publish_container(container_id)
        print(f"[{step_name}] 발행 완료 (ID: {published_id})")
        
        previous_post_id = published_id
        time.sleep(3)

if __name__ == "__main__":
    main()
