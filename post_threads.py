import os
import time
import json
import random
import requests
from google import genai
from google.genai import types

THREADS_USER_ID = os.environ.get("THREADS_USER_ID")
ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BASE_URL = "https://graph.threads.net/v1.0"

def get_marketing_prompt():
    personas = [
        "사내에서 와이프 바보 사랑꾼으로 소문난 유부남 팀장",
        "다음 달 청첩장 돌린다던 7년 지기 예비신랑 남사친",
        "점잖고 가정적인 척 완벽하게 연기하는 거래처 유부남 대표",
        "여친이랑 5주년 기념일 챙기면서 나한테만 선 넘는 직장 사수",
        "결혼 전날 새벽에 술 취해서 우리 집 앞 찾아온 전남친"
    ]
    spaces = [
        "야근 후 아무도 없는 텅 빈 사무실과 탕비실",
        "회식 끝나고 대리기사 기다리는 어두운 차 안",
        "비 오는 날 우산 하나 같이 쓰고 걷는 골목길",
        "출장 가서 각자 방 잡았는데 새벽 1시에 노크하는 호텔 복도",
        "공적인 업무 지시인 척 날아오는 사내 메신저와 인스타 부계 디엠"
    ]
    triggers = [
        "목덜미 빤히 보면서 '넌 왜 이렇게 사람을 미치게 만드냐'고 낮게 읊조림",
        "슬쩍 뒤로 와서 손끝 스치더니 '오늘 입은 옷 진짜 위험하다'고 귓속말함",
        "손목 꽉 잡으면서 '나 이 결혼 안 하면 안 되냐, 너 다른 남자 만나는 거 못 보겠다'고 숨 몰아쉼",
        "남들 앞에선 칼같이 선 긋다가 둘만 남으면 '너 때문에 미쳐버릴 것 같다'며 경계 무너뜨림"
    ]

    picked_persona = random.choice(personas)
    picked_space = random.choice(spaces)
    picked_trigger = random.choice(triggers)

    prompt = f"""
당신은 스레드(Threads) 계정 '@ninano.saju(니나노사주💛연애 멘헤라 대나무숲)'의 바이럴 콘텐츠 생성기입니다.
조회수 2,300회 이상 터졌던 '유부남 팀장 이중생활 썰'의 문체와 텐션을 그대로 재현해, 금지된 사랑의 도파민 실화 4편 연속 타래(Thread)를 작성하세요.

[오늘의 랜덤 조합 변수]
- 상대 인물: {picked_persona}
- 은밀한 공간: {picked_space}
- 경계 침범 행동/대사: {picked_trigger}

[작성 규칙]
1. 1편(메인 글): 사주, 운세, 광고 뉘앙스를 0%로 완전히 배제할 것. 겉으로는 완벽하고 반듯한 척하는 상대의 이중생활과 심장 철렁했던 대사를 리얼한 1인칭 구어체(~함, ~임, 이 지랄함, 개소름 돋음 등)로 묘사할 것. (공백 포함 280~330자)
2. 2편(첫 번째 답글): 화자의 멘헤라적 내적 갈등. '선 넘으면 끝장인 거 아는데 자꾸 흔들려서 밤마다 잠도 안 온다. 이 사람이 진짜 리스크 감수할 진심인지 나를 두 번째 자리에 두려는 건지 미치겠다'는 심리 묘사 + 댓글 논쟁 유도 질문 1줄 포함. (250~300자)
3. 3편(두 번째 답글): '혼자 희망회로 돌리다 미칠 것 같아서 허락받지 못한 사랑 전용으로 봐주는 월영도령 사주로 상대 속마음이랑 내가 평생 세컨드에 갇힐 운명인지 17개 섹션 뜯어보고 정신 번쩍 들었다'는 팩폭 후기. (250~300자)
4. 4편(마지막 답글 + CTA): '비밀연애나 위험한 관계 때문에 밤새 잠 못 자는 멘헤라들은 혼자 앓지 말고 상대 진심부터 팩트로 확인해라'는 조언과 함께 아래 링크를 정확히 포함할 것.
   링크: https://foxbunny.io/r/UH0F2SRP

[출력 형식]
반드시 부가 설명 없이 유효한 JSON 배열 포맷으로만 응답하세요:
[
  "1편 내용",
  "2편 내용",
  "3편 내용",
  "4편 내용"
]
"""
    return prompt

def generate_thread_contents():
    client = genai.Client(api_key=GEMINI_API_KEY)
    prompt = get_marketing_prompt()
    
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
        step_name = f"{idx + 1}편 타래" if idx < len(posts) - 1 else "마지막 타래(CTA)"
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
