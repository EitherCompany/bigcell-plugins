"""
빅셀 특이사항 섹션 HTML 조립 + v3 보고서 삽입.

입력:
  --context       build_special_context.py가 만든 JSON (숫자/상품 데이터)
  --interpretation Claude가 작성한 해석 문장들 JSON (구조는 아래 INTERPRETATION_SCHEMA 참조)
  --report        삽입 대상 v3 HTML 보고서 경로 (in-place 수정)

동작:
  - context의 숫자 기반 테이블(한눈 요약 + 계정별 변동 표)을 자동 조립
  - interpretation의 해석 문장을 주입 (한눈 요약 마지막 해석, 계정별 '주요 사유', 상품 bullet)
  - 최종 HTML 블록을 보고서의 </body> 직전에 삽입

interpretation JSON 스키마:
{
  "summary_interpretation": "문장 (한눈 요약의 해석 부분)",
  "account_reasons": {
    "전체 합산": "...",
    "뉴트리정": "...",
    "이더컴퍼니": "...",
    "클린인테크": "...",
    "마인플로": "...",
    "이든코퍼레이션": "..."
  },
  "product_bullets": [
    "<b>상품명 — 이슈</b>: 설명",
    ...
  ],
  "weekly_interpretation": "지난주 동일요일 대비 해석 (optional)"
}
"""
import json
import argparse
import os
import re


def won(n):
    """정수를 ₩12,345 형식으로."""
    if n < 0:
        return f"-₩{abs(n):,}"
    return f"₩{n:,}"


def change_cell(delta, pct=None, bg=''):
    """변동 셀 HTML. +/-에 따라 색상 + 컬럼 그룹 배경색."""
    color = '#27ae60' if delta > 0 else ('#e74c3c' if delta < 0 else '#7f8c8d')
    sign = '+' if delta > 0 else ('' if delta == 0 else '')
    pct_str = f" ({pct:+.1f}%)" if pct is not None else ''
    bg_style = f'background:{bg};' if bg else ''
    return f'<td style="padding:8px;text-align:center;color:{color};border:1px solid #e0e0e0;{bg_style}"><b>{sign}{won(delta)}</b>{pct_str}</td>'


def value_cell(value, bold=False, bg=''):
    """일반 숫자 셀 (가운데 정렬)."""
    bg_style = f'background:{bg};' if bg else ''
    inner = f'<b>{won(value)}</b>' if bold else won(value)
    return f'<td style="padding:8px;text-align:center;border:1px solid #e0e0e0;{bg_style}">{inner}</td>'


def to_bullets(value):
    """해석 값을 번호 리스트 아이템으로. list면 그대로, string이면 소수점 보호 split."""
    if value is None:
        return []
    if isinstance(value, list):
        return [s for s in (str(x).strip() for x in value) if s]
    text = str(value).strip().replace('。', '.')
    if not text:
        return []
    # 소수점(앞뒤가 숫자인 .)은 보호
    parts = re.split(r'(?<!\d)\.(?!\d)', text)
    return [p.strip() for p in parts if p and p.strip()]


def format_weekday(date_str):
    """2026-04-19 → '04/19 일'"""
    from datetime import datetime
    days = ['월', '화', '수', '목', '금', '토', '일']
    dt = datetime.strptime(date_str, '%Y-%m-%d')
    return f"{dt.month:02d}/{dt.day:02d} {days[dt.weekday()]}"


def build_html(context, interp):
    """특이사항 섹션 HTML 블록 생성."""
    td = context['target_date']
    pd = context['prev_date']
    lw = context.get('last_week_date')
    total = context['total']

    # 한눈 요약 — 전일 대비
    s_delta = total['change']['sales']
    np_delta = total['change']['netProfit']
    s_color = '#27ae60' if s_delta > 0 else '#e74c3c'
    np_color = '#27ae60' if np_delta > 0 else '#e74c3c'

    # 지난주 대비
    week_change = total.get('change_week')
    has_week = week_change is not None
    wk_s_delta = week_change['sales'] if has_week else 0
    wk_np_delta = week_change['netProfit'] if has_week else 0
    wk_s_color = '#27ae60' if wk_s_delta > 0 else '#e74c3c'
    wk_np_color = '#27ae60' if wk_np_delta > 0 else '#e74c3c'

    # 해석 bullet — list 구조 우선, 없으면 string에서 소수점 보호 split
    daily_bullets = to_bullets(interp.get('summary_bullets') or interp.get('summary_interpretation'))
    weekly_bullets = to_bullets(interp.get('weekly_bullets') or interp.get('weekly_interpretation'))

    # 전일 대비 수치 아이템
    s_pct = total['change'].get('sales_pct')
    np_pct = total['change'].get('netProfit_pct')
    s_pct_str = f", {s_pct:+.1f}%" if s_pct is not None else ''
    np_pct_str = f", {np_pct:+.1f}%" if np_pct is not None else ''

    daily_items_html = f'''
                <li>매출: {won(total['prev']['sales'])} → <b>{won(total['target']['sales'])}</b> <span style="color:{s_color}">({'+' if s_delta>=0 else ''}{won(s_delta)}{s_pct_str})</span></li>
                <li>순이익: {won(total['prev']['netProfit'])} → <b>{won(total['target']['netProfit'])}</b> <span style="color:{np_color}">({'+' if np_delta>=0 else ''}{won(np_delta)}{np_pct_str})</span></li>'''
    for b in daily_bullets:
        daily_items_html += f'\n                <li>{b}</li>'

    # 지난주 대비 블록
    week_summary_html = ''
    if has_week:
        wk_s_pct = week_change.get('sales_pct')
        wk_np_pct = week_change.get('netProfit_pct')
        wk_s_pct_str = f", {wk_s_pct:+.1f}%" if wk_s_pct is not None else ''
        wk_np_pct_str = f", {wk_np_pct:+.1f}%" if wk_np_pct is not None else ''
        weekly_items_html = f'''
                <li>매출: {won(total['last_week']['sales'])} → <b>{won(total['target']['sales'])}</b> <span style="color:{wk_s_color}">({'+' if wk_s_delta>=0 else ''}{won(wk_s_delta)}{wk_s_pct_str})</span></li>
                <li>순이익: {won(total['last_week']['netProfit'])} → <b>{won(total['target']['netProfit'])}</b> <span style="color:{wk_np_color}">({'+' if wk_np_delta>=0 else ''}{won(wk_np_delta)}{wk_np_pct_str})</span></li>'''
        for b in weekly_bullets:
            weekly_items_html += f'\n                <li>{b}</li>'

        week_summary_html = f'''
            <div style="background:#fff;border-left:4px solid #8e44ad;padding:14px 18px;margin-bottom:18px;border-radius:6px">
                <strong style="font-size:1.05em;color:#8e44ad">📅 지난주 동일요일 대비 ({format_weekday(lw)} → {format_weekday(td)})</strong>
                <ol style="margin:10px 0 0 0;padding-left:24px;color:#444;line-height:1.8">{weekly_items_html}
                </ol>
            </div>'''
    elif lw:
        week_summary_html = f'''
            <div style="background:#f9f9f9;padding:10px 14px;margin-bottom:18px;border-radius:6px">
                <span style="color:#999;font-size:0.9em">📅 지난주 동일요일({lw}) 데이터 미수집 — 다음 실행 시 자동 수집</span>
            </div>'''

    html = f'''<!-- 특이사항 (자동 분석) -->
    <div class="account-section" style="margin-top:30px;border:2px solid #f39c12;background:#fffaf0">
        <div class="account-header" onclick="toggleSection('section_special')" style="background:linear-gradient(135deg,#f39c12 0%,#e67e22 100%);color:white">
            <div class="account-title-row">
                <span class="account-name" style="color:white">📌 특이사항 — 전일/지난주 대비 분석 요약</span>
                <span class="account-toggle" style="color:white">▼</span>
            </div>
        </div>
        <div class="account-body" id="section_special" style="padding:24px;line-height:1.7">

            <div style="background:#fff;border-left:4px solid #e67e22;padding:14px 18px;margin-bottom:18px;border-radius:6px">
                <strong style="font-size:1.05em">🔎 한눈 요약 ({format_weekday(pd)} → {format_weekday(td)})</strong>
                <ol style="margin:10px 0 0 0;padding-left:24px;color:#444;line-height:1.8">{daily_items_html}
                </ol>
            </div>
            {week_summary_html}

            <h3 style="color:#e67e22;border-bottom:2px solid #f39c12;padding-bottom:6px;margin-top:18px">① 계정별 변동 (전일 · 지난주 동일요일 대비)</h3>
            <table style="width:100%;border-collapse:collapse;margin-bottom:8px;font-size:0.93em">
                <thead>
                    <tr style="background:#f8f9fa">
                        <th rowspan="2" style="padding:8px;text-align:center;border:1px solid #e0e0e0;vertical-align:middle">계정</th>
                        <th rowspan="2" style="padding:8px;text-align:center;border:1px solid #e0e0e0;vertical-align:middle">금일 순이익</th>
                        <th colspan="2" style="padding:6px;text-align:center;border:1px solid #e0e0e0;background:#fce6c6;color:#b75b12">전일 대비</th>
                        <th colspan="2" style="padding:6px;text-align:center;border:1px solid #e0e0e0;background:#e1c9ec;color:#5e2a76">지난주 동일요일 대비</th>
                        <th rowspan="2" style="padding:8px;text-align:center;border:1px solid #e0e0e0;vertical-align:middle">주요 사유</th>
                    </tr>
                    <tr>
                        <th style="padding:6px;text-align:center;border:1px solid #e0e0e0;font-weight:500;color:#b75b12;background:#fff3e0">전일 순이익</th>
                        <th style="padding:6px;text-align:center;border:1px solid #e0e0e0;font-weight:500;color:#b75b12;background:#fff3e0">변동</th>
                        <th style="padding:6px;text-align:center;border:1px solid #e0e0e0;font-weight:500;color:#5e2a76;background:#f3e5f5">지난주 순이익</th>
                        <th style="padding:6px;text-align:center;border:1px solid #e0e0e0;font-weight:500;color:#5e2a76;background:#f3e5f5">변동</th>
                    </tr>
                </thead>
                <tbody>
'''

    reasons = interp.get('account_reasons', {})

    # 컬럼 배경색 (얇은 톤)
    BG_PREV = '#fff3e0'   # 전일 대비 열
    BG_WEEK = '#f3e5f5'   # 지난주 대비 열

    # 전체 합산 행
    total_reason = reasons.get('전체 합산', '')
    if total.get('change_week'):
        cw = total['change_week']
        total_lw_cells = value_cell(total['last_week']['netProfit'], bg=BG_WEEK) + '\n                    ' + change_cell(cw['netProfit'], cw['netProfit_pct'], bg=BG_WEEK)
    else:
        total_lw_cells = f'<td colspan="2" style="padding:8px;text-align:center;border:1px solid #e0e0e0;color:#999;background:{BG_WEEK}">N/A</td>'

    html += f'''                <tr style="background:#fef9f3">
                    <td style="padding:8px;text-align:center;border:1px solid #e0e0e0"><b>전체 합산</b></td>
                    {value_cell(total['target']['netProfit'], bold=True)}
                    {value_cell(total['prev']['netProfit'], bg=BG_PREV)}
                    {change_cell(np_delta, total['change']['netProfit_pct'], bg=BG_PREV)}
                    {total_lw_cells}
                    <td style="padding:8px;text-align:left;border:1px solid #e0e0e0">{total_reason}</td>
                </tr>
'''

    # 계정별 행
    for a in context['accounts']:
        name = a['name']
        label = name + ("(전체)" if a['dual'] else "")
        reason = reasons.get(name, '')
        if a.get('change_week'):
            cw = a['change_week']
            lw_cells = value_cell(a['last_week']['netProfit'], bg=BG_WEEK) + '\n                    ' + change_cell(cw['netProfit'], cw['netProfit_pct'], bg=BG_WEEK)
        else:
            lw_cells = f'<td colspan="2" style="padding:8px;text-align:center;border:1px solid #e0e0e0;color:#999;background:{BG_WEEK}">N/A</td>'
        html += f'''                <tr>
                    <td style="padding:8px;text-align:center;border:1px solid #e0e0e0"><b>{label}</b></td>
                    {value_cell(a['target']['netProfit'], bold=True)}
                    {value_cell(a['prev']['netProfit'], bg=BG_PREV)}
                    {change_cell(a['change']['netProfit'], a['change']['netProfit_pct'], bg=BG_PREV)}
                    {lw_cells}
                    <td style="padding:8px;text-align:left;border:1px solid #e0e0e0">{reason}</td>
                </tr>
'''

    html += '''                </tbody>
            </table>

            <h3 style="color:#e67e22;border-bottom:2px solid #f39c12;padding-bottom:6px;margin-top:18px">② 주목할 상품 단위 이슈</h3>
            <ul>
'''

    for bullet in interp.get('product_bullets', []):
        html += f'                <li>{bullet}</li>\n'

    html += '''            </ul>

        </div>
    </div>'''

    return html


def inject(report_path, html_block):
    """보고서의 </body> 직전에 HTML 블록 삽입."""
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 기존 특이사항 섹션이 있으면 제거하고 새로 삽입
    old_start = content.find('<!-- 특이사항 (자동 분석) -->')
    if old_start != -1:
        old_end_marker = '</div>\n    </div>'
        # 섹션 끝 찾기 (마지막 </div>\n    </div>)
        search_start = old_start
        # 간단한 대처: 특이사항 시작부터 다음 빈 줄 or </body> 까지
        body_end = content.find('</body>', old_start)
        content = content[:old_start].rstrip() + '\n' + content[body_end:]

    body_close = content.rfind('</body>')
    if body_close == -1:
        raise RuntimeError("</body> 태그를 찾을 수 없음")

    new_content = content[:body_close] + '\n    ' + html_block + '\n\n' + content[body_close:]

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    return len(html_block)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--context', required=True, help='special_context JSON 경로')
    parser.add_argument('--interpretation', required=True, help='Claude 해석 JSON 경로')
    parser.add_argument('--report', required=True, help='v3 HTML 보고서 경로 (in-place 수정)')
    args = parser.parse_args()

    with open(args.context, encoding='utf-8') as f:
        context = json.load(f)
    with open(args.interpretation, encoding='utf-8') as f:
        interp = json.load(f)

    html = build_html(context, interp)
    size = inject(args.report, html)

    print(f"✅ 특이사항 섹션 삽입 완료")
    print(f"   HTML 블록 크기: {size:,} bytes")
    print(f"   보고서: {args.report}")


if __name__ == '__main__':
    main()
