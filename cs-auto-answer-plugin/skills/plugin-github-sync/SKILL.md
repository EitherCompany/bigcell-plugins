---
name: plugin-github-sync
description: >
  `cs-auto-answer-plugin` 을 수정했을 때 공유 마켓플레이스 레포(EitherCompany/bigcell-plugins)의
  `cs-auto-answer-plugin/` 하위 폴더로 자동 푸시 + 루트 marketplace.json 동기화 + 릴리스 태그까지 수행한다.
  PAT 는 워크스페이스 .env 우선, 누락 시 노션 "👮 이창근" 페이지에서 조회 (토큰 하드코딩 절대 금지).
  반드시 이 스킬을 사용해야 하는 경우: "CS 플러그인 수정/업데이트", "스킬 수정해줘", "SKILL.md 고쳐",
  "재패키징", "배포", "버전 올려", "마켓플레이스 업데이트", "GitHub 푸시", "플러그인 재배포" 등.
---

# cs-auto-answer-plugin GitHub 동기화 (공유 마켓플레이스 방식 · v1.0.0)

## 고정 상수
- 마켓플레이스 레포: `EitherCompany/bigcell-plugins` (Private, 기본 브랜치 main)
- 이 플러그인 위치: 레포 내 `cs-auto-answer-plugin/` 하위 폴더
- PAT: 워크스페이스 `.env` 의 `GITHUB_PAT` 우선, 없으면 노션 페이지
  `1d8d9e75-0367-80b3-9f32-e82210a58e20` 에서 `github_pat_...` 정규식 추출

## 2 곳 version 동기 bump 필수
- 루트 `.claude-plugin/marketplace.json` 의 `plugins[]` 중 cs-auto-answer-plugin 항목의 `version`
- `cs-auto-answer-plugin/.claude-plugin/plugin.json` 의 `version`
- (새 플러그인/정책 추가 시 루트 marketplace.json 최상위 `version` 도 minor bump)

## 절차
1. PAT 확보 (.env → 노션 fallback)
2. semver 결정: patch=문구·픽스 / minor=새 정책·스킬 / major=구조변경
3. version bump (위 2~3곳)
4. `git clone --depth 1 https://x-access-token:${TOKEN}@github.com/EitherCompany/bigcell-plugins.git "$TMP"`
5. `rsync -av --delete --exclude='.git' "$SRC/" "$TMP/cs-auto-answer-plugin/"` (이 플러그인 폴더만 갱신)
6. 루트 `$TMP/.claude-plugin/marketplace.json` 의 cs-auto-answer-plugin 항목 version 갱신
7. Secret 검사: `grep -rEn 'github_pat_[A-Za-z0-9_]{50,}|dlejzja|password\s*[:=]' "$TMP" --exclude-dir=.git` → 있으면 중단
8. 커밋·태그·푸시: `git commit -m "cs vN.M.K: 요약"`, `git push origin main`,
   `git tag -a cs-vN.M.K`, `git push origin cs-vN.M.K`
9. 릴리스(선택): `POST /repos/EitherCompany/bigcell-plugins/releases`
10. 정리: `rm -rf "$TMP"` (토큰 잔존 방지)

## 금지 사항
1. GitHub 웹 UI 자동화 편집 금지
2. PAT·사방넷 비밀번호를 플러그인·커밋·로그에 노출 금지
3. 개별 플러그인 이름(cs-auto-answer-plugin) 변경 금지 — 마켓플레이스 업데이트 경로 끊김
4. 레포 Public 전환 금지 (Private 유지)
5. `.git` 폴더 잔존 push 금지
