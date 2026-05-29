# cs-auto-answer-plugin

이더컴퍼니 **사방넷 CS(고객문의) 자동답변** 플러그인입니다.
쿠팡·네이버 스마트스토어 고객 문의를 사방넷에서 수집하고, 안전하고 친절한 답변을 생성하여
저장·송신합니다. 자가학습 가이드라인과 CS 메모리(답변 원칙·상품 레퍼런스)를 함께 번들합니다.

## 구성
- `skills/cs-auto-answer/` — CS 수집·답변 메인 스킬 (+ `scripts/cs_answer_guidelines.json` 자가학습 시드)
- `skills/plugin-github-sync/` — 플러그인 수정 시 GitHub·마켓플레이스 자동 반영
- `memory/` — CS 답변 원칙·템플릿·뉴트리정 성분 레퍼런스 등 지식 베이스

## 설치 (직원용)
1. Cowork 플러그인 마켓플레이스에 다음 마켓플레이스를 추가:
   `https://github.com/EitherCompany/cs-auto-answer-plugin`
2. 목록에서 `cs-auto-answer-plugin` 설치
3. 사방넷(sbadmin03.sabangnet.co.kr)에 회사 계정(`eithercompany`)으로 **직접 로그인**
   (브라우저 비밀번호 저장 권장). 비밀번호는 플러그인에 포함되지 않습니다.

## 사용
채팅에 "CS 수집", "CS 답변", "문의 답변해줘" 등을 입력하면 스킬이 트리거됩니다.

## 보안
- 사방넷 비밀번호는 레포에 저장하지 않습니다. 운영자가 직접 로그인합니다.
- GitHub PAT 등 비밀은 커밋·로그에 노출하지 않습니다.
