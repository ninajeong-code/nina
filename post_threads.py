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
    # 한국 시간(KST = UTC+9) 기준 요일 계산 (0: 월, 1: 화, 2: 수, 3: 목, 4: 금, 5: 토, 6: 일)
    kst = timezone(timedelta(hours=9))
    current_weekday = datetime.now(kst).weekday()

    if current_weekday == 0:
        # 1. [월요일] 전체 인생/대운 신점 사주
        print("[오늘의 모드] 월요일: 전체 인생 신점 사주 (대운/인생총운)")
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
    elif current_weekday == 2:
        # 2. [수요일] 홍염사주 (짝사랑/집착 속마음)
        print("[오늘의 모드] 수요일: 홍염사주 (짝사랑/속마음)")
        prompt = """
당신은 스레드(Threads)에서 바이럴되는 20대 타깃 넋두리 썰을 작성하는 마케터입니다.
상대방을 짝사랑하며 혼자 속앓이하다가 사주를 통해 상대의 음습한 집착 속마음을 알고 통쾌해하는 4편 연속 타래(Thread)를 작성하세요.

[필수 설정 및 톤앤매너]
- 소재: 학원, 동아리, 회사 사수, 스터디, 운동 모임 등 일상적인 상황 중 무작위 1개 선정.
- 스토리 구조: 
  1편: 남들 앞이나 공적인 자리에선 철벽 치고 차갑게 굴던 상대방. 내가 다른 이성과 웃는 모습을 본 뒤 표정 굳고 싸늘해진 태도.
  2편: 밤에 인스타 부계 스토리를 올리자마자 1빠로 읽고 질투 섞인 갠톡을 보냈다가 빛의 속도로 삭튀하는 음습한 행동.
  3편: 사주로 걔 속마음을 까봤더니, 자존심 때문에 겉으로만 선 긋고 뒤에선 나한테 미쳐서 혼자 집착에 피말라하던 명식(홍염사주)이었음.
  4편: 걔의 진짜 밑바닥을 알고 나서 자책을 멈추고 주도권을 잡음. 너네도 혼자 앓지 말고 속마음 까보라는 조언.
- 첫 댓글용 CTA: 지 혼자 쿨한 척하며 피말리게 하는 걔 진짜 속마음 홍염사주로 까보라는 내용 + 링크 (https://foxbunny.io/r/QTPBQ5RA).
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
    else:
        # 3. [화·목·금·토·일] 월영도령 사주 (불륜/금기된 치정/매운맛 허락받지 못한 사주)
        print("[오늘의 모드] 화·목·금·토·일: 월영도령 사주 (불륜/허락받지 못한 사주 매운맛)")
        prompt = """
당신은 스레드(Threads)에서 폭발적인 조회수를 끄는 2030 타깃 막장·치정 매운맛 썰을 작성하는 마케터입니다.
보통 불륜이나 바람피우는 사람들이 유독 많이 본다는 '월영도령 허락받지 못한 사주'를 소재로, 도덕적으로 허락되지 않는 아슬아슬하고 은밀한 관계의 밑바닥을 폭로하는 4편 연속 타래(Thread)를 작성하세요.

[필수 설정 및 톤앤매너]
- 소재: 애인 있는 직장 상사, 유부남/유부녀 거래처, 친구의 남친, 파혼 직전의 양다리, 비밀 사내 연애 등 절대 세상에 들키면 안 되는 금기된 관계 중 1개 선정.
- 매운맛 수위: 심리적 텐션과 가스라이팅, 이중생활의 음습함이 생생하게 드러나는 극강의 현실 매운맛 썰.
- 스토리 구조:
  1편: 겉으로는 멀쩡하고 가정적/공적인 이미지 완벽하게 연기하면서, 뒤로는 나한테 미친 듯이 들이대고 이중생활하며 경계 허물던 상대방의 실체.
  2편: 들키면 파멸인 거 알면서도 새벽마다 부계로 질척거리고 호텔 방이나 인적이 드문 곳에서 사람 정신적으로 옭아매며 가스라이팅하던 위험한 정황.
  3편: 이 지옥 같은 관계를 못 끊겠어서 '월영도령'으로 걔와 나의 궁합 및 사주를 까봤더니, '평생 허락받지 못한 인연에만 목매다는 파격 사주', 불륜·환승하는 자들이 타고난다는 살(煞) 낀 명식이었음. 상대가 왜 그렇게까지 위험을 무릅쓰고 집착했는지 음습한 본능의 밑바닥이 다 나옴.
  4편: 걔의 추악한 사주 원국과 본색을 확인하고 나서 정신 번쩍 차리고 칼손절 치며 판을 엎어버림. 금기된 관계나 똥차한테 잡혀서 혼자 갉아먹히지 말고 월영도령으로 걔 속마음 밑바닥부터 까보라는 살벌한 조언.
- 첫 댓글용 CTA: 보통 불륜이나 바람피우는 애들이 환장하고 본다는 '허락받지 못한 사주'... 걔 이중생활 속마음 밑바닥 1초 만에 까볼 사람들만 월영도령 보라는 경고성 문구 + 링크 (https://foxbunny.io/r/UH0F2SRP).
- 말투: 2030 여성의 거침없고 자극적인 독백체 (~했음, ~하더라, ㅋㅋㅋ, 개소름, 쓰레기 등 실감 나는 표현 사용).
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
