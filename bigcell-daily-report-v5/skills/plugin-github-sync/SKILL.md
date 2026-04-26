---
name: plugin-github-sync
description: 창근님 `bigcell-daily-report-v5` 플러그인을 수정했을 때 GitHub 레포(EitherCompany/bigcell-plugins)로 자동 패키징·푸시·릴리스 태그까지 수행한다. PAT는 워크스페이스 `.env` 우선 → 없으면 노션 "👮 이창근" 페이지 fallback. 반드시 이 스킬을 사용해야 하는 경우는 "빅셀 플러그인 수정", "빅셀 플러그인 업데이트", "빅셀 스킬 수정", "SKILL.md 고쳐", "재패키징", "배포", "버전 올려", "마켓플레이스 업데이트", "GitHub 푸시", "플러그인 재배포", "v5.x.x 올려줘" 등 빅셀 플러그인 편집 후 GitHub·마켓플레이스 반영과 관련된 모든 요청. 사용자가 "빅셀 플러그인" + "수정/업데이트/편집/배포/올려" 키워드를 조합하면 이 스킬을 사용할 것. 트리거는 각 PC 어디서나 동일.
---

# 빅셀 플러그인 GitHub 자동 동기화 스킬 (plugin-github-sync · v0.1.0)

창근님 `bigcell-daily-report-v5` 플러그인의 어떤 파일이든 편집됐을 때 **같은 세션 안에서 GitHub 레포까지 자동 패키징 + 푸시 + 릴리스 태그**까지 완결한다.

---

## ⭐ 자동 트리거 조건 (v0.1.0 · 절대 원칙)

플러그인 내 다음 중 하나라도 변경되면 **별도 지시 없이 이 절차 착수**:

- `claude-plugin-def/plugin.json` 편집 (소스에서는 `claude-plugin-def`, 패키징/리모트에서는 `.claude-plugin` 으로 복원됨)
- `skills/*/SKILL.md` 편집 또는 신규 스킬 추가
- `skills/*/scripts/*.py` 편집
- `skills/*/reference_*.md` 편집
- `README.md` · `SETUP.md` · `LICENSE` 편집
- 새 스킬 폴더 추가·기존 스킬 폴더 삭제
- `cowork-plugin-management:cowork-plugin-customizer` 스킬 호출 후 플러그인 수정

**Why**: "앞으로 항상 플러그인 최신화하면 너가 알아서 깃헙에도 최신화해" (창근, 2026-04-23, 창근 투자 플러그인 정책 동일 적용). 로컬 리빌드로 끝내지 말고 타 PC 반영을 위해 무조건 레포 푸시까지 완결해야 한다.

**타 PC 지원**: 이 스킬이 플러그인에 내장돼 있어 어느 PC 의 Claude/Cowork 든 빅셀 플러그인 편집 시 동일하게 자동 푸시 가능. 워크스페이스 폴더(`/sessions/<세션>/mnt/빅셀/`)는 OneDrive/구글드라이브로 모든 PC 동기화되므로 `.env` 도 함께 따라옴.

---

## 🔑 고정 상수

- **레포**: `EitherCompany/bigcell-plugins` (Private, 무기한 유지)
- **레포 URL**: https://github.com/EitherCompany/bigcell-plugins
- **플러그인 폴더명 (레포 내)**: `bigcell-daily-report-v5/`
- **로컬 소스 위치**: 워크스페이스 `빅셀/.plugin_source/bigcell-daily-report-v5/`
- **PAT 저장 위치 (우선순위)**:
  1. **워크스페이스 `.env`**: `빅셀/.env` 의 `GH_TOKEN=github_pat_...` 라인 (1순위)
  2. **노션 "👮 이창근" 페이지** fallback: pageId `1d8d9e75-0367-80b3-9f32-e82210a58e20` 본문에서 `github_pat_...` 정규표현식 추출 (`.env` 누락 시)
- **PAT 범위**: EitherCompany org · repo · Fine-grained · 무기한
- **기본 브랜치**: `main`
- **메타 폴더 이름 비대칭** (절대 잊지 말 것):
  - 소스: `claude-plugin-def/` (Cowork 자동 감지 회피용 — 점 시작 폴더면 Cowork 가 "플러그인 저장하시겠습니까" 팝업을 띄움)
  - .plugin zip 내부 + GitHub 리모트: `.claude-plugin/` (표준)
  - `rebuild_plugin.sh` 가 staging 단계에서 자동 변환

**⚠️ PAT 는 이 플러그인 SKILL.md/README/스크립트에 절대 하드코딩 금지** — secret scanning 이 push 자체를 차단. 항상 `.env` 또는 노션 런타임 조회로 주입.

---

## 📂 레포 구조 (2026-04-26 기준)

```
EitherCompany/bigcell-plugins/
├── .claude-plugin/marketplace.json          ← 루트. version bump 필수 (마켓플레이스 알림 트리거)
├── README.md
└── bigcell-daily-report-v5/                 ← 실제 플러그인 폴더
    ├── .claude-plugin/plugin.json           ← version bump 필수
    ├── README.md
    └── skills/
        ├── bigcell-daily-report/
        │   ├── SKILL.md
        │   └── scripts/
        │       ├── integrated_bigcell.py
        │       ├── rebuild_report.py
        │       ├── build_v3_report.py
        │       ├── build_special_context.py
        │       ├── inject_special_section.py
        │       └── capture_screenshots.py (legacy)
        └── plugin-github-sync/              ← 이 스킬 (v5.2.0+)
            └── SKILL.md
```

**⚠️ 두 version 필드 모두 bump 필수** (`marketplace.json` · `plugin.json`) — `rebuild_plugin.sh` 가 marketplace.json 은 자동 bump 해주지만, **`plugin.json` 은 사람이 직접 bump 해야 함** (이 스킬이 그 역할 자동화).

---

## 🧭 자동 실행 절차 (10단계)

### Step 1 — PAT 조회

```bash
# 1순위: 워크스페이스 .env
ENV=/sessions/<세션>/mnt/빅셀/.env
TOKEN=$(grep -oE '^GH_TOKEN=github_pat_[A-Za-z0-9_]+' "$ENV" | cut -d= -f2)
```

비어 있으면 2순위 — 노션 조회:
```
notion-fetch(id: "1d8d9e75-0367-80b3-9f32-e82210a58e20")
```
응답 본문에서 `github_pat_...` 추출. 발견 안 되면 그때만 창근님께 한 줄로 요청: "GitHub 동기화 시작, PAT 요청드립니다".

### Step 2 — 변경본 확인 + 커밋 메시지 준비

편집한 파일 목록을 확인하고 커밋 메시지에 반영할 요약 준비:
- 어떤 파일이 바뀌었는지 (skills 추가? scripts 수정? SKILL.md 정책 변경?)
- 버전 bump 종류 결정 (semver)
- Why (창근 직접 피드백이 있으면 인용)

### Step 3 — `plugin.json` version bump (필수)

소스 파일: `빅셀/.plugin_source/bigcell-daily-report-v5/claude-plugin-def/plugin.json`

```python
import json
p = json.load(open(PJ))
# semver bump
p['version'] = '<NEW>'
json.dump(p, open(PJ,'w'), ensure_ascii=False, indent=2)
```

버전 규칙 (semver):
- **patch (5.x.N)**: 문구 수정, 버그 픽스, 오타 교정
- **minor (5.X.0)**: 새 정책·스킬·기능 추가 (호환 유지)
- **major (X.0.0)**: 구조 변경, breaking change

> `marketplace.json` 의 mp-level version 은 `rebuild_plugin.sh` 가 자동 patch bump (변경 감지 시).

### Step 4 — Secret 검사 (push 전 필수)

`rebuild_plugin.sh` 가 push 직전에 자동으로 수행. 정확한 fine-grained PAT 패턴만 매치 (`github_pat_` + 영숫자 50자 이상) — 문서/예시의 `github_pat_...` placeholder 는 통과:

```bash
grep -rEn 'github_pat_[A-Za-z0-9_]{50,}' /sessions/<세션>/mnt/빅셀/.plugin_source/ \
  --exclude-dir=.git --exclude-dir=__pycache__ 2>/dev/null
```

매치가 1건이라도 있으면 **푸시 중단 → 창근님께 알림**. `.env` 는 위 경로 밖에 있어 자연 제외.

### Step 5 — `rebuild_plugin.sh` 실행 (재패키징 + 1차 push)

```bash
cd /sessions/<세션>/mnt/빅셀/.plugin_source
bash rebuild_plugin.sh
```

스크립트가 자동으로:
1. `claude-plugin-def` → `.claude-plugin` 복원 후 `.plugin` zip 재패키징 (워크스페이스 루트에 저장)
2. `EitherCompany/bigcell-plugins` clone (depth 1)
3. 플러그인 폴더 + 리모트 marketplace.json 동기화 (변경 감지 시 mp version 자동 patch bump)
4. `git diff --cached` 검사 — 차이 있으면 commit + push, 없으면 스킵 (idempotent)
5. 작업 디렉토리 `/tmp/.push_*` 자동 정리

### Step 6 — 커밋 SHA 회수

```bash
TOKEN=...  # Step 1 의 PAT
TMPREPO="/tmp/.verify_$$"
git clone --depth 1 "https://x-access-token:${TOKEN}@github.com/EitherCompany/bigcell-plugins.git" "$TMPREPO" 2>/dev/null
SHA=$(cd "$TMPREPO" && git rev-parse HEAD)
SHORT=$(echo "$SHA" | cut -c1-7)
echo "commit: $SHORT"
```

(`rebuild_plugin.sh` 출력에서 직접 파싱해도 OK — `✅ GitHub push 완료 — commit XXXXXXX`)

### Step 7 — Git 태그 + 푸시

```bash
cd "$TMPREPO"
VER=$(python3 -c "import json; print(json.load(open('bigcell-daily-report-v5/.claude-plugin/plugin.json'))['version'])")
git tag "v${VER}"
git push -q origin "v${VER}"
```

### Step 8 — GitHub 릴리스 생성

```bash
curl -sS -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer ${TOKEN}" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  https://api.github.com/repos/EitherCompany/bigcell-plugins/releases \
  -d "{
    \"tag_name\":\"v${VER}\",
    \"name\":\"v${VER} — <한 줄 요약>\",
    \"body\":\"## 하이라이트\n\n- 변경 1\n- 변경 2\n\n## Why\n\n<창근 피드백 인용 또는 의도>\n\n## 설치·업데이트\n\n\`/plugin update bigcell-daily-report-v5@EitherCompany\`\",
    \"draft\":false,
    \"prerelease\":false
  }"
```

### Step 9 — 정리

```bash
rm -rf "$TMPREPO"  # PAT 잔존 방지
```

### Step 10 — 보고

창근님에게 한 줄 요약 전달:
- 커밋 URL: `https://github.com/EitherCompany/bigcell-plugins/commit/<sha>`
- 릴리스 URL: `https://github.com/EitherCompany/bigcell-plugins/releases/tag/v<N>.<M>.<K>`
- 변경 요약 (3-5줄)
- 타 PC 반영 명령: `/plugin update bigcell-daily-report-v5@EitherCompany`

---

## 🚫 금지 사항

1. **GitHub 웹 UI 자동화 편집 금지** — 검증된 차단 케이스 다수. `git push` + Release API 경로만 허용
2. **PAT 를 플러그인·커밋·로그·스크린샷에 노출 금지** — `.env`/노션에서만 조회, 사용 후 bash 변수 폐기. SKILL.md/스크립트에 하드코딩하지 말 것
3. **한 version 필드만 bump 금지** — `plugin.json` 은 이 스킬이, `marketplace.json` 은 `rebuild_plugin.sh` 가 동기 bump. 둘 중 하나만 올라가면 마켓플레이스 알림이 안 뜸
4. **소스 메타 폴더 이름 변경 금지** — 소스는 무조건 `claude-plugin-def`, 리모트는 무조건 `.claude-plugin`. 이 비대칭이 Cowork 자동 감지 회피의 핵심
5. **PAT revoke 잔소리 금지** — 창근 명시: "어차피 직원들한테만 공유할거고 뭐하러 revoke해?" → 1회만 간단히 언급하거나 생략
6. **노션/`.env` 둘 다 실패 시 추측 금지** — "혹시 새 PAT 있으시면 알려주세요" 한 줄로 요청

---

## 💡 타 PC 초기 설치 대응

신규 PC 에서 이 플러그인을 처음 설치한다면:

1. 창근님이 Cowork → 플러그인 마켓플레이스 → `EitherCompany/bigcell-plugins` 추가
2. `/plugin install bigcell-daily-report-v5@EitherCompany`
3. 워크스페이스 폴더(`빅셀/`)는 클라우드 동기화로 자동 도달 — `.env`(GH_TOKEN, GH_REPO) + `.plugin_source/` 모두 따라옴
4. 이후 이 스킬이 자동으로 사용 가능 — 해당 PC 에서도 플러그인 편집 시 동일하게 자동 푸시 동작

**주의**: `.env` 가 아직 도달 안 한 신규 PC 라면 Step 1 fallback (노션 PAT 조회) 으로 보완. Notion MCP 미연결 시 창근님께 한 줄로 PAT 요청.

---

## 📜 버전 히스토리

- **v0.1.0** (2026-04-26) — 신규 스킬 신설. PAT `.env` 우선 + 노션 fallback. `rebuild_plugin.sh` 활용 + tag/Release 단계 추가. 빅셀 플러그인 v5.2.0 과 함께 배포. 창근 투자 플러그인 `plugin-github-sync` 스킬 패턴 차용 (트리거/금지사항 동일).

---

## 🏁 완료 기준

- [ ] PAT 자동 조회 완료 (`.env` 또는 노션)
- [ ] `plugin.json` version bump (`marketplace.json` 은 `rebuild_plugin.sh` 가 처리)
- [ ] Secret 검사 통과 (소스 트리에 `.env` 외 `github_pat_` 매치 0)
- [ ] `rebuild_plugin.sh` 실행 성공 → commit + push 완료
- [ ] `git tag v<N>.<M>.<K>` + `git push origin v<N>.<M>.<K>` 성공
- [ ] GitHub 릴리스 생성 성공
- [ ] 임시 디렉토리 정리 (`rm -rf /tmp/.verify_*`, `/t