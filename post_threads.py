import os
import time
import json
import requests
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types

THREADS_USER_ID = os.environ.get("THREADS_USER_ID")
ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BASE_URL = "https://graph.threads.net/v1.0"

def get_marketing_prompt():
    # 한국 시간(KST = UTC+9) 기준 요일 계산 (0: 월요일, 1: 화요일, ..., 6: 일요일)
    kst = timezone(timedelta(hours=9))
    current_weekday = datetime.now(kst).weekday()

    if current_weekday == 0:
        # [월요일 전용] 전체 인생/신점 사주 타깃
        print("[오늘의 모드] 월요일 특화: 전체 인생 신점/사주 총운")
        prompt = """
당신은 스레드(Threads)에서 바이럴되는 2030 타깃 넋두리 썰을 작성하는 마케터입니다.
하는 일마다 안 풀리고 내 인생만 뒤처지는 것 같아 극도로 불안해하다가, 용한 신점/사주로 내 인생 전체 대운 흐름을 확인하고 불안을 털어낸 4편 연속 타래(Thread)를 작성하세요.

[필수 설정 및 톤앤매너]
- 소재: 취업 준비, 잦은 이직 고민, 퇴사 후 공백기, 번아웃, 모아둔 돈 없는 현실 등 2030이 겪는 인생 정체기 상황 중 무작위 1개 선정.
- 스토리 구조:
  1편: 동기들이나 주변 사람들은 다 자리 잡고 잘 사는데, 나만 하는 일마다 꼬이고 뒤처지는 것 같아 바닥을 치던 현실.
  2편: 밤마다 남들과 비교하며 자책하고, "내 인생은 도대체 언제 풀리나" 불안해서 가슴 답답해 잠 못 들던 심정.
  3편: 답답한 마음에 신점 사주로 내 전체 인생 흐름(초년운, 대운, 앞으로 터질 재물운)을 봤더니, 지금이 대운 바뀌기 직전 액땜하는 교운기 구간이라고 소름 돋게 짚어냄.
  4편: 내 사주 원국과 앞으로 풀릴 인생 판을 다 확인하고 나니 남 눈치 볼 필요 없이 마음이 싹 정리됨. 막막하다고 혼자 자책하지 말고 인생 전체 흐름부터 까보라는 조언.
- 첫 댓글용 CTA: 내 인생 도대체 언제 풀리는지 전체 사주/신점 흐름 1초 만에 확인하라는 내용 + 링크 (https://foxbunny.io/r/0222G0HV).
- 말투: 현실적인 20대~30대의 솔직한 독백체 (~했음, ~하더라, ㅋㅋㅋ 사용, 리얼하고 생생한 묘사).
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
    else:
        # [화~일요일] 기본 짝사랑 홍염사주 타깃
        print("[오늘의 모드] 평일/주말 기본: 짝사랑 홍염사주")
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
    return prompt

def generate_thread_contents():
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = get_marketing_prompt()
    
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
