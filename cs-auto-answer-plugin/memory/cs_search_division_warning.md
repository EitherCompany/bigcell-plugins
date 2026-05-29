---
name: 사방넷 신규접수 검색 시 division=001만으로 부족 (반드시 전체 검색)
description: 신규 미답변 문의 조회 시 division=001 단독 검색하면 누락 발생. 전체(000)로 검색 후 answText 비어있는 것 필터해야 함
type: feedback
originSessionId: a64194ba-bda6-4c38-a999-02b2ebdc8643
---
**규칙: 신규 미답변 CS 조회 시 `division=001`(신규접수)로만 검색하면 일부가 빠진다. 반드시 `division=000`(전체) + `answText` 비어있는 행 필터 방식으로 조회할 것.**

**Why:** 2026-05-07 사용자가 "쿠팡 nutrijung/eithercompany 어제 2개씩 들어왔는데 왜 덜 갱신됐냐" 지적. 확인 결과 division=001 필터로는 검색되지 않는 미답변 건들이 있었음 (3건 누락). division=000으로 다시 검색하고 answText가 빈 것을 필터하니 누락된 건들이 모두 나옴.

**How to apply:**

1. **신규 미답변 조회 시 표준 방식:**
   ```javascript
   comp.$data.sbForm.division = '000';  // 전체
   comp.$data.sbForm.sDate = '날짜시작';
   comp.$data.sbForm.eDate = '날짜끝';
   // 검색 후 tableData에서 answText 비어있는 것 필터
   const pending = td.filter(t => 
     t.askPrtclSrno && 
     (!t.answText || t.answText.length < 5)
   );
   ```

2. **division=001 단독 사용 금지:**
   - division 값이 null이거나 다른 값으로 분류된 미답변 건이 있을 수 있음
   - 쇼핑몰 자동수집 시 division 분류 로직이 일관되지 않을 가능성

3. **수집 페이지 (ask-collect) 기간 설정:**
   - sbForm.startDate, endDate 형식: `'YYYYMMDD'` (예: `'20260507'`)
   - 기본값은 보통 최근 3일이라 누락 가능. 7~14일로 확장 권장

4. **수집 후 답변 페이지 검증 필수:**
   - 수집 완료 후 답변 페이지에서 division=000으로 다시 조회
   - 진짜 미답변(`answText` 빈 것) 카운트로 사용자에게 보고

**적용 예시 (실패→성공):**
- ❌ division=001 → 7건 조회 (누락 3건)
- ✅ division=000 + answText 빈 것 필터 → 10건 조회 (정확)
