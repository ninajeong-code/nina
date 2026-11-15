import os
import time
import json
import random
import requests
from datetime import datetime, timezone, timedelta
from google import genai
from google.genai import types

THREADS_USER_ID = os.environ.get("THREADS_USER_ID")
ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
BASE_URL = "https://graph.threads.net/v1.0"


def select_mode():
    # 수동 테스트 시 특정 모드 강제 지정 가능 (기본값: auto)
    manual_mode = os.environ.get("POST_MODE", "auto").strip().lower()
    if manual_mode in ["wolyeong", "gwiyeon", "cheongyeon"]:
        return manual_mode

    # 한국 시간(KST = UTC+9) 기준 시간 및 연속 일수 계산
    kst = timezone(timedelta(hours=9))
    now_kst = datetime.now(kst)

    # 오후 6시(18시) 이후 밤 시간대 -> 매일 월영도령
    if now_kst.hour >= 18:
        return "wolyeong"

    # 낮 시간대 -> 연속 일수(toordinal) 기준 정확한 격일 교차 (귀연도령 <-> 청연도령)
    if now_kst.date().toordinal() % 2 == 0:
        return "gwiyeon"
    else:
        return "cheongyeon"


def get_marketing_prompt():
    mode = select_mode()

    if mode == "wolyeong":
        print("[발행 모드] 매일 밤 메인: 월영도령 허락받지 못한 사랑 사주")
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
            "슬쩍 뒤로 와서 손끝 스치더니 '오늘 입은 셔츠 진짜 위험하다'고 귓속말함",
            "손목 꽉 잡으면서 '나 이 결혼 안 하면 안 되냐, 너 다른 남자 만나는 거 못 보겠다'고 숨 몰아쉼",
            "남들 앞에선 칼같이 선 긋다가 둘만 남으면 '너 때문에 미쳐버릴 것 같다'며 경계 무너뜨림"
        ]

        p_persona = random.choice(personas)
        p_space = random.choice(spaces)
        p_trigger = random.choice(triggers)

        return f"""
당신은 스레드(Threads) 계정 '@ninano.saju(니나노사주💛연애 멘헤라 대나무숲)'의 바이럴 콘텐츠 생성기입니다.
조회수 2,300회 이상 터졌던 '유부남 팀장 이중생활 썰'의 문체와 텐션을 그대로 재현해, 금지된 사랑의 도파민 실화 4편 연속 타래(Thread)를 작성하세요.

[오늘의 랜덤 조합 변수]
- 상대 인물: {p_persona}
- 은밀한 공간: {p_space}
- 경계 침범 행동/대사: {p_trigger}

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

    elif mode == "gwiyeon":
        print("[발행 모드] 낮 격일 A: 귀연도령 재회운 사주")
        situations = [
            "다시는 안 볼 것처럼 차갑게 환승 이별 통보하고 차단했던 전남친",
            "권태기라며 핑계 대고 잠수 이별 타더니 3개월 만에 새벽 3시 부계 스토리 1초 컷으로 염탐하는 전애인",
            "서로 좋아하는데 현실 문제로 눈물 콧물 짜며 합의 이별했던 구남친",
            "헤어질 때 모진 말 다 쏟아붓고 정리했다더니 술 취해서 '자니?' 부재중 3통 남긴 전남친"
        ]
        triggers = [
            "내가 다른 남자랑 웃는 사진 올리자마자 차단 풀고 '잘 지내냐'고 디엠 보냈다가 삭튀함",
            "전애인 친한 친구한테 내 근황 미친 듯이 캐묻고 다닌다는 소식 들림",
            "프사 배경음악을 우리가 사귈 때 맨날 듣던 노래로 바꿔놓고 상태메시지에 의미심장한 글 적어둠",
            "우연히 마주쳤는데 눈 마주치자마자 얼굴 하얗게 질려서 말도 못 잇고 내 손목 붙잡으려다 멈칫함"
        ]

        p_sit = random.choice(situations)
        p_trig = random.choice(triggers)

        return f"""
당신은 스레드(Threads) 계정 '@ninano.saju(니나노사주💛연애 멘헤라 대나무숲)'의 바이럴 콘텐츠 생성기입니다.
이별 후 후폭풍과 미련 때문에 밤잠 설치는 2030 타깃의 도파민 재회 썰 4편 연속 타래(Thread)를 작성하세요.

[오늘의 랜덤 조합 변수]
- 상황 설정: {p_sit}
- 후폭풍 정황: {p_trig}

[작성 규칙]
1. 1편(메인 글): 사주, 운세, 광고 뉘앙스를 0%로 완전히 배제할 것. 냉정하게 돌아섰던 전애인의 찌질한 후폭풍 정황과 심장 철렁했던 순간을 리얼한 1인칭 구어체(~함, ~임, 개소름 돋음, 어이없음 등)로 생생하게 묘사할 것. (공백 포함 280~330자)
2. 2편(첫 번째 답글): 화자의 흔들리는 속마음. '다 끝난 거 아는데 그 행동 하나 때문에 또 밤새 잠 못 자고 의미 부여하게 된다. 진짜 후회해서 돌아오려는 건지 외로워서 찔러보는 건지 미치겠다'는 심리 묘사 + 댓글 논쟁 유도 질문 1줄 포함. (250~300자)
3. 3편(두 번째 답글): '혼자 카톡창만 들여다보다 미칠 것 같아서 재회 전문 귀연도령 재회운 사주로 걔 속마음이랑 실제 재회 타이밍, 다시 만나도 똑같이 깨질 운명인지 뜯어보고 정신 번쩍 들었다'는 팩폭 후기. (250~300자)
4. 4편(마지막 답글 + CTA): '전애인 행동 하나에 희망회로 돌리며 밤새우는 멘헤라들은 혼자 앓지 말고 재회 가능성부터 팩트로 확인해라'는 조언과 함께 아래 링크를 정확히 포함할 것.
   링크: https://foxbunny.io/r/MKG4O4GJ

[출력 형식]
반드시 부가 설명 없이 유효한 JSON 배열 포맷으로만 응답하세요:
[
  "1편 내용",
  "2편 내용",
  "3편 내용",
  "4편 내용"
]
"""

    else:
        print("[발행 모드] 낮 격일 B: 청연도령 퀴어 연애 궁합 사주")
        situations = [
            "남들 앞에선 그냥 제일 친한 동성 친구(언니)인 척 선 긋는데 둘만 있으면 텐션 미쳐버리는 썸녀",
            "주변 시선 때문에 우리 사이 절대 티 못 내고 비밀로 만나는 동성 연인",
            "이성애자인 줄만 알았던 친한 동기가 술만 마시면 내 방에 자고 가겠다고 떼쓰며 경계 허무는 상황",
            "회사에서 완벽한 선후배 사이로 지내면서 퇴근 후 단둘이 있을 때만 은밀하게 손 깍지 끼는 언니"
        ]
        triggers = [
            "새벽에 내 침대에 같이 누워서 내 머리카락 쓸어넘기며 '너 다른 사람 만나는 거 상상만 해도 미칠 것 같다'고 속삭임",
            "다른 사람하고 조금만 친하게 지내도 표정 싸늘하게 굳더니 밤에 '너는 내 거잖아'라고 갠톡 보냄",
            "남들 눈 피해서 비상계단이나 차 안에서 내 손목 꽉 잡고 '우리 그냥 아무도 모르는 데로 도망갈까'라고 낮게 말함",
            "술 취해서 내 목덜미에 얼굴 묻고 '친구라는 말 지겨워 죽겠다, 나한테만 다정하면 안 되냐'고 중얼거림"
        ]

        p_sit = random.choice(situations)
        p_trig = random.choice(triggers)

        return f"""
당신은 스레드(Threads) 계정 '@ninano.saju(니나노사주💛연애 멘헤라 대나무숲)'의 바이럴 콘텐츠 생성기입니다.
말 못 할 동성 썸·퀴어 연애의 아슬아슬한 텐션과 불안을 다룬 4편 연속 타래(Thread)를 작성하세요.

[오늘의 랜덤 조합 변수]
- 관계 설정: {p_sit}
- 심장 철렁한 순간: {p_trig}

[작성 규칙]
1. 1편(메인 글): 사주, 운세, 광고 뉘앙스를 0%로 완전히 배제할 것. 주변에 들키지 않으려 조심하면서도 둘만 남으면 숨 막히게 선을 넘는 동성 상대와의 도파민 실화를 리얼한 1인칭 구어체(~함, ~임, 심장 터질 뻔함 등)로 몰입감 있게 묘사할 것. (공백 포함 280~330자)
2. 2편(첫 번째 답글): 화자의 불안과 고민. '친구인지 연인인지 정의도 못 내리고 주변에 말할 곳도 없어서 밤마다 혼자 끙끙 앓는다. 이 사람도 나랑 같은 마음인지 나만 진심인 건지 미치겠다'는 심리 묘사 + 댓글 공감 유도 질문 1줄 포함. (250~300자)
3. 3편(두 번째 답글): '일반 사주는 성별 고정관념 때문에 안 맞아서 답답했는데, 청연도령 퀴어 연애 궁합 사주로 두 사람 인연의 깊이랑 상대방 진짜 속마음 뜯어보고 소름 돋아서 눈물 났다'는 리얼 후기. (250~300자)
4. 4편(마지막 답글 + CTA): '아무한테도 털어놓지 못할 퀴어 짝사랑·비밀 연애 때문에 밤잠 설치는 사람들은 혼자 속 태우지 말고 두 사람 궁합부터 팩트로 확인해라'는 조언과 함께 아래 링크를 정확히 포함할 것.
   링크: https://foxbunny.io/r/LBGZL0J_

[출력 형식]
반드시 부가 설명 없이 유효한 JSON 배열 포맷으로만 응답하세요:
[
  "1편 내용",
  "2편 내용",
  "3편 내용",
  "4편 내용"
]
"""


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
