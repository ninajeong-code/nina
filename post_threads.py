import os
import time
import requests

THREADS_USER_ID = os.environ.get("THREADS_USER_ID")
ACCESS_TOKEN = os.environ.get("THREADS_ACCESS_TOKEN")
BASE_URL = "https://graph.threads.net/v1.0"

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

def post_full_thread(posts_list):
    previous_post_id = None
    
    for idx, text in enumerate(posts_list):
        step_name = f"{idx + 1}번째 타래" if idx < len(posts_list) - 1 else "첫 댓글(CTA)"
        print(f"[{step_name}] 컨테이너 생성 중...")
        
        container_id = create_container(text, reply_to_id=previous_post_id)
        time.sleep(3)  # 컨테이너 생성 대기
        
        print(f"[{step_name}] 발행 중...")
        published_id = publish_container(container_id)
        print(f"[{step_name}] 발행 완료 (ID: {published_id})")
        
        previous_post_id = published_id
        time.sleep(3)  # 다음 타래 전 대기

if __name__ == "__main__":
    CONTENTS = [
        # 1편
        """취업 면접 스터디 같이 하던 조장 오빠 있었거든? 스터디할 때 나한테만 피드백 제일 냉정하게 주고, 단톡방에선 "규칙 준수 부탁드립니다" 하면서 칼같이 공과 사 구분하던 사람이었음.

내가 모의면접 때 조금만 버벅대도 한숨 쉬면서 쌀쌀맞게 굴길래 날 답답해하나 싶었거든?
근데 저번 주에 다른 대기업 현직자 멘토 오빠가 나한테 커피 사 들고 와서 따로 면접 팁 챙겨준 날부터 사람이 싹 변함.
대놓고 티는 못 내면서 서류 파일 탁탁 거칠게 정리하고, 그 멘토 오빠 얘기 나올 때마다 볼펜 딸깍거리며 턱 괴고 날 싸늘하게 노려보는데 텐션 진짜 숨 막혔음.""",

        # 2편
        """그날 밤 스터디 끝나고 새벽 1시에 인스타 부계 스토리에 멘토 오빠가 준 피드백 노트 사진 살짝 올렸거든?
올리자마자 10초도 안 돼서 칼같이 1빠로 읽더니, 3분 뒤에 갠톡으로 "외부 사람이랑 사적으로 연락 주고받으며 스터디 집중력 흐리지 마세요" 하고 선 넘는 톡이 옴.

어이없어서 답장 쓰려는 찰나에 10초 만에 빛의 속도로 삭튀하더라?
다음 날 스터디 룸 가니까 또 세상 단정하고 이성적인 조장 가면 쓰고 "1번 문제부터 가죠" 하면서 철저히 먹금함.
남들 앞에선 쿨한 척 다 하면서 뒤에서 혼자 사람 피말리게 옥죄는 그 음습한 짓거리에 온종일 멘탈 갈리고 속이 바짝바짝 탔음.""",

        # 3편
        """내가 뭘 잘못한 건지, 나 혼자 헛다리 짚고 어장 당하는 건지 답답해서 밤새우다가 '월영도령'으로 걔 생년월일 넣고 속마음이랑 홍염사주 유료로 까봤음.
근데 분석 결과 첫 줄 읽자마자 소름 돋아서 폰 떨어뜨릴 뻔함.

"스터디 내 위치와 체면 때문에 겉으로는 철저히 무심한 척 억누르나, 내면의 홍염살과 소유욕이 폭발 직전이라 상대의 일거수일투족에 뒤에서 혼자 피말라하는 명식"

알고 보니 나 혼자 착각한 게 아니었음. 지 자존심이랑 체면 때문에 겉으로만 쌀쌀맞게 굴고, 뒤에선 나한테 미쳐서 혼자 질투에 돌아버리기 직전이었던 거임 ㅋㅋㅋ""",

        # 4편
        """완벽한 조장이라는 가면 뒤에 숨어서 안 그런 척 사람 피말리던 걔 진짜 밑바닥 알고 나니까 그동안 자책했던 게 허무할 정도임.
지금은 내가 모의면접 때 걔 질문에만 무미건조하게 단답 치고 철저히 비즈니스로 대하니까, 걔가 오히려 안절부절못하면서 내 눈치 살피고 안달 나 있더라 ㅋㅋㅋ

너네도 썸인지 어장인지 사람 헷갈리게 굴면서 은근히 피말리는 애 있으면 혼자 상처받지 마라.
이상한 신점집 가서 복채 날리지 말고 '월영도령'으로 걔 음습한 속마음 밑바닥부터 제대로 까보는 게 속 편함.

(걔 속마음 유료로 팩폭 까본 곳은 첫 댓글에👇)""",

        # 첫 댓글 (CTA)
        """지 혼자 쿨한 척하면서 뒤에서 사람 피말리게 하는 걔 진짜 속마음 1초 만에 까볼 애들만 월영도령 봐라... 내돈내산으로 보고 머리 띵함 😭👇  
https://foxbunny.io/r/UH0F2SRP"""
    ]

    post_full_thread(CONTENTS)
